import os
import sys
import datetime
import calendar
import warnings

from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import pyodbc

# 忽略 pandas 对 DBAPI2 对象的警告
warnings.filterwarnings('ignore', category=UserWarning)

# 解决 PyInstaller 打包后的模板路径问题
if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=template_folder)
else:
    app = Flask(__name__)

# 数据库连接函数
def get_db_connection():
    mdb_file = r'\\192.168.0.118\金恒晟共享文档\ZKTIMEACCESS\test.MDB'
    conn_str = (
        rf'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};'
        rf'DBQ={mdb_file};'
    )
    return pyodbc.connect(conn_str)

# 生成考勤 Excel 文件的函数
def generate_attendance_excel(query_date):
    """
    生成考勤Excel文件的函数
    
    参数:
    query_date (str): 查询月份，格式为 'YYYY-MM'，例如 '2025-03'
    
    返回:
    str or None: 如果成功，返回生成的Excel文件路径；如果失败，返回None
    """
    try:
        start_date = datetime.datetime.strptime(query_date + '-01', '%Y-%m-%d').date()
    except ValueError:
        return None

    _, last_day = calendar.monthrange(start_date.year, start_date.month)
    end_date = start_date.replace(day=last_day)
    
    # 格式化日期确保覆盖整天
    start_date_str = start_date.strftime('%Y-%m-%d 00:00:00')

    # 查询范围延伸到次月1号09:00，覆盖夜班下班打卡
    if end_date.month == 12:
        next_month_first = end_date.replace(year=end_date.year + 1, month=1, day=1)
    else:
        next_month_first = end_date.replace(month=end_date.month + 1, day=1)
    end_date_str = next_month_first.strftime('%Y-%m-%d 09:00:00')

    try:
        conn = get_db_connection()
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

    try:
        # 使用参数化查询防止 SQL 注入
        sql = """
        SELECT 
            c.CHECKTIME AS 时间,
            U.[Name] AS 姓名,
            c.SENSORID AS 机器号,
            D.DEPTNAME AS 部门名称
        FROM 
            (CHECKINOUT c 
        INNER JOIN 
            USERINFO U ON c.USERID = U.USERID)
        INNER JOIN
            DEPARTMENTS D ON U.DEFAULTDEPTID = D.DEPTID
        WHERE 
            c.CHECKTIME >= ? AND c.CHECKTIME <= ?
            AND (c.SENSORID = '1' OR c.SENSORID = '11')
        """
        
        df = pd.read_sql(sql, conn, params=[start_date_str, end_date_str])
        # 过滤同一人同一机器号在5分钟内的重复打卡，只保留第一次
        df.sort_values(['姓名', '机器号', '时间'], inplace=True)
        df['prev_time'] = df.groupby(['姓名', '机器号'])['时间'].shift()
        df = df[(df['prev_time'].isna()) | ((df['时间'] - df['prev_time']).dt.total_seconds() > 5 * 60)]
        df.drop(columns=['prev_time'], inplace=True)
    except Exception as e:
        print(f"查询数据失败: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()  # 确保连接被关闭释放资源

    if df.empty:
        return None

    base_dir = os.path.dirname(os.path.abspath(__file__))
    # 创建 excel 子目录和日期子文件夹，确保存在
    excel_dir = os.path.join(base_dir, 'excel', query_date)
    os.makedirs(excel_dir, exist_ok=True)

    # 将时间拆分为日期和时间，仅保留必要列
    df['考勤日期'] = df['时间'].dt.date
    df['考勤时间'] = df['时间'].dt.strftime('%H:%M')

    # --------- 1. 保存原始打卡数据（保留所有列） ---------
    raw_path = os.path.join(excel_dir, f"{query_date}_attendance_raw.xlsx")
    df_raw = df[['姓名', '时间', '机器号', '部门名称']]
    # 为了保留原始时间列，重新读取一次含时间的 DataFrame
    # 这里使用原始 df（包括 '时间' 列）
    df_raw = df.assign(考勤日期=df['考勤日期'], 考勤时间=df['考勤时间'])
    df_raw = df_raw[['姓名', '时间', '机器号', '部门名称']]
    df_raw.to_excel(raw_path, index=False)

    # --------- 2. 按部门、姓名、考勤日期聚合时间（换行符） ---------
    df = df[['姓名', '考勤日期', '考勤时间', '部门名称']]
    agg = (
        df.groupby(['部门名称', '姓名', '考勤日期'], as_index=False)
          .agg({
              '考勤时间': lambda s: "\n".join(sorted(s.astype(str)))
          })
    )

    # --------- 3. 写入聚合文件（多工作表） ---------
    aggregated_path = os.path.join(excel_dir, f"{query_date}_attendance_aggregated.xlsx")
    pivot_path = os.path.join(excel_dir, f"{query_date}_attendance_by_dept_pivot.xlsx")
    with pd.ExcelWriter(aggregated_path, engine='openpyxl') as agg_writer, pd.ExcelWriter(pivot_path, engine='openpyxl') as pivot_writer:
        for dept, sub_df in agg.groupby('部门名称'):
            sheet_name = dept[:31]  # Excel sheet name max 31 chars
            # Write raw aggregated sheet (no pivot)
            sub_df.drop(columns='部门名称').to_excel(agg_writer, sheet_name=sheet_name, index=False)
            # Create pivot: rows = 姓名, columns = 考勤日期, values = 考勤时间
            pivot_df = sub_df.pivot(index='姓名', columns='考勤日期', values='考勤时间')
            safe_name = sheet_name.replace('?', '').replace('*', '').replace(':', '').replace('/', '').replace('\\', '').replace('[', '').replace(']', '')
            pivot_df.to_excel(pivot_writer, sheet_name=safe_name)

    # --------- 4. 打包为 ZIP ---------
    # 创建日志记录器
    import logging
    logger = logging.getLogger('attendance')
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    zip_path = os.path.join(excel_dir, f"{query_date}_attendance_bundle.zip")
    import zipfile

    # 使用压缩模式并确保所有文件都被写入 zip 包
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
        for file_path in [raw_path, aggregated_path, pivot_path]:
            if os.path.exists(file_path):
                zipf.write(file_path, os.path.basename(file_path))
                logger.info(f"Added {file_path} to zip bundle, size={os.path.getsize(file_path)} bytes")
            else:
                logger.warning(f"File not found, skipping: {file_path}")

    # 确认 zip 文件已创建
    if os.path.exists(zip_path):
        logger.info(f"Zip bundle created at {zip_path}, size={os.path.getsize(zip_path)} bytes")
    else:
        logger.error(f"Failed to create zip bundle at {zip_path}")

    return zip_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['GET'])
def generate_excel():
    query_date = request.args.get('query_date')
    if not query_date:
        return jsonify({'error': '日期格式无效'}), 400
    # 调用生成函数获取文件路径
    file_path = generate_attendance_excel(query_date)
    if not file_path:
        return jsonify({'error': '未查询到数据或日期格式不正确，或数据库连接失败'}), 400
    if os.path.exists(file_path):
        # 返回下载链接而不是直接文件
        download_url = f'/download/{query_date}'
        return jsonify({'download_url': download_url})
    else:
        return jsonify({'error': '生成的文件未找到'}), 500

@app.route('/download/<date>', methods=['GET'])
def download_file(date):
    # 构造 zip 文件路径
    zip_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'excel', date, f"{date}_attendance_bundle.zip")
    if os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True, mimetype='application/zip', download_name=os.path.basename(zip_path))
    else:
        return jsonify({'error': '文件未找到'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

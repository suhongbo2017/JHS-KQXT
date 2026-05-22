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
    end_date_str = end_date.strftime('%Y-%m-%d 23:59:59')

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
    except Exception as e:
        print(f"查询数据失败: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()  # 确保连接被关闭释放资源

    if df.empty:
        return None

    df = df.sort_values(['姓名', '时间'])
    df['考勤日期'] = df['时间'].dt.date
    df['考勤时间'] = df['时间'].dt.time
    df = df[['姓名', '考勤日期', '考勤时间', '部门名称', '机器号']]
    df['时间戳'] = pd.to_datetime(df['考勤日期'].astype('str') + ' ' + df['考勤时间'].astype('str'))

    def filter_record(group):
        result = [group.iloc[0]]
        for i in range(1, len(group)):
            current = group.iloc[i]
            previous = result[-1]
            if current['时间戳'].hour != previous['时间戳'].hour:
                result.append(current)
            else:
                minutes_diff = (current['时间戳'] - previous['时间戳']).total_seconds() / 60
                if minutes_diff > 5:
                    result.append(current)
        return pd.DataFrame(result)

    filter_group = df.groupby(['姓名', '考勤日期'], group_keys=False).apply(filter_record)
    filter_group.drop('时间戳', inplace=True, axis=1)

    output_path = os.path.join(os.getcwd(), f'{query_date}_attendance.xlsx')
    filter_group.to_excel(output_path, index=False)

    return output_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['GET'])
def generate_excel():
    query_date = request.args.get('query_date')
    if not query_date:
        return jsonify({'error': '日期格式无效'}), 400

    file_path = generate_attendance_excel(query_date)
    if not file_path:
        return jsonify({'error': '未查询到数据或日期格式不正确，或数据库连接失败'}), 400

    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

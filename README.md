# 考勤查询系统 (Attendance Query System)

本项目是一个轻量级的考勤数据处理与查询系统。它能够自动读取远程局域网共享的 **ZKTime Access MDB (Microsoft Access)** 数据库，对打卡流水记录进行去重清洗，并导出符合财务与 HR 要求的月度考勤报表 Excel 文件。

项目支持**本地直接运行（开发与测试）**以及**使用 PM2 进行进程守护部署（生产环境）**。

---

## 📂 项目结构

```text
考勤查询 - 副本/               # 项目根目录
├─ app.py                      # Web 服务启动入口（使用 Waitress WSGI 服务器）
├─ web_main.py                 # Flask 应用核心逻辑（数据库查询、清洗、生成报表）
├─ attendance_service.py       # Windows Service 封装（备选部署方式，仅供参考）
├─ service_control.bat         # Windows Service 控制脚本（仅供参考）
├─ ecosystem.config.js         # PM2 部署配置文件
├─ .gitignore                  # Git 忽略配置
├─ README.md                   # 本说明文档
├─ requirements.txt            # Python 依赖清单
├─ templates/
│  └─ index.html               # 前端交互页面（选择月份、生成并下载报表）
├─ excel/                      # 生成的 Excel 报表输出目录（由 .gitignore 排除）
│  ├─ 2026-06/                 # 按月存放
│  └─ ...
└─ .venv/                      # Python 虚拟环境（由 .gitignore 排除）
```

---

## 🛠️ 前置条件

1. **环境依赖**：
   * Windows 操作系统
   * **Python 3.9+**（已安装并加入系统 `PATH`）
   * 局域网内可正常访问考勤机共享数据库：`\\192.168.0.118\金恒晟共享文档\ZKTIMEACCESS\test.MDB`
   * 系统需安装 **Microsoft Access Database Engine** 驱动（以便 `pyodbc` 连接 `.MDB` 数据库）

2. **虚拟环境与依赖安装**：
   项目使用 `.venv` 虚拟环境。如在新机器部署，请执行：
   ```bash
   python -m venv .venv
   .venv\Scripts\activate.bat
   pip install flask waitress pandas pyodbc pywin32 openpyxl
   ```

---

## 🚀 使用方法

### 方法一：本地开发与测试运行

```cmd
.venv\Scripts\python.exe app.py
```
或者激活虚拟环境后：
```cmd
.venv\Scripts\activate.bat
python app.py
```
启动后 Waitress 服务默认监听 `http://0.0.0.0:5000`。

浏览器访问 `http://localhost:5000`，选择月份后点击"生成考勤报表"即可下载。

---

### 方法二：生产环境——使用 **PM2** 进程守护部署（推荐）

目标 Windows Server 上已安装 PM2，只需以下步骤：

#### 1. 修改 `ecosystem.config.js` 中的 Python 解释器路径

打开 `ecosystem.config.js`，将 `interpreter` 改为项目虚拟环境的 Python 绝对路径：

```javascript
module.exports = {
  apps: [
    {
      name: "attendance-app",
      script: "app.py",
      // ↓ 改为服务器上实际的虚拟环境路径
      interpreter: "D:\\VSCODE\\PYTHON3\\考勤查询 - 副本\\.venv\\Scripts\\python.exe",
      watch: false,
      max_restarts: 10,
      env: {
        NODE_ENV: "production",
        PORT: "5000"
      }
    }
  ]
};
```

#### 2. 启动服务

在项目根目录下执行：

```bash
pm2 start ecosystem.config.js
```

#### 3. 常用 PM2 命令

```bash
pm2 list                     # 查看所有进程状态
pm2 logs attendance-app      # 查看实时日志
pm2 restart attendance-app   # 重启（代码更新后）
pm2 stop attendance-app      # 停止
pm2 delete attendance-app    # 删除进程
pm2 save                     # 保存当前进程列表（配合 startup 实现开机自启）
```

> **注意**：`pm2 start` 时需在项目根目录执行，确保相对路径（如数据库连接、模板目录）能正确解析。

---

## 🧩 更新记录

### 2026-07-01：夜班考勤覆盖修复

**问题**：夜班人员（如 6月30日 23:00 上班）会在次月1号早上 8:00 左右打下班卡。原查询范围仅为当月（如 6月1日 ~ 6月30日 23:59:59），导致该记录被遗漏。

**修复**：将查询范围向后延伸至**次月1号 09:00**。修改位于 `web_main.py` 的 `generate_attendance_excel` 函数：

```python
# 改前
end_date_str = end_date.strftime('%Y-%m-%d 23:59:59')

# 改后
if end_date.month == 12:
    next_month_first = end_date.replace(year=end_date.year + 1, month=1, day=1)
else:
    next_month_first = end_date.replace(month=end_date.month + 1, day=1)
end_date_str = next_month_first.strftime('%Y-%m-%d 09:00:00')
```

**效果**：查询 6月考勤时，实际查询范围为 `6月1日 00:00 ~ 7月1日 09:00`。7月1日早上的打卡记录会出现在报表中，由人工识别为前一晚夜班的下班卡，无需额外的标记或日期修正逻辑。

**跨月场景验证**：

| 查询月份 | 扩展后范围 | 是否正常 |
|---------|-----------|---------|
| 2026-06（30天） | ~ 2026-07-01 09:00 | ✅ |
| 2026-02（28天） | ~ 2026-03-01 09:00 | ✅ |
| 2028-02（闰年29天） | ~ 2028-03-01 09:00 | ✅ |
| 2025-12（跨年） | ~ 2026-01-01 09:00 | ✅ |

---

## 🧮 考勤数据清洗逻辑

1. 按 **姓名** 和 **机器号** 分组并按时序排序
2. 去除同一人同一机器号 **5分钟内** 的重复打卡，仅保留第一次

---

## 📦 其他文件说明

- `attendance_service.py` + `service_control.bat`：基于 pywin32 的 Windows Service 封装，备选部署方式，仅供参考。
- `ecosystem.config.js`：PM2 的部署配置文件，需根据部署路径修改 `interpreter`。
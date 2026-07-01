# 考勤查询系统 (Attendance Query System)

本项目是一个轻量级的考勤数据处理与查询系统。它能够自动读取远程局域网共享的 **ZKTime Access MDB (Microsoft Access)** 数据库，对打卡流水记录进行去重和清洗（5 分钟内同一小时去重算法），并导出符合财务与 HR 要求的月度考勤报表 Excel 文件。

项目支持**本地直接运行（开发与测试）**以及**使用 PM2 进行进程守护部署（生产环境）**。

---

## 📂 项目结构

经过清理后，项目保持了最简的核心文件结构：
```text
考勤查询 - 副本/
├─ templates/
│  └─ index.html              # 前端交互页面（支持输入月份生成并下载报表）
├─ app.py                     # Web 服务启动入口（使用高性能 Waitress WSGI 服务器）
├─ web_main.py                # Flask 应用核心逻辑（数据库查询与考勤过滤清洗算法）
├─ attendance_service.py      # **已保留**，但不再用于生产部署（供参考）
├─ service_control.bat        # **已保留**，但不再推荐使用的 Windows Service 批处理脚本
├─ attendance_tool.py         # 新增工具：复制原始考勤文件并生成格式化透视表
├─ ecosystem.config.js        # PM2 部署配置文件（新增）
├─ .gitignore                 # Git 忽略配置文件
└─ README.md                  # 本说明文档
```

---

## 🛠️ 前置条件

1. **环境依赖**：
   * Windows 操作系统（亦可在 WSL/其他 POSIX 环境下运行）。
   * **Python 3.9+**（已安装并加入系统 `PATH`）。
   * 局域网内可正常访问考勤机共享的数据库：`\\\\192.168.0.118\\金恒晟共享文档\\ZKTIMEACCESS\\test.MDB`。
   * 系统需安装 **Microsoft Access Database Engine** 驱动（以便 `pyodbc` 连接 `.MDB` 数据库）。

2. **虚拟环境准备**：
   项目已配置 `.venv` 虚拟环境。如果在其他机器部署，请激活环境并确保安装以下依赖：
   ```bash
   pip install flask waitress pandas pyodbc pywin32 openpyxl
   ```

---

## 🚀 使用方法

### 方法一：本地开发与临时测试运行

如果您仅需要在本地临时启动服务进行查询或开发测试，可以采用此方法：

1. **启动服务**：
   打开命令行，进入项目根目录，运行：
   ```cmd
   .venv\Scripts\python.exe app.py
   ```
   或者激活虚拟环境后运行：
   ```cmd
   .venv\Scripts\activate.bat
   python app.py
   ```
   运行后，控制台会启动 Waitress 服务，默认监听：`http://0.0.0.0:5000`。

2. **前端使用**：
   * 打开浏览器，访问 `http://localhost:5000`。
   * 在页面上的“月份选择”输入框中输入或选择要查询的月份（格式为 `YYYY-MM`，如 `2025-03`）。
   * 点击 **"生成并下载考勤报表"** 按钮。
   * 系统将自动连接数据库并执行清洗，完成后浏览器会自动下载生成的 Excel 报表文件（例如 `2025-03_attendance.xlsx`）。

---

### 方法二：生产环境——使用 **PM2** 进程守护部署（推荐）

在服务器或生产环境部署时，推荐使用 **PM2**（Node.js 生态的进程管理工具）来守护 Python 程序。PM2 能自动重启崩溃的进程、提供日志管理以及简洁的启动/停止指令。

> **前置**：确保服务器已安装 Node.js（>=12）与 npm。

#### 1. 安装 PM2（全局）
```bash
npm install -g pm2
```

#### 2. 使用 **ecosystem.config.js**（推荐）
项目根目录已提供 `ecosystem.config.js` 示例，内容如下（可自行调整 `script` 与 `name`）：
```javascript
module.exports = {
  apps: [
    {
      name: "attendance-app",
      script: "app.py",
      interpreter: "python",
      watch: false,
      env: {
        NODE_ENV: "production"
      }
    }
  ]
};
```

#### 3. 启动服务
```bash
pm2 start ecosystem.config.js
```
- 该命令会启动 **app.py**（Waitress 服务器），并在后台守护进程。
- 进程名称为 `attendance-app`，可通过 `pm2 list` 查看状态。

#### 4. 常用 PM2 操作
```bash
# 查看运行状态
pmmlist
pm2 list

# 查看日志
pmmlog attendance-app
pm2 logs attendance-app

# 重启服务（代码更新后）
pmrestart attendance-app
pm2 restart attendance-app

# 停止服务
pm2 stop attendance-app

# 删除进程记录（彻底移除）
pmdelete attendance-app
pm2 delete attendance-app
```

#### 5. 开机自启（系统重启后自动启动）
```bash
pm2 startup   # 生成系统启动脚本并提示后续执行的 command
pm2 save      # 保存当前进程列表，以便开机时恢复
```
> **注意**：执行 `pm2 startup` 后会输出一行带有 `sudo` 的命令，复制粘贴执行即可完成系统服务注册。

---

## 📊 新增工具：`attendance_tool.py`

### 功能概述
- **复制原始文件**：将 `excel/2026-06_attendance.xlsx` 复制为 `excel/2026-06_attendance_original_download.xlsx`，供前端直接下载未加工的原始数据。
- **生成格式化透视表**：读取原始文件，时间统一为 `HH:MM`（去除秒），并生成一个透视表：
  - 行 = **姓名**
  - 列 = **考勤日期**
  - 单元格 = 当天所有考勤时间，使用换行 `\n` 分隔（如 `07:07\n18:01`）
- **按部门拆分工作表**：在同一 Excel 文件 `excel/2026-06_attendance_formatted.xlsx` 中为每个 **部门名称** 创建独立工作表（工作表名自动截取至 31 字符）。
- **输出文件**：
  - `2026-06_attendance_original_download.xlsx`（原始数据副本）
  - `2026-06_attendance_formatted.xlsx`（已透视、按部门分 sheet）

### 使用方法（服务器端）
1. **确保在项目根目录**（`d:/VSCODE/PYTHON3/考勤查询 - 副本`）下。
2. **运行工具**：
   ```cmd
   .venv\Scripts\python.exe attendance_tool.py
   ```
   - 如未使用虚拟环境，请直接使用系统 `python`：`python attendance_tool.py`。
3. **运行完成后**，控制台会输出两行提示，例如：
   ```
   Original attendance data copied to D:\VSCODE\PYTHON3\考勤查询 - 副本\excel\2026-06_attendance_original_download.xlsx
   Formatted attendance workbook written to D:\VSCODE\PYTHON3\考勤查询 - 副本\excel\2026-06_attendance_formatted.xlsx
   ```
4. **前端下载**：前端页面只需要提供这两个文件的下载链接即可（例如通过 HTTP 静态文件服务或直接返回文件流）。

> **注意**：该工具仅处理本地的 Excel 文件，不涉及网络下载。如果后端需要从远程服务器拉取最新的 6 月份考勤数据，请在运行此工具前自行将最新的 `2026-06_attendance.xlsx` 放置到 `excel/` 目录下。

---

## 🧮 考勤数据清洗逻辑说明

为了减少员工误打卡（短时间内多次重复打卡）对报表统计的干扰，系统在将原始打卡数据导出为 Excel 时，会自动按以下规则进行去重清洗：

1. 将数据按 **姓名** 和 **考勤日期** 进行分组并排序。
2. 保留每日的首次打卡记录。
3. 对于随后的打卡：
   * 如果打卡时间与上一次保留的打卡记录**不在同一个小时**（如 7:27 与 8:01），则**保留**该记录。
   * 如果在**同一个小时内**（如 11:22 与 11:34），且与上一次保留的记录**时间差大于 5 分钟**，则**保留**该记录；如果时间差在 5 分钟内，则**剔除**。

---

## 📦 其他文件说明
- **`attendance_service.py`** 与 **`service_control.bat`** 已保留，仅供参考或在 Windows 环境下手动使用。
- **`ecosystem.config.js`** 为 PM2 的部署配置文件，推荐在生产环境使用。

---

如有任何疑问或需要进一步自定义（例如加入鉴权、定时任务等），请随时告知！祝部署顺利 🚀

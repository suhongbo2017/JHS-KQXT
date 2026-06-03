# 考勤查询系统 – Windows Service 部署指南

本项目提供了 **基于 pywin32 的原生 Windows Service**，让 Flask（使用 Waitress）在 Windows 服务器上实现自动启动、自动重启、统一运维管理。

---

## 目录
- [项目结构](#项目结构)
- [前置条件](#前置条件)
- [一键部署脚本](#一键部署脚本)
- [手动安装 Service](#手动安装-service)
  - [1️⃣ 安装 Python 依赖](#1️⃣-安装-python-依赖)
  - [2️⃣ 注册 Service（install）](#2️⃣-注册-serviceinstall)
  - [3️⃣ 启动 Service（start）](#3️⃣-启动-servicestart)
  - [4️⃣ 停止 Service（stop）](#4️⃣-停止-servicestop)
  - [5️⃣ 删除 Service（remove）](#5️⃣-删除-serviceremove)
- [验证运行状态](#验证运行状态)
- [日志查看](#日志查看)
- [常见问题 & FAQ](#常见问题--faq)

---

## 项目结构
```text
考勤查询
├─ attendance_service.py      # ★ Windows Service 实现（pywin32）
├─ service_control.bat        # ★ 批处理脚本，封装 install/start/stop/remove
├─ app.py                     # 原始入口（仅供 reference）
├─ web_main.py                # Flask 实例定义
├─ templates/                 # 前端页面
├─ requirements.txt           # 依赖清单（请自行维护）
└─ README.md                  # 本文档
```

---

## 前置条件
1. **Windows Server**（或任意 Windows 机器）
2. **管理员权限**的命令提示符 / PowerShell（后续所有 Service 操作均需管理员）
3. **Python 3.9+** 已安装并加入 `PATH`
4. 已下载 **NSSM**（如果你仍需要旧的 `install_service.bat`）——本指南不再依赖它。

---

## 一键部署脚本
项目已提供 `service_control.bat`，只要在管理员窗口运行对应指令即可完成全部操作。示例：

```cmd
cd D:\VSCODE\PYTHON3\考勤查询
service_control.bat install   :: 注册并设为自动启动
service_control.bat start     :: 启动服务
```

后续如需停止或删除，只需分别执行 `service_control.bat stop`、`service_control.bat remove`。

---

## 手动安装 Service（若不想使用批处理）
下面列出每一步的详细命令，便于自定义或集成到 CI/CD 中。

### 1️⃣ 安装 Python 依赖
```cmd
cd D:\VSCODE\PYTHON3\考勤查询
python -m pip install -r requirements.txt
# 必须包含 pywin32、waitress、flask 等```

> `requirements.txt` 示例（确保已有）：
> ```text
> flask
> waitress
> pywin32
> ```

### 2️⃣ 注册 Service（install）
```cmd
python attendance_service.py install
python attendance_service.py setstarttype auto   :: 设置为开机自动启动
```
执行后会在 **服务管理器** 中出现名为 **AttendanceService** 的条目。

### 3️⃣ 启动 Service（start）
```cmd
python attendance_service.py start
```
或等系统重启后自动启动（已设为自动启动）。

### 4️⃣ 停止 Service（stop）
```cmd
python attendance_service.py stop
```

### 5️⃣ 删除 Service（remove）
> 删除前请先 **stop**，否则会提示错误。
```cmd
python attendance_service.py remove
```

---

## 验证运行状态
使用 `sc query` 或 PowerShell `Get-Service` 检查服务状态：

```cmd
sc query AttendanceService
```
期望输出类似：
```
SERVICE_NAME: AttendanceService
        TYPE               : 10  WIN32_OWN_PROCESS
        STATE              : 4  RUNNING
        WIN32_EXIT_CODE    : 0  (0x0)
        SERVICE_EXIT_CODE  : 0  (0x0)
        CHECKPOINT         : 0
        WAIT_HINT          : 0
```

若返回 `STATE: 1  STOPPED` 表示服务未启动，检查日志（见下文）定位原因。

---

## 日志查看
`pywin32` 会把 Service 的输出写入 **Windows 事件日志**，打开 **事件查看器 → Windows 日志 → 应用程序**，筛选来源 `AttendanceService` 即可看到 `Info`、`Error` 信息。

如果想把日志直接写入文件，可在 `attendance_service.py` `run_server` 之前加入如下代码（自行编辑即可）：

```python
import logging, sys
log_path = r"D:\logs\attendance_service.log"
logging.basicConfig(filename=log_path, level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
sys.stdout = open(log_path, "a")
sys.stderr = open(log_path, "a")
```

---

## 常见问题 & FAQ

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| Service 启动后立即停止 | 依赖未安装、`ImportError`、路径错误 | 查看 **事件日志** 中的错误信息，确保 `requirements.txt` 已完整安装；若使用 virtualenv，取消注释 `attendance_service.py` 中的 virtualenv 激活代码并填入正确路径。 |
| 访问 `http://<ip>:5000` 报 502/无法连接 | 防火墙阻止端口 | 在服务器防火墙或安全组打开 **5000** 端口（或在 `attendance_service.py` 中自行改为 80/443）。 |
| 想更改监听端口 | 端口硬编码在 `attendance_service.py` | 修改 `serve(app, host="0.0.0.0", port=5000)` 为所需端口，重新 `service_control.bat restart`（先 stop 再 start）。 |
| Service 未自动启动 | 未设置为 `AUTO_START` | 再次执行 `python attendance_service.py setstarttype auto`，或在 **服务管理器** 手动改为 “自动”。 |
| 想让 Service 以普通用户身份运行 | 默认是 `LocalSystem`，权限可能过大 | 在 **服务属性 → 登录** 中改为指定用户；或在 `service_control.bat` 中使用 `python attendance_service.py setobj username password`（需要自行实现）。 |

---

## 小结
通过 `attendance_service.py` + `service_control.bat`，你可以在 Windows 服务器上**像管理系统服务一样管理** Flask 考勤查询系统，拥有自动启动、统一日志、简洁的启动/停止脚本，极大提升运维效率。

如有更多需求（如添加健康检查、HTTPS 终端、日志轮转等），可在 `attendance_service.py` 基础上继续扩展。祝使用愉快 🚀

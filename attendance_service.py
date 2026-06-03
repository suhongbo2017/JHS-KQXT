import os
import sys
import time
import win32event
import win32service
import win32serviceutil
import servicemanager
from waitress import serve
from web_main import app

class AttendanceService(win32serviceutil.ServiceFramework):
    _svc_name_ = "AttendanceService"
    _svc_display_name_ = "考勤查询系统 Windows Service"
    _svc_description_ = "使用 pywin32 将 Flask/Waitress 应用包装为原生 Windows Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.start_time = time.time()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        servicemanager.LogInfoMsg("AttendanceService 正在停止 …")
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        servicemanager.LogInfoMsg("AttendanceService 正在启动 …")
        # 若使用 virtualenv，可在此处激活（示例）
        # venv_path = r"D:\VSCODE\PYTHON3\考勤查询\.venv\Scripts"
        # os.environ["PATH"] = venv_path + os.pathsep + os.environ["PATH"]
        # os.chdir(r"D:\VSCODE\PYTHON3\考勤查询")

        from threading import Thread

        def run_server():
            serve(app, host="0.0.0.0", port=5000)

        server_thread = Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()

        while True:
            rc = win32event.WaitForSingleObject(self.stop_event, 1000)
            if rc == win32event.WAIT_OBJECT_0:
                servicemanager.LogInfoMsg("AttendanceService 收到停止请求，正在关闭服务器 …")
                break
        servicemanager.LogInfoMsg("AttendanceService 已成功停止。")

if __name__ == "__main__":
    win32serviceutil.HandleCommandLine(AttendanceService)

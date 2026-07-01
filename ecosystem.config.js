module.exports = {
  apps: [
    {
      name: "attendance-app",
      script: "app.py",
      // 使用 uv 管理的 Python 解释器
      // 在 cmd 中执行 uv python list 可查看所有可用版本
      interpreter: "C:\\Users\\Administrator\\AppData\\Roaming\\uv\\python\\cpython-3.11-windows-x86_64-none\\python.exe",
      watch: false,
      max_restarts: 10,
      env: {
        NODE_ENV: "production",
        PORT: "5000"
      }
    }
  ]
};

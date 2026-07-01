module.exports = {
  apps: [
    {
      name: "attendance-app",
      script: "app.py",
      // 如果 Python 已加入系统 PATH，留空即可；否则填绝对路径
      // 例如："C:\Python312\python.exe"
      interpreter: "",
      watch: false,
      max_restarts: 10,
      env: {
        NODE_ENV: "production",
        PORT: "5000"
      }
    }
  ]
};

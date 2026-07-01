module.exports = {
  apps: [
    {
      name: "attendance-app",
      script: "app.py",
      // Python 绝对路径，请根据服务器实际安装位置修改
      // 可在 cmd 中执行 where python 查看路径
      interpreter: "C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
      watch: false,
      max_restarts: 10,
      env: {
        NODE_ENV: "production",
        PORT: "5000"
      }
    }
  ]
};

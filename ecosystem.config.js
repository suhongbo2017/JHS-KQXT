module.exports = {
  apps: [
    {
      name: "attendance-app",
      script: "app.py",
      // Python 解释器路径（根据服务器实际路径修改）
      // 例如："D:/项目路径/.venv/Scripts/python.exe"
      interpreter: "D:/金恒晟共享文档/PC/JHS/JHS-KQXT/.venv/Scripts/python.exe",
      watch: false,
      max_restarts: 10,
      env: {
        NODE_ENV: "production",
        PORT: "5555"
      }
    }
  ]
};

module.exports = {
  apps: [
    {
      name: "attendance-app",
      script: "app.py",
      // Python 解释器路径（使用正斜杠，Windows 也支持）
      // 使用 uv 创建虚拟环境后指向 .venv\Scripts\python.exe
      interpreter: "D:/金恒晟共享文档/PC/JHS/JHS-KQXT/.venv/Scripts/python.exe",
      watch: false,
      max_restarts: 10,
      env: {
        NODE_ENV: "production",
        PORT: "6000"
      }
    }
  ]
};

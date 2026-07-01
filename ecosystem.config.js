module.exports = {
  apps: [
    {
      name: "attendance-app",
      script: "app.py",
      interpreter: "python",
      interpreter_kwargs: {
        // 指向项目虚拟环境的 Python 解释器
      },
      // If you want PM2 to automatically restart on file changes (useful for dev)
      watch: false,
      // Number of times to restart on failure before giving up
      max_restarts: 10,
      // Log files (optional, can be omitted to use default PM2 logs)
      // output: "./logs/out.log",
      // error: "./logs/err.log",
      env: {
        NODE_ENV: "production",
        // You can set any custom env vars here, e.g., PORT
        PORT: "5000"
      }
    }
  ]
};

module.exports = {
  apps: [
    {
      name: "attendance-app",
      script: "app.py",
      interpreter: "python",
      interpreter_kwargs: {
        // Use the virtual environment python if it exists
        // When running on Windows you can point to .venv\Scripts\python.exe
        // Leave empty to use the system python in PATH
        // Example: "c:/VSCODE/PYTHON3/考勤查询 - 副本/.venv/Scripts/python.exe"
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

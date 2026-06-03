module.exports = {
  apps: [
    {
      name: "jhs-attendance",
      script: "app.py",
      interpreter: "./.venv/Scripts/python.exe",
      cwd: __dirname,
      env: {
        PORT: "5000"
      },
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      out_file: "./logs/out.log",
      error_file: "./logs/error.log",
      combine_logs: true,
      max_logs: "5M",
      // keep only important logs (stdout and stderr) and rotate when exceeding 5MB
    }
  ]
};

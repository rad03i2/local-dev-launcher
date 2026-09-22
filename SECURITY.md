# Security Policy

Local Dev Launcher executes commands explicitly listed in a local configuration file. Treat configuration files as executable intent: review them before running. Commands are passed directly to `subprocess.Popen` with `shell=False`; shell command strings are intentionally rejected.

Do not store secrets in `dev-launch.json`; use the host environment or a dedicated secret manager. Logs may contain output produced by child processes, so protect `.dev-logs` appropriately.

For security reports, use GitHub's private vulnerability reporting feature when available. Do not publish credentials or exploit details in a public issue.

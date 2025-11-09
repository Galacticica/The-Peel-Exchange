#!/usr/bin/env bash
set -euo pipefail

cd /app

echo "Cron worker starting..."

# Export all current environment variables to a file that cron can source
# This ensures DB credentials and other secrets are available to cron jobs
printenv | grep -v "no_proxy" > /etc/environment

echo "Registering crontab entries..."
python manage.py crontab add

echo "Starting cron daemon in foreground..."
cron -f

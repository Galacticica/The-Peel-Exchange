#!/usr/bin/env bash
set -euo pipefail

cd /app

echo "Cron worker starting..."
echo "Registering crontab entries..."
python manage.py crontab add

echo "Starting cron daemon in foreground..."
cron -f

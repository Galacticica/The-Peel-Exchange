#!/usr/bin/env bash
set -euo pipefail


export DJANGO_SECRET_KEY="${DJANGO_SECRET_KEY:-devsecretkey}"

cd /app

if command -v python >/dev/null 2>&1; then
	echo "Registering crontab entries (django-crontab)..."
	python manage.py crontab add || true
	echo "Starting cron daemon..."
	cron || true
fi

echo "Starting Vite (npm run dev)..."
npm run dev &
NPM_PID=$!

cleanup() {
	echo "Shutting down..."
	if command -v python >/dev/null 2>&1; then
		python manage.py crontab remove || true
	fi
	kill -TERM "${NPM_PID}" 2>/dev/null || true
	wait ${NPM_PID} 2>/dev/null || true
}

trap 'cleanup; exit' SIGINT SIGTERM
echo "Running database migrations..."
python manage.py migrate --noinput
echo "Starting Django dev server on 0.0.0.0:8000..."

python manage.py runserver 0.0.0.0:8000

wait ${NPM_PID}

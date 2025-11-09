#!/usr/bin/env bash
set -euo pipefail

cd /app

# Use DEBUG env var ("1" for development) to decide dev vs production behavior
DEBUG=${DEBUG:-0}

if [ "$DEBUG" = "1" ]; then
	echo "Development mode: starting vite dev server and Django runserver"
	echo "Registering crontab entries (django-crontab)..."
	python manage.py crontab add || true
	echo "Starting cron daemon..."
	cron || true

	echo "Starting Vite (npm run dev)..."
	npm run dev &
	NPM_PID=$!

	cleanup() {
		echo "Shutting down..."
		python manage.py crontab remove || true
		kill -TERM "${NPM_PID}" 2>/dev/null || true
		wait ${NPM_PID} 2>/dev/null || true
	}

	trap 'cleanup; exit' SIGINT SIGTERM

	echo "Running database migrations..."
	python manage.py migrate --noinput
	echo "Starting Django dev server on 0.0.0.0:8000..."
	python manage.py runserver 0.0.0.0:8000 &

	wait ${NPM_PID}
else
	echo "Production mode: running migrations and collectstatic"
	python manage.py migrate --noinput
	python manage.py collectstatic --noinput || true

	PORT=${PORT:-8000}
	echo "Starting gunicorn on 0.0.0.0:${PORT}"
	# Reduce workers from 3 to 2 to save memory on free tier
	exec gunicorn conf.wsgi:application \
		--bind 0.0.0.0:${PORT} \
		--workers 2 \
		--log-level info \
		--access-logfile - \
		--error-logfile -
fi

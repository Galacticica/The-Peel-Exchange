FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
     && apt-get install -y --no-install-recommends \
         curl ca-certificates gnupg build-essential libpq-dev git cron \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get update \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip

COPY package.json package-lock.json* ./

RUN npm ci --unsafe-perm

RUN pip install --no-cache-dir \
    "django>=5.2.8" \
    "django-browser-reload>=1.21.0" \
    "django-crontab>=0.7.1" \
    "django-vite>=3.1.0" \
    "psycopg2>=2.9.11" \
    "python-dotenv>=1.2.1" \
    "gunicorn>=20.1.0" \
    "whitenoise>=1.4.0"

COPY . .

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

COPY run-cron.sh /usr/local/bin/run-cron.sh
RUN chmod +x /usr/local/bin/run-cron.sh

COPY run-scheduled-job.sh /usr/local/bin/run-scheduled-job.sh
RUN chmod +x /usr/local/bin/run-scheduled-job.sh

# Build frontend assets (vite) at image build time so production image serves static files
# Fail the build if the frontend build fails so we don't produce images missing the manifest.
RUN npm run build 

# Ensure Django settings are available and collect static files into STATIC_ROOT so
# the Vite manifest (static/dist/manifest.json) is copied into STATIC_ROOT/dist/manifest.json
# This makes the manifest available at /app/staticfiles/dist/manifest.json in the container.
ENV DJANGO_SETTINGS_MODULE=conf.settings

# Collect static files after the frontend build so the manifest exists in STATIC_ROOT
RUN python manage.py collectstatic --noinput

EXPOSE 8000 5173

ENV DJANGO_SETTINGS_MODULE=conf.settings

CMD ["/usr/local/bin/docker-entrypoint.sh"]

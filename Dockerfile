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
    "python-dotenv>=1.2.1"

COPY . .

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8000 5173

ENV DJANGO_SETTINGS_MODULE=conf.settings

CMD ["/usr/local/bin/docker-entrypoint.sh"]

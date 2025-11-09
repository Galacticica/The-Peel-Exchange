#!/usr/bin/env bash
# Script to run Django management commands on Fly.io scheduled machines
set -euo pipefail

cd /app

# Run the command passed as argument
python manage.py "$@"

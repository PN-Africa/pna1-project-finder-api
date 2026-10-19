#!/bin/sh
set -e

# ==============================================================================
# Container Entrypoint Script for Project Finder
# ==============================================================================

echo "==> Project Finder Container Initializing..."

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-projectfinder.settings.prod}"

# Check database connection if requested or in production
if [ "${WAIT_FOR_DB:-true}" = "true" ] || [ "${WAIT_FOR_DB:-true}" = "1" ]; then
    echo "==> Verifying database connectivity..."
    python - <<'EOF'
import sys
import time
import django
from django.db import connections
from django.db.utils import OperationalError

django.setup()
conn = connections['default']
retries = 30
while retries > 0:
    try:
        conn.cursor()
        print("==> Database connection successful!")
        sys.exit(0)
    except OperationalError as err:
        retries -= 1
        print(f"==> Database not ready yet ({err}). Retrying in 2 seconds ({retries} retries left)...")
        time.sleep(2)
print("==> ERROR: Timed out waiting for database connectivity.")
sys.exit(1)
EOF
fi

# Run database migrations
if [ "${RUN_MIGRATIONS:-true}" = "true" ] || [ "${RUN_MIGRATIONS:-true}" = "1" ]; then
    echo "==> Running database migrations..."
    python manage.py migrate --noinput
fi

# Re-collect static files if explicitly requested (already baked into image at build time)
if [ "${COLLECT_STATIC:-false}" = "true" ] || [ "${COLLECT_STATIC:-false}" = "1" ]; then
    echo "==> Re-collecting static assets at runtime..."
    python manage.py collectstatic --noinput --clear
fi

echo "==> Starting application server..."
exec "$@"

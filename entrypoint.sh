#!/bin/bash
set -e

# Windows CRLF ni tozalash
if [ -f /app/entrypoint.sh ]; then
    sed -i 's/\r$//' /app/entrypoint.sh 2>/dev/null || true
fi

echo "═══════════════════════════════════════════════════════"
echo "  SoLuna — Starting up"
echo "═══════════════════════════════════════════════════════"

echo ""
echo "Waiting for PostgreSQL..."
python3.11 -c "
import os, time, sys
DB_HOST = os.environ.get('DB_HOST', '')
if not DB_HOST:
    print('DB_HOST not set, skipping')
    sys.exit(0)
try:
    import psycopg2
except ImportError:
    print('psycopg2 not installed, skipping')
    sys.exit(0)
for attempt in range(30):
    try:
        conn = psycopg2.connect(
            dbname=os.environ.get('DB_NAME', 'postgres'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', ''),
            host=DB_HOST,
            port=os.environ.get('DB_PORT', '5432'),
            connect_timeout=3,
        )
        conn.close()
        print('PostgreSQL is ready.')
        sys.exit(0)
    except Exception as e:
        print(f'   Attempt {attempt+1}/30: {str(e)[:80]}')
        time.sleep(2)
print('PostgreSQL not ready after 60s')
sys.exit(1)
"

echo ""
echo "Waiting for Redis..."
python3.11 -c "
import os, time, sys
REDIS_HOST = os.environ.get('REDIS_HOST', '')
if not REDIS_HOST:
    print('REDIS_HOST not set, skipping')
    sys.exit(0)
try:
    import redis
except ImportError:
    print('redis not installed, skipping')
    sys.exit(0)
for attempt in range(15):
    try:
        r = redis.Redis(host=REDIS_HOST, port=int(os.environ.get('REDIS_PORT', 6379)), socket_connect_timeout=2)
        r.ping()
        print('Redis is ready.')
        sys.exit(0)
    except Exception as e:
        print(f'   Attempt {attempt+1}/15: {str(e)[:80]}')
        time.sleep(2)
print('Redis not ready - continuing')
sys.exit(0)
"

echo ""
echo "Running migrations..."
python3.11 manage.py migrate --noinput

echo ""
echo "Compiling translations..."
python3.11 manage.py compilemessages --locale=uz --locale=ru --locale=ko --locale=en 2>/dev/null || echo "   (skipped)"

echo ""
echo "Collecting static files..."
python3.11 manage.py collectstatic --noinput --verbosity 0

if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo ""
    echo "Creating superuser (if not exists)..."
    python3.11 manage.py createsuperuser --noinput 2>/dev/null && echo "   Superuser created" || echo "   (already exists)"
fi

echo ""
echo "═══════════════════════════════════════════════════════"

if [ "$DEBUG" = "False" ] || [ "$DEBUG" = "false" ] || [ "$DEBUG" = "0" ]; then
    if python3.11 -c "import uvicorn" 2>/dev/null; then
        echo "PRODUCTION (uvicorn) on :8008..."
        WORKERS="${WORKERS:-4}"
        exec python3.11 -m uvicorn config.asgi:application --host 0.0.0.0 --port 8008 --workers "$WORKERS" --proxy-headers --forwarded-allow-ips='*'
    elif python3.11 -c "import gunicorn" 2>/dev/null; then
        echo "PRODUCTION (gunicorn) on :8008..."
        WORKERS="${WORKERS:-4}"
        exec python3.11 -m gunicorn config.wsgi:application --bind 0.0.0.0:8008 --workers "$WORKERS" --access-logfile - --error-logfile -
    fi
fi

echo "DEV server on :8008..."
exec python3.11 manage.py runserver 0.0.0.0:8008

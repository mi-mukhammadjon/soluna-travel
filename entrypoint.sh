#!/bin/bash
set -e

echo "⏳ Waiting for PostgreSQL..."
python << 'PYEOF'
import os, time, sys
for attempt in range(30):
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT'],
        )
        conn.close()
        print("✅ PostgreSQL is ready.")
        sys.exit(0)
    except ImportError:
        print("⚠️  psycopg2 not installed, skipping DB wait.")
        sys.exit(0)
    except Exception as e:
        print(f"   Attempt {attempt+1}/30: {e}")
        time.sleep(2)
print("❌ PostgreSQL not ready after 60s")
sys.exit(1)
PYEOF

echo "🔄 Running migrations..."
python manage.py migrate --noinput

echo "🌍 Compiling translations..."
python manage.py compilemessages --locale=uz --locale=ru --locale=ko 2>/dev/null || echo "   (skipped)"

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting server on :8008..."
exec python manage.py runserver 0.0.0.0:8008
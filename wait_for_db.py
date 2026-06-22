"""Database tayyor bo'lguncha kutish skripti."""
import os
import time
import sys


def wait_for_db():
    db_host = os.environ.get('DB_HOST', '')
    if not db_host:
        print("⚠️  DB_HOST not set, skipping (SQLite?)")
        sys.exit(0)

    try:
        import psycopg2
    except ImportError:
        print("⚠️  psycopg2 not installed, skipping")
        sys.exit(0)

    for attempt in range(30):
        try:
            conn = psycopg2.connect(
                dbname=os.environ.get('DB_NAME', 'postgres'),
                user=os.environ.get('DB_USER', 'postgres'),
                password=os.environ.get('DB_PASSWORD', ''),
                host=db_host,
                port=os.environ.get('DB_PORT', '5432'),
                connect_timeout=3,
            )
            conn.close()
            print("✅ PostgreSQL is ready.")
            sys.exit(0)
        except Exception as e:
            print(f"   Attempt {attempt+1}/30: {str(e)[:80]}")
            time.sleep(2)

    print("❌ PostgreSQL not ready after 60s")
    sys.exit(1)


if __name__ == '__main__':
    wait_for_db()

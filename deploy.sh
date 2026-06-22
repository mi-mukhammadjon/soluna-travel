#!/bin/bash
set -e

echo "═══════════════════════════════════════════════════════"
echo "  SoLuna — Deploy"
echo "═══════════════════════════════════════════════════════"

# 1. Yangiliklarni olish
echo ""
echo "[1/5] Git pull..."
git pull origin main

# 2. Build kerakmi? — faqat Dockerfile yoki requirements.txt o'zgarganda
NEED_BUILD=false

if git diff HEAD~1 --name-only | grep -qE "^(Dockerfile|requirements\.txt)$"; then
    echo "      Dockerfile yoki requirements.txt o'zgardi — build kerak"
    NEED_BUILD=true
else
    echo "      Dockerfile/requirements.txt o'zgarishsiz — cache ishlatiladi"
fi

# 3. Build
if [ "$NEED_BUILD" = true ]; then
    echo ""
    echo "[2/5] Docker build (--no-cache)..."
    docker compose build --no-cache
else
    echo ""
    echo "[2/5] Docker build (cache bilan)..."
    docker compose build
fi

# 4. Restart
echo ""
echo "[3/5] Servislarni qayta ishga tushirish..."
docker compose up -d --remove-orphans

# 5. Migrations
echo ""
echo "[4/5] Migrations..."
docker compose exec -T web python3.11 manage.py migrate --noinput

# 6. Static
echo ""
echo "[5/5] Collectstatic..."
docker compose exec -T web python3.11 manage.py collectstatic --noinput --verbosity 0

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  ✅ Deploy tugadi!"
echo "═══════════════════════════════════════════════════════"
docker compose ps

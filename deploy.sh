#!/bin/bash
set -e

echo "═══════════════════════════════════════════════════════"
echo "  SoLuna — Deploy"
echo "  Branch: $(git branch --show-current)"
echo "  Vaqt:   $(date '+%Y-%m-%d %H:%M:%S')"
echo "═══════════════════════════════════════════════════════"

# 1. Uncommitted o'zgarishlar bor-yo'qligini tekshirish
UNCOMMITTED=$(git status --porcelain 2>/dev/null | grep -v "^??" | head -5)
if [ -n "$UNCOMMITTED" ]; then
    echo ""
    echo "⚠️  Server'da commit qilinmagan o'zgarishlar bor!"
    echo "$UNCOMMITTED"
    echo "    Avtomatik stash qilinadi..."
    git stash push -m "deploy-auto-stash-$(date +%s)"
fi

# 2. Yangiliklarni olish
echo ""
echo "[1/5] Git pull..."
git pull origin main || {
    echo "❌ Git pull xatolik berdi. Manual tekshiring."
    exit 1
}

# 3. Build kerakmi?
NEED_BUILD=false
if git diff HEAD~1 --name-only 2>/dev/null | grep -qE "^(Dockerfile|requirements\.txt)$"; then
    echo "      Dockerfile/requirements.txt o'zgardi — to'liq build"
    NEED_BUILD=true
else
    echo "      Tez build (cache bilan)"
fi

# 4. Build
echo ""
echo "[2/5] Docker build..."
if [ "$NEED_BUILD" = true ]; then
    docker compose build --no-cache
else
    docker compose build
fi

# 5. Restart
echo ""
echo "[3/5] Servislarni qayta ishga tushirish..."
docker compose up -d --remove-orphans

# 6. Web konteyner tayyor bo'lguncha kutish
echo ""
echo "      Web konteyner kutilmoqda..."
sleep 5

# 7. Migrations
echo ""
echo "[4/5] Migrations..."
docker compose exec -T web python3.11 manage.py migrate --noinput

# 8. Collectstatic
echo ""
echo "[5/5] Collectstatic..."
docker compose exec -T web python3.11 manage.py collectstatic --noinput --verbosity 0

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  Deploy tugadi!"
echo "═══════════════════════════════════════════════════════"
docker compose ps

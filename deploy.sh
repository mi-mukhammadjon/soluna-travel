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
echo "[1/6] Git pull..."
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
echo "[2/6] Docker build..."
if [ "$NEED_BUILD" = true ]; then
    docker compose build --no-cache
else
    docker compose build
fi

# 5. Restart
echo ""
echo "[3/6] Servislarni qayta ishga tushirish..."
docker compose up -d --remove-orphans

# 6. Web konteyner tayyor bo'lguncha kutish
echo ""
echo "      Web konteyner kutilmoqda..."
sleep 5

# 7. Migrations + tarjimalarni kompilyatsiya
echo ""
echo "[4/6] Migrations + tarjimalar (compilemessages)..."
docker compose exec -T web python3.11 manage.py migrate --noinput
docker compose exec -T web python3.11 manage.py compilemessages 2>/dev/null || true

# 8. Sample turlarni DB'ga yozish + 9 tilda tarjima (idempotent)
echo ""
echo "[5/6] Turlarni yuklash (9 tilda, rasm + nearby)..."
docker compose exec -T web python3.11 manage.py upload_sample_tours

# 9. Collectstatic
echo ""
echo "[6/6] Collectstatic..."
docker compose exec -T web python3.11 manage.py collectstatic --noinput --verbosity 0

# 10. Static'ni nginx papkasiga sync qilish
#     collectstatic  -> ./staticfiles/  (bind mount, /root/soluna-travel/staticfiles)
#     nginx o'qiydi  -> /var/www/soluna-travel/staticfiles/
#     Ular boshqa papka, shuning uchun nusxalaymiz (aks holda yangi static ko'rinmaydi).
NGINX_STATIC="/var/www/soluna-travel/staticfiles"
if [ -d "$NGINX_STATIC" ]; then
    echo ""
    echo "      Static -> nginx papkasiga ($NGINX_STATIC)..."
    if command -v rsync >/dev/null 2>&1; then
        rsync -a --delete ./staticfiles/ "$NGINX_STATIC"/
    else
        cp -a ./staticfiles/. "$NGINX_STATIC"/
    fi
fi

# 11. Web'ni qayta ishga tushirish — yangi kod/template/tarjima (.mo) yuklansin
#     (bind-mount kod o'zgarishlari gunicorn xotirasida eski qoladi — restart shart).
echo ""
echo "      Web qayta ishga tushirilmoqda (yangi kod/tarjima)..."
docker compose restart web

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  Deploy tugadi!"
echo "═══════════════════════════════════════════════════════"
docker compose ps

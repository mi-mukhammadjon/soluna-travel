#!/usr/bin/env bash
#
# deploy_sample_tours.sh — 3 ta sample turni (9 tilda, rasm + nearby bilan)
# serverda BITTA buyruq bilan bazaga yozadi.
#
# Ishlatish (server, repo ildizida):
#     ./deploy_sample_tours.sh
#     ./deploy_sample_tours.sh --no-images     # faqat matn, rasmsiz
#
# Talab: shu 5 narsa repo ichida bo'lsin (git pull / scp orqali):
#   tours/management/commands/upload_sample_tours.py
#   tours/management/commands/_sample_tours_data.py
#   tours/translation.py
#   tours/migrations/0014_itineraryday_description_ar_and_more.py
#   seed_assets/   (26 ta .png)
#
set -euo pipefail

# Loyiha qaysi container nomi bilan ishlayotganini avtomatik aniqlaymiz
SERVICE="web"

echo "═══ 1/2  Migratsiyalar (ItineraryDay tarjima ustunlari) ═══"
docker compose exec -T "$SERVICE" python manage.py migrate --noinput

echo
echo "═══ 2/2  Turlarni bazaga yozish ═══"
docker compose exec -T "$SERVICE" python manage.py upload_sample_tours "$@"

echo
echo "✅ Tugadi. Endi saytda 3 ta tur 9 tilda, rasm va nearby joylari bilan ko'rinadi."

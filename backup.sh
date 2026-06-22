#!/bin/bash

# Zaxira saqlanadigan joy va sana formati
BACKUP_DIR="/root/soluna-travel/backups"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
FILE_NAME="tour_agency_backup_$DATE.sql"

# Docker ichidagi bazadan nusxa olish (soluna-travel_db_1 - konteyner, tour_agency - baza nomi)
docker exec -t soluna-travel_db_1 pg_dump -U postgres tour_agency > $BACKUP_DIR/$FILE_NAME

# Eski zaxiralarni o'chirish (faqat so'nggi 7 kunlik fayllar saqlab qolinadi)
find $BACKUP_DIR -type f -name "*.sql" -mtime +7 -exec rm {} \;

echo "Zaxira muvaffaqiyatli saqlandi: $FILE_NAME"

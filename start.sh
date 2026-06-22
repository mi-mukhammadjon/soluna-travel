#!/bin/bash
# CRLF ni tozalab asosiy entrypoint ni ishga tushirish
sed -i 's/\r$//' /app/entrypoint.sh 2>/dev/null || true
exec bash /app/entrypoint.sh

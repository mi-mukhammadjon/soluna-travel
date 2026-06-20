FROM python:3.11-slim

# Muhit o'zgaruvchilari
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 1. Tizim kutubxonalarini o'rnatish (PostgreSQL, Redis, Rasmlar va Tarjimalar uchun)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gettext \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 2. Python kutubxonalarini online o'rnatish
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt \
    mkdir -p /app/logs

# 3. Barcha fayllarni nusxalash
COPY . .

# 4. Entrypoint va DB skriptlariga ishlash huquqini berish
RUN chmod +x /app/entrypoint.sh


# Portni ochish
EXPOSE 8008

# Konteyner ishga tushganda bajariladigan buyruq
CMD ["/app/entrypoint.sh"]
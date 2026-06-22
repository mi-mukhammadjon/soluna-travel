FROM ubuntu:22.04

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Tashkent \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

WORKDIR /app

# 1. Asosiy tools
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
        gnupg2 \
        dos2unix \
    && rm -rf /var/lib/apt/lists/*

# 2. Deadsnakes PPA
RUN curl -fsSL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xF23C5A6CF475977595C89F51BA6932366A755776" \
        | gpg --dearmor -o /usr/share/keyrings/deadsnakes.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/deadsnakes.gpg] https://ppa.launchpadcontent.net/deadsnakes/ppa/ubuntu jammy main" \
        > /etc/apt/sources.list.d/deadsnakes.list

# 3. Python 3.11 + tizim kutubxonalari
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 \
        python3.11-dev \
        python3.11-venv \
        python3.11-distutils \
        build-essential \
        gcc \
        gettext \
        libjpeg-dev \
        zlib1g-dev \
        libpng-dev \
        libpq-dev \
        libffi-dev \
        libssl-dev \
        tzdata \
        locales \
    && ln -sf /usr/bin/python3.11 /usr/bin/python \
    && ln -sf /usr/bin/python3.11 /usr/bin/python3 \
    && curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11 \
    && locale-gen en_US.UTF-8 \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4. Python kutubxonalari
COPY requirements.txt .
RUN python3.11 -m pip install --upgrade pip setuptools wheel
RUN python3.11 -m pip install -r requirements.txt

# 5. Papkalar
RUN mkdir -p /app/logs /app/staticfiles /app/media

# 6. Loyiha fayllari
COPY . .

# 7. entrypoint.sh — Windows CRLF'ni LF'ga + executable
RUN dos2unix /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

EXPOSE 8008

# Shell orqali ishga tushirish (permission'dan qat'iy nazar ishlaydi)
CMD ["sh", "/app/entrypoint.sh"]
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DATA_DIR=/app/data

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app
COPY seed ./seed

RUN useradd --create-home --uid 1000 tnc && mkdir -p /app/data && chown -R tnc:tnc /app
USER tnc

EXPOSE 8010
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8010/healthz', timeout=4)"

# 2 worker là đủ cho VPS nhỏ; SQLite ở chế độ WAL chịu được nhiều tiến trình đọc/ghi
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010", "--workers", "2", "--proxy-headers", "--forwarded-allow-ips", "*"]

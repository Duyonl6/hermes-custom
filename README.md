# Hermes Custom Setup

## 1. Clone Hermes gốc
git clone https://github.com/YOUR-HERMES-REPO

## 2. Clone repo này
git clone https://github.com/YOUR-REPO/hermes-custom

## 3. Setup
cd hermes-custom
bash setup.sh

## 4. Add API key
cp .env.example ~/.hermes/.env
nano ~/.hermes/.env

## Web thuê thiết bị: Tiệm nhà Cam

Thư mục [`tiem-nha-cam/`](tiem-nha-cam/README.md) chứa marketplace thuê máy ảnh, action cam, flycam
kiểu Airbnb (FastAPI + SQLite). App gửi thông báo đơn mới về Discord của Hermes qua `DISCORD_WEBHOOK_URL`.

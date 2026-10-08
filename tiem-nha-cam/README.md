# Tiệm nhà Cam — marketplace thuê máy ảnh, action cam, flycam kiểu Airbnb

Web hoàn chỉnh cho thuê thiết bị quay chụp theo mô hình chợ (marketplace) như Airbnb: nhiều chủ thuê
đăng thiết bị, người thuê tìm theo thành phố, ngày và loại máy, xem lịch trống, đặt ngay hoặc gửi yêu cầu,
nhắn tin, thanh toán VietQR, sau đó đánh giá. Chủ thuê có dashboard để duyệt đơn, quản lý tin, khóa lịch
và xem thu nhập.

- **Stack:** FastAPI + Jinja2 (render phía server) + SQLite (WAL) + vanilla JS + Leaflet. Không cần build
  frontend, không phụ thuộc CDN (Leaflet và font Be Vietnam Pro đã vendor sẵn).
- **Dữ liệu:** 31 mẫu máy thật với thông số theo hãng. Giá thuê được khảo sát từ các shop cho thuê ở VN
  (tháng 10/2026). Có 51 tin đăng demo trải trên 8 tỉnh/thành, địa chỉ dùng tên phường mới từ 01/07/2025.
  Xem [DATA_SOURCES.md](DATA_SOURCES.md).

## 1. Kiến trúc & luồng dữ liệu

```
Trình duyệt ──HTTP──► nginx (TLS, gzip, cache /static) ──► uvicorn (2 worker) ──► FastAPI app
                                                                       │
     ┌─────────────────────────────────────────────────────────────────┤
     │ routes/pages.py     khám phá, chi tiết, hồ sơ, /api/listings (bản đồ), /art.svg
     │ routes/bookings.py  checkout → tạo đơn → trang đơn (chat, hủy, đánh giá)
     │ routes/host.py      dashboard, duyệt đơn, đăng/sửa tin, upload ảnh, khóa lịch
     │ routes/auth.py      đăng ký/đăng nhập (PBKDF2), session cookie ký HMAC, CSRF
     │ routes/account.py   hồ sơ, yêu thích
     └──► services.py (nghiệp vụ đặt thuê) ──► db.py ──► SQLite data/app.db  (+ data/uploads/)
                         │
                         └──► Discord webhook (thông báo đơn mới → kênh của Hermes)
```

**Luồng đặt thuê:**

1. Trang chi tiết nhúng cấu hình giá và danh sách ngày bận (`db.blocked_dates`).
2. `calendar.js` chặn chọn khoảng ngày trùng lịch. `listing.js` tính giá tức thì bằng đúng công thức của
   `pricing.py`.
3. `GET /book/{id}` mở trang checkout. Server tính lại báo giá; không tin số liệu do client gửi lên.
4. `POST /book/{id}` gọi `services.create_booking`. Bước này mở `BEGIN IMMEDIATE`, kiểm tra lịch trống lần
   nữa rồi mới INSERT, nên hai người bấm cùng lúc thì chỉ một người đặt được.
5. Tin bật *Đặt ngay* chuyển thẳng sang `confirmed`. Tin còn lại ở trạng thái `pending`, chủ thuê duyệt
   trong 24 giờ, quá hạn thì tự chuyển `expired`.
6. Trạng thái `confirmed` được chia tiếp theo ngày: `upcoming` → `active` (đang thuê) → `completed`. Người
   thuê đánh giá được sau khi đơn `completed`.

**Quy tắc giá** (`app/pricing.py`, theo thực tế các shop VN):

- 1 ngày thuê = 24 giờ kể từ giờ nhận máy.
- Thuê từ 3 ngày giảm `discount_3d`%, từ 7 ngày giảm `discount_7d`%.
- Phí dịch vụ 8% do người thuê trả; phí host 3% trừ vào tiền chủ thuê nhận.
- Tiền cọc thu khi nhận máy, hoàn lại khi trả, không cộng vào tổng thanh toán.
- Chính sách hủy có 3 mức: Linh hoạt / Trung bình / Nghiêm ngặt.

## 2. Tính năng

| Người thuê | Chủ thuê |
|---|---|
| Tìm theo thành phố + ngày + từ khóa (không dấu: "ha dong" khớp "Hà Đông") | Dashboard: thu nhập 6 tháng, tỉ lệ lấp đầy, yêu cầu chờ duyệt |
| 9 danh mục (Mirrorless, DSLR, Compact, Máy film, Action cam, 360°, Flycam, Vlog & Gimbal, Ống kính) | Duyệt / từ chối / hủy đơn, nhắn tin với người thuê |
| Bộ lọc: histogram giá, hãng, Đặt ngay, Giao tận nơi, Chủ thuê siêu cấp, 4,8★, sắp xếp | Đăng/sửa tin: thông số, phụ kiện, giá, cọc, giảm giá, chính sách hủy |
| Bản đồ chia đôi với marker giá (Leaflet + OSM) | Chọn vị trí bằng ghim trên bản đồ, chọn nhanh phường |
| Trang chi tiết: gallery, lịch 2 tháng, thẻ đặt thuê sticky, đánh giá theo 5 tiêu chí | Upload tối đa 12 ảnh (Pillow kiểm tra định dạng, xoay EXIF, resize) |
| Checkout: giao tận nơi, VietQR / tiền mặt, cam kết CCCD + cọc | Khóa lịch khi tự dùng hoặc bảo dưỡng máy |
| Chuyến thuê: timeline, chat, hủy kèm tính tiền hoàn, đánh giá | Thông báo Discord khi có đơn, tin nhắn hoặc đơn bị hủy |
| Yêu thích, hồ sơ công khai, trung tâm trợ giúp có luật bay flycam 2026 | Tin chưa có ảnh thật tự dùng 5 ảnh minh họa SVG |

Giao diện responsive. Trên mobile có thanh tab dưới, sheet tìm kiếm toàn màn hình, gallery vuốt ngang và
thanh đặt thuê cố định ở đáy màn hình, giống app Airbnb.

## 3. Chạy local

**Nhanh nhất:** Windows bấm đúp `run.bat`; macOS/Linux chạy `./run.sh`. Script tự tạo `.venv`, cài thư viện
và mở http://localhost:8010. Yêu cầu Python 3.10+ (Windows: tick "Add python.exe to PATH" khi cài).

Chạy tay:

```bash
cd tiem-nha-cam
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env            # sửa SECRET_KEY
uvicorn app.main:app --reload --port 8010
# mở http://localhost:8010
```

Lần chạy đầu, app tự tạo DB và dữ liệu demo (`AUTO_SEED=1`).

- Seed lại từ đầu: `python -m seed.seed --reset`
- Tài khoản demo (mật khẩu chung `demo1234`):
  - Người thuê: `khach@demo.vn`. Có sẵn 1 đơn đã hoàn tất chờ đánh giá, 1 đơn sắp tới, 1 đơn chờ duyệt.
  - Chủ thuê: `cam@demo.vn` (Tiệm nhà Cam). Có sẵn 2 yêu cầu chờ duyệt và lịch sử thu nhập.

Chạy test: `pytest -q` (32 test, gồm giá, hoàn tiền, chống đặt trùng, CSRF, phân quyền, upload ảnh độc).

## 4. Deploy lên VPS

### Cách A — Docker

```bash
git clone <repo> && cd hermes-custom/tiem-nha-cam
cp .env.example .env && nano .env      # SECRET_KEY, SITE_URL, SESSION_HTTPS_ONLY=1, AUTO_SEED/DEMO_MODE
docker compose up -d --build           # app chạy ở 127.0.0.1:8010, dữ liệu nằm trong ./data
```

### Cách B — systemd (cùng kiểu với `hermes-gateway.service`)

```bash
cd ~/hermes-custom/tiem-nha-cam
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env && nano .env
sudo cp deploy/tiem-nha-cam.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now tiem-nha-cam
```

### nginx + HTTPS + backup

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/tiem-nha-cam   # sửa server_name
sudo ln -s /etc/nginx/sites-available/tiem-nha-cam /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d thue.example.com
crontab -e   # thêm: 0 3 * * * /home/ducdu/hermes-custom/tiem-nha-cam/deploy/backup.sh >> ~/tnc-backup.log 2>&1
```

`backup.sh` chụp DB bằng SQLite online backup API, nên không cần dừng app. Script nén kèm thư mục ảnh và
giữ 14 bản gần nhất.

**Trước khi chạy thật:**

- Đặt `AUTO_SEED=0` và `DEMO_MODE=0`.
- Xóa `data/app.db` để bắt đầu với DB trống.
- Đặt `SESSION_HTTPS_ONLY=1`.
- Điền `VIETQR_*` để hiện mã QR thanh toán.

## 5. Cấu hình (`.env`)

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `SECRET_KEY` | (dev) | Khóa ký cookie phiên — **bắt buộc đổi** |
| `SITE_NAME`, `SITE_URL` | Tiệm nhà Cam | Tên hiển thị, URL tuyệt đối (sitemap, link trong thông báo) |
| `DATA_DIR` | `./data` | Nơi chứa `app.db` và `uploads/` |
| `AUTO_SEED` / `DEMO_MODE` | 1 / 1 | Tạo dữ liệu demo / hiện banner + tài khoản demo |
| `SERVICE_FEE_PCT` / `HOST_FEE_PCT` | 8 / 3 | Phí nền tảng (%) |
| `PENDING_EXPIRE_HOURS` | 24 | Hạn chủ thuê duyệt yêu cầu |
| `VIETQR_BANK_ID`, `VIETQR_ACCOUNT_NO`, `VIETQR_ACCOUNT_NAME` | trống | Mã QR chuyển khoản (img.vietqr.io), nội dung CK = mã đơn |
| `DISCORD_WEBHOOK_URL` | trống | Gửi thông báo về Discord (kênh Hermes) |
| `TILE_URL` | OSM | Nguồn tile bản đồ |
| `SESSION_HTTPS_ONLY` | 0 | Đặt 1 khi chạy HTTPS |

## 6. Tích hợp Hermes

Đặt `DISCORD_WEBHOOK_URL` là webhook của một kênh trong server Discord mà Hermes đang trực. Mỗi đơn mới
(Đặt ngay hoặc yêu cầu), mỗi tin nhắn của người thuê và mỗi đơn bị hủy sẽ được gửi về kênh đó dưới dạng
embed màu cam, kèm link đơn. Từ kênh này bạn có thể cho Hermes đọc và tóm tắt đơn trong ngày.

## 7. Cấu trúc thư mục

```
tiem-nha-cam/
├── app/
│   ├── main.py            # tạo app, middleware session/headers, lifespan (init DB + seed)
│   ├── config.py          # đọc .env
│   ├── db.py              # schema SQLite, truy vấn tin đăng, lịch bận, trạng thái hiệu lực
│   ├── pricing.py         # báo giá, chính sách hủy, tiền hoàn
│   ├── services.py        # tạo đơn (chống trùng), tin nhắn, thông báo Discord
│   ├── search.py          # bộ lọc, sắp xếp, histogram giá, khớp cụm từ không dấu
│   ├── illustrations.py   # sinh ảnh minh họa SVG cho 13 kiểu thiết bị × 5 góc nhìn
│   ├── meta.py            # danh mục, khu vực (phường mới 2025), toạ độ
│   ├── web.py             # template helpers, format VND/ngày, flash, user hiện tại
│   ├── routes/            # pages, auth, bookings, host, account
│   ├── templates/         # Jinja2 (base, index, listing, checkout, booking, host/…)
│   └── static/            # app.css, calendar.js, app.js, listing.js, explore.js, host.js, vendor/leaflet, fonts
├── seed/                  # catalog.py (máy + giá + nguồn), seed.py
├── tests/                 # pytest
├── deploy/                # nginx.conf, tiem-nha-cam.service, backup.sh
├── Dockerfile, docker-compose.yml, requirements*.txt, .env.example
└── DATA_SOURCES.md
```

## 8. Hướng phát triển tiếp

- Cổng thanh toán tự động (VNPay/MoMo/PayOS): webhook xác nhận tiền rồi tự chuyển trạng thái đơn.
- eKYC CCCD (chip NFC / OCR) để giảm cọc cho người thuê đã xác minh.
- Gửi email/Zalo OA nhắc lịch trả máy, cảnh báo trả trễ.
- Lịch iCal xuất/nhập để chủ thuê đồng bộ với Google Calendar.
- Hợp đồng/biên bản bàn giao PDF có chữ ký điện tử.

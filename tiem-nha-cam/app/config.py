"""Cấu hình ứng dụng — đọc từ biến môi trường (và file .env nếu có)."""
from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent


def _load_dotenv(path: Path) -> None:
    """Parser .env tối giản (KEY=VALUE), không ghi đè biến đã có sẵn trong môi trường."""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv(ROOT_DIR / ".env")


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, "1" if default else "0").lower() in {"1", "true", "yes", "on"}


SITE_NAME = os.getenv("SITE_NAME", "Tiệm nhà Cam")
SITE_TAGLINE = os.getenv("SITE_TAGLINE", "Thuê máy ảnh, action cam, flycam từ người thật — gần bạn")
SITE_URL = os.getenv("SITE_URL", "http://localhost:8010")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-doi-ngay-khi-deploy")

DATA_DIR = Path(os.getenv("DATA_DIR", str(ROOT_DIR / "data")))
DB_PATH = Path(os.getenv("DB_PATH", str(DATA_DIR / "app.db")))
UPLOAD_DIR = DATA_DIR / "uploads"
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "8"))

# Phí nền tảng (%): người thuê trả phí dịch vụ, chủ thuê bị trừ phí host khi nhận tiền
SERVICE_FEE_PCT = float(os.getenv("SERVICE_FEE_PCT", "8"))
HOST_FEE_PCT = float(os.getenv("HOST_FEE_PCT", "3"))
# Đơn "chờ duyệt" quá số giờ này mà chủ thuê chưa phản hồi sẽ tự hết hạn
PENDING_EXPIRE_HOURS = int(os.getenv("PENDING_EXPIRE_HOURS", "24"))

# Bản đồ (Leaflet). Mặc định dùng tile OpenStreetMap — nên đổi sang provider riêng khi traffic lớn.
TILE_URL = os.getenv("TILE_URL", "https://tile.openstreetmap.org/{z}/{x}/{y}.png")
TILE_ATTRIBUTION = os.getenv(
    "TILE_ATTRIBUTION", '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
)

# Thanh toán chuyển khoản qua VietQR (img.vietqr.io) — để trống thì ẩn mã QR
VIETQR_BANK_ID = os.getenv("VIETQR_BANK_ID", "")  # vd: VCB, MB, TCB, 970436
VIETQR_ACCOUNT_NO = os.getenv("VIETQR_ACCOUNT_NO", "")
VIETQR_ACCOUNT_NAME = os.getenv("VIETQR_ACCOUNT_NAME", "")

# Thông báo đơn mới qua Discord webhook (tích hợp với Hermes)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

DEMO_MODE = _bool("DEMO_MODE", True)
AUTO_SEED = _bool("AUTO_SEED", True)
SESSION_HTTPS_ONLY = _bool("SESSION_HTTPS_ONLY", False)

try:
    TZ = ZoneInfo(os.getenv("TZ_NAME", "Asia/Ho_Chi_Minh"))
except ZoneInfoNotFoundError:
    # Windows không có sẵn CSDL múi giờ IANA (cần gói tzdata) → dùng UTC+7 cố định, VN không có giờ mùa hè
    TZ = timezone(timedelta(hours=7), "ICT")


def now() -> datetime:
    return datetime.now(TZ)


def today() -> date:
    return now().date()

"""Tiện ích dùng chung cho các route: template, user hiện tại, flash message, format."""
from __future__ import annotations

import sqlite3
from datetime import date, datetime
from urllib.parse import quote, urlencode

from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from . import config, pricing, security
from .meta import CATEGORIES, CATEGORY_LABELS, CITIES

templates = Jinja2Templates(directory=str(config.BASE_DIR / "templates"))

WEEKDAYS = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
STATUS_LABELS = {
    "pending": ("Chờ chủ thuê duyệt", "amber"),
    "confirmed": ("Đã xác nhận", "green"),
    "upcoming": ("Sắp nhận máy", "green"),
    "active": ("Đang thuê", "blue"),
    "completed": ("Đã hoàn tất", "grey"),
    "declined": ("Bị từ chối", "red"),
    "cancelled": ("Đã hủy", "red"),
    "expired": ("Hết hạn duyệt", "grey"),
}
PAYMENT_LABELS = {"transfer": "Chuyển khoản (VietQR)", "cash": "Tiền mặt khi nhận máy"}


def vnd(value) -> str:
    try:
        return f"{int(value):,}".replace(",", ".") + "₫"
    except (TypeError, ValueError):
        return "—"


def short_k(value) -> str:
    """550000 → 550k; 1300000 → 1,3tr (dùng cho marker bản đồ)."""
    v = int(value)
    if v >= 1_000_000:
        s = f"{v / 1_000_000:.1f}".rstrip("0").rstrip(".").replace(".", ",")
        return f"{s}tr"
    return f"{v // 1000}k"


def to_date(value) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def fmt_date(value, style: str = "short") -> str:
    d = to_date(value)
    if style == "long":
        return f"{WEEKDAYS[d.weekday()]}, {d.day:02d}/{d.month:02d}/{d.year}"
    if style == "dm":
        return f"{d.day} thg {d.month}"
    return f"{d.day:02d}/{d.month:02d}/{d.year}"


def date_range(start, end) -> str:
    s, e = to_date(start), to_date(end)
    if s.year == e.year and s.month == e.month:
        return f"{s.day} – {e.day} thg {e.month}"
    return f"{s.day} thg {s.month} – {e.day} thg {e.month}"


def time_ago(value: str) -> str:
    dt = datetime.fromisoformat(value)
    delta = config.now() - dt
    days = delta.days
    if days < 1:
        hours = delta.seconds // 3600
        return f"{hours} giờ trước" if hours else "vừa xong"
    if days < 30:
        return f"{days} ngày trước"
    if days < 365:
        return f"tháng {dt.month}/{dt.year}"
    return f"năm {dt.year}"


def response_label(minutes: int) -> str:
    if minutes <= 30:
        return "trong vài phút"
    if minutes <= 60:
        return "trong vòng 1 giờ"
    if minutes <= 180:
        return "trong vài giờ"
    return "trong ngày"


def art_url(art: str, listing_id: int, view: int) -> str:
    return f"/art.svg?{urlencode({'a': art, 'p': listing_id % 8, 'v': view})}"


def gallery(listing: dict, photos: list[str], count: int = 5) -> list[str]:
    """Ảnh thật do chủ thuê upload được ưu tiên, phần còn thiếu bù bằng ảnh minh họa SVG."""
    urls = [f"/uploads/{f}" for f in photos]
    view = 0
    while len(urls) < count:
        urls.append(art_url(listing["art"], listing["id"], view))
        view += 1
    return urls[:max(count, len(photos))]


templates.env.filters.update(vnd=vnd, short_k=short_k, fmt_date=fmt_date, time_ago=time_ago, response_label=response_label)
templates.env.globals.update(
    site_name=config.SITE_NAME,
    site_tagline=config.SITE_TAGLINE,
    demo_mode=config.DEMO_MODE,
    categories=CATEGORIES,
    cities=CITIES,
    category_labels=CATEGORY_LABELS,
    status_labels=STATUS_LABELS,
    payment_labels=PAYMENT_LABELS,
    policies=pricing.CANCELLATION_POLICIES,
    art_url=art_url,
    date_range=date_range,
    service_fee_pct=config.SERVICE_FEE_PCT,
    host_fee_pct=config.HOST_FEE_PCT,
    tile_url=config.TILE_URL,
    tile_attribution=config.TILE_ATTRIBUTION,
    static_v="1",
)


# ---------------------------------------------------------------- session ---

def current_user(request: Request, conn: sqlite3.Connection) -> dict | None:
    if hasattr(request.state, "user"):
        return request.state.user
    uid = request.session.get("uid")
    user = None
    if uid:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
        user = dict(row) if row else None
        if not user:
            request.session.pop("uid", None)
    request.state.user = user
    return user


def login_redirect(request: Request) -> RedirectResponse:
    nxt = request.url.path + (f"?{request.url.query}" if request.url.query else "")
    return RedirectResponse(f"/login?next={quote(nxt)}", status_code=303)


class LoginRequired(Exception):
    """Ném ra trong route cần đăng nhập — handler trong main.py chuyển hướng sang /login."""


class NotHost(Exception):
    """Người dùng chưa bật chế độ chủ thuê — chuyển về trang onboarding /host."""


def require_user(request: Request, conn: sqlite3.Connection) -> dict:
    user = current_user(request, conn)
    if not user:
        raise LoginRequired()
    return user


def flash(request: Request, message: str, kind: str = "success") -> None:
    request.session.setdefault("flash", []).append([kind, message])


def safe_next(url: str | None, default: str = "/") -> str:
    if url and url.startswith("/") and not url.startswith("//"):
        return url
    return default


def redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url, status_code=303)


def render(request: Request, conn: sqlite3.Connection, template: str, status_code: int = 200, **ctx):
    user = current_user(request, conn)
    wishlist_ids: set[int] = set()
    if user:
        wishlist_ids = {r[0] for r in conn.execute("SELECT listing_id FROM wishlist WHERE user_id = ?", (user["id"],))}
        ctx.setdefault(
            "host_pending",
            conn.execute(
                """SELECT COUNT(*) FROM bookings b JOIN listings l ON l.id = b.listing_id
                   WHERE l.host_id = ? AND b.status = 'pending'""",
                (user["id"],),
            ).fetchone()[0] if user["is_host"] else 0,
        )
    ctx.update(
        request=request,
        user=user,
        csrf=security.csrf_token(request),
        flashes=request.session.pop("flash", []),
        wishlist_ids=wishlist_ids,
        today=config.today().isoformat(),
    )
    return templates.TemplateResponse(request, template, ctx, status_code=status_code)


def not_found(message: str = "Không tìm thấy trang bạn cần.") -> HTTPException:
    return HTTPException(status_code=404, detail=message)

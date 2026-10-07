"""Nghiệp vụ đặt thuê: tạo đơn (chống đặt trùng), đổi trạng thái, thông báo."""
from __future__ import annotations

import json
import logging
import secrets
import sqlite3
import string
import threading
import urllib.request
from datetime import date

from . import config, db, pricing

log = logging.getLogger("tiemnhacam")


class BookingError(Exception):
    pass


def new_code(conn: sqlite3.Connection) -> str:
    alphabet = string.ascii_uppercase.replace("O", "").replace("I", "") + "23456789"
    while True:
        code = "TNC-" + "".join(secrets.choice(alphabet) for _ in range(6))
        if not conn.execute("SELECT 1 FROM bookings WHERE code = ?", (code,)).fetchone():
            return code


def validate_dates(listing: dict, start: date, end: date, allow_past: bool = False) -> None:
    if end <= start:
        raise BookingError("Ngày trả máy phải sau ngày nhận máy.")
    if not allow_past and start < config.today():
        raise BookingError("Ngày nhận máy không được ở quá khứ.")
    if (end - start).days < listing["min_days"]:
        raise BookingError(f"Thiết bị này cho thuê tối thiểu {listing['min_days']} ngày.")
    if (end - start).days > 60:
        raise BookingError("Thời gian thuê tối đa 60 ngày — vui lòng liên hệ chủ thuê để thuê dài hạn.")


def create_booking(
    conn: sqlite3.Connection,
    listing: dict,
    renter_id: int,
    start: date,
    end: date,
    *,
    delivery: bool = False,
    delivery_address: str = "",
    payment_method: str = "transfer",
    message: str = "",
    status: str | None = None,
    created_at: str | None = None,
    allow_past: bool = False,
) -> dict:
    if listing["host_id"] == renter_id:
        raise BookingError("Bạn không thể tự đặt thiết bị của chính mình.")
    if not listing["active"]:
        raise BookingError("Thiết bị này đang tạm ngưng cho thuê.")
    validate_dates(listing, start, end, allow_past=allow_past)
    if delivery and not listing["delivery"]:
        delivery = False
    if delivery and not delivery_address.strip():
        raise BookingError("Vui lòng nhập địa chỉ giao máy.")
    q = pricing.quote(listing, start, end, delivery)
    status = status or ("confirmed" if listing["instant_book"] else "pending")
    ts = created_at or db.now_iso()
    with db.transaction(conn, immediate=True):
        # Kiểm tra lại trong transaction ghi — hai người bấm cùng lúc thì chỉ một người thành công
        if not db.is_available(conn, listing["id"], start, end):
            raise BookingError("Rất tiếc, khoảng ngày này vừa có người đặt. Vui lòng chọn ngày khác.")
        code = new_code(conn)
        cur = conn.execute(
            """INSERT INTO bookings (code, listing_id, renter_id, start_date, end_date, days, price_day, subtotal,
                   discount, service_fee, delivery_fee, deposit, total, host_payout, delivery, delivery_address,
                   payment_method, status, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (code, listing["id"], renter_id, start.isoformat(), end.isoformat(), q.days, q.price_day, q.subtotal,
             q.discount, q.service_fee, q.delivery_fee, q.deposit, q.total, q.host_payout, int(delivery),
             delivery_address.strip(), payment_method, status, ts, ts),
        )
        booking_id = cur.lastrowid
        if message.strip():
            conn.execute(
                "INSERT INTO messages (booking_id, sender_id, body, created_at) VALUES (?,?,?,?)",
                (booking_id, renter_id, message.strip()[:2000], ts),
            )
    return dict(conn.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone())


def get_booking(conn: sqlite3.Connection, code: str) -> dict | None:
    row = conn.execute(
        """SELECT b.*, l.title, l.art, l.host_id, l.city, l.ward, l.lat, l.lng, l.cancellation, l.brand, l.model,
                  l.category, l.instant_book,
                  h.name AS host_name, h.phone AS host_phone, h.avatar_hue AS host_hue, h.email AS host_email,
                  r.name AS renter_name, r.phone AS renter_phone, r.avatar_hue AS renter_hue, r.email AS renter_email
           FROM bookings b
           JOIN listings l ON l.id = b.listing_id
           JOIN users h ON h.id = l.host_id
           JOIN users r ON r.id = b.renter_id
           WHERE b.code = ?""",
        (code,),
    ).fetchone()
    if not row:
        return None
    d = dict(row)
    d["effective_status"] = db.effective_status(d)
    return d


def set_status(conn: sqlite3.Connection, booking_id: int, status: str, refund: int = 0) -> None:
    conn.execute(
        "UPDATE bookings SET status = ?, refund = ?, updated_at = ? WHERE id = ?",
        (status, refund, db.now_iso(), booking_id),
    )


def add_message(conn: sqlite3.Connection, booking_id: int, sender_id: int, body: str) -> None:
    body = body.strip()
    if not body:
        return
    conn.execute(
        "INSERT INTO messages (booking_id, sender_id, body, created_at) VALUES (?,?,?,?)",
        (booking_id, sender_id, body[:2000], db.now_iso()),
    )


# ------------------------------------------------------------ notifications ---

def _post_json(url: str, payload: dict) -> None:
    try:
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json", "User-Agent": "TiemNhaCam/1.0"}
        )
        urllib.request.urlopen(req, timeout=8).read()
    except Exception as exc:  # thông báo lỗi không được làm hỏng luồng đặt thuê
        log.warning("Discord webhook lỗi: %s", exc)


def notify(title: str, lines: list[str], url: str = "") -> None:
    """Gửi thông báo sang Discord (kênh Hermes) nếu có DISCORD_WEBHOOK_URL. Chạy nền, không chặn request."""
    if not config.DISCORD_WEBHOOK_URL:
        return
    embed = {"title": title[:250], "description": "\n".join(lines)[:3800], "color": 0xFF6A1A}
    if url:
        embed["url"] = url
    threading.Thread(target=_post_json, args=(config.DISCORD_WEBHOOK_URL, {"embeds": [embed]}), daemon=True).start()


def vnd(value: int | float) -> str:
    return f"{int(value):,}".replace(",", ".") + "₫"

"""SQLite: kết nối, schema và các hàm truy vấn dùng chung."""
from __future__ import annotations

import json
import sqlite3
import unicodedata
from contextlib import contextmanager
from datetime import date, timedelta
from typing import Iterator

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id               INTEGER PRIMARY KEY,
    email            TEXT NOT NULL UNIQUE,
    password_hash    TEXT NOT NULL,
    name             TEXT NOT NULL,
    phone            TEXT NOT NULL DEFAULT '',
    bio              TEXT NOT NULL DEFAULT '',
    city             TEXT NOT NULL DEFAULT '',
    avatar_hue       INTEGER NOT NULL DEFAULT 20,
    is_host          INTEGER NOT NULL DEFAULT 0,
    id_verified      INTEGER NOT NULL DEFAULT 0,
    superhost        INTEGER NOT NULL DEFAULT 0,
    response_minutes INTEGER NOT NULL DEFAULT 60,
    created_at       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS listings (
    id               INTEGER PRIMARY KEY,
    host_id          INTEGER NOT NULL REFERENCES users(id),
    title            TEXT NOT NULL,
    category         TEXT NOT NULL,
    brand            TEXT NOT NULL,
    model            TEXT NOT NULL,
    kit              TEXT NOT NULL DEFAULT '',
    description      TEXT NOT NULL,
    price_day        INTEGER NOT NULL,
    discount_3d      INTEGER NOT NULL DEFAULT 10,
    discount_7d      INTEGER NOT NULL DEFAULT 20,
    deposit          INTEGER NOT NULL DEFAULT 0,
    retail_value     INTEGER NOT NULL DEFAULT 0,
    city             TEXT NOT NULL,
    ward             TEXT NOT NULL,
    lat              REAL NOT NULL,
    lng              REAL NOT NULL,
    instant_book     INTEGER NOT NULL DEFAULT 0,
    delivery         INTEGER NOT NULL DEFAULT 0,
    delivery_fee     INTEGER NOT NULL DEFAULT 0,
    min_days         INTEGER NOT NULL DEFAULT 1,
    condition        TEXT NOT NULL DEFAULT 'Như mới',
    weight_g         INTEGER NOT NULL DEFAULT 0,
    specs            TEXT NOT NULL DEFAULT '[]',
    included         TEXT NOT NULL DEFAULT '[]',
    cancellation     TEXT NOT NULL DEFAULT 'flexible',
    art              TEXT NOT NULL DEFAULT '',
    active           INTEGER NOT NULL DEFAULT 1,
    created_at       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_listings_city ON listings(city);
CREATE INDEX IF NOT EXISTS idx_listings_category ON listings(category);

CREATE TABLE IF NOT EXISTS listing_photos (
    id          INTEGER PRIMARY KEY,
    listing_id  INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    filename    TEXT NOT NULL,
    position    INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS bookings (
    id               INTEGER PRIMARY KEY,
    code             TEXT NOT NULL UNIQUE,
    listing_id       INTEGER NOT NULL REFERENCES listings(id),
    renter_id        INTEGER NOT NULL REFERENCES users(id),
    start_date       TEXT NOT NULL,
    end_date         TEXT NOT NULL,
    days             INTEGER NOT NULL,
    price_day        INTEGER NOT NULL,
    subtotal         INTEGER NOT NULL,
    discount         INTEGER NOT NULL,
    service_fee      INTEGER NOT NULL,
    delivery_fee     INTEGER NOT NULL,
    deposit          INTEGER NOT NULL,
    total            INTEGER NOT NULL,
    host_payout      INTEGER NOT NULL,
    delivery         INTEGER NOT NULL DEFAULT 0,
    delivery_address TEXT NOT NULL DEFAULT '',
    payment_method   TEXT NOT NULL DEFAULT 'transfer',
    status           TEXT NOT NULL CHECK (status IN ('pending','confirmed','declined','cancelled','expired')),
    refund           INTEGER NOT NULL DEFAULT 0,
    created_at       TEXT NOT NULL,
    updated_at       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_bookings_listing ON bookings(listing_id, start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_bookings_renter ON bookings(renter_id);

CREATE TABLE IF NOT EXISTS blocks (
    id          INTEGER PRIMARY KEY,
    listing_id  INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    start_date  TEXT NOT NULL,
    end_date    TEXT NOT NULL,
    reason      TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS reviews (
    id              INTEGER PRIMARY KEY,
    booking_id      INTEGER UNIQUE REFERENCES bookings(id),
    listing_id      INTEGER NOT NULL REFERENCES listings(id),
    author_id       INTEGER NOT NULL REFERENCES users(id),
    rating          INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    r_condition     INTEGER NOT NULL DEFAULT 5,
    r_accuracy      INTEGER NOT NULL DEFAULT 5,
    r_communication INTEGER NOT NULL DEFAULT 5,
    r_handover      INTEGER NOT NULL DEFAULT 5,
    r_value         INTEGER NOT NULL DEFAULT 5,
    comment         TEXT NOT NULL,
    created_at      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_reviews_listing ON reviews(listing_id);

CREATE TABLE IF NOT EXISTS wishlist (
    user_id     INTEGER NOT NULL REFERENCES users(id),
    listing_id  INTEGER NOT NULL REFERENCES listings(id),
    created_at  TEXT NOT NULL,
    PRIMARY KEY (user_id, listing_id)
);

CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY,
    booking_id  INTEGER NOT NULL REFERENCES bookings(id),
    sender_id   INTEGER NOT NULL REFERENCES users(id),
    body        TEXT NOT NULL,
    created_at  TEXT NOT NULL
);
"""

# Trạng thái đơn đang giữ lịch (không cho người khác đặt trùng)
HOLDING_STATUSES = ("pending", "confirmed")


def unaccent(text: str | None) -> str:
    """Bỏ dấu tiếng Việt + lowercase để tìm kiếm không dấu ('ha noi' khớp 'Hà Nội')."""
    if not text:
        return ""
    text = text.replace("đ", "d").replace("Đ", "D")
    norm = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in norm if unicodedata.category(ch) != "Mn").lower()


def connect() -> sqlite3.Connection:
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH, timeout=10, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    conn.create_function("unaccent", 1, unaccent, deterministic=True)
    return conn


@contextmanager
def transaction(conn: sqlite3.Connection, immediate: bool = False) -> Iterator[sqlite3.Connection]:
    """BEGIN IMMEDIATE khóa ghi ngay — dùng khi kiểm tra lịch trống rồi tạo đơn để tránh đặt trùng."""
    conn.execute("BEGIN IMMEDIATE" if immediate else "BEGIN")
    try:
        yield conn
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    else:
        conn.execute("COMMIT")


def get_db() -> Iterator[sqlite3.Connection]:
    """FastAPI dependency: mỗi request một connection."""
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


def init_db(conn: sqlite3.Connection | None = None) -> None:
    own = conn is None
    conn = conn or connect()
    conn.executescript(SCHEMA)
    if own:
        conn.close()


def now_iso() -> str:
    return config.now().replace(microsecond=0).isoformat()


# ---------------------------------------------------------------- listings ---

RATING_JOIN = """
LEFT JOIN (
    SELECT listing_id, AVG(rating) AS rating_avg, COUNT(*) AS rating_count
    FROM reviews GROUP BY listing_id
) r ON r.listing_id = l.id
"""

LISTING_SELECT = f"""
SELECT l.*, COALESCE(r.rating_avg, 0) AS rating_avg, COALESCE(r.rating_count, 0) AS rating_count,
       u.name AS host_name, u.avatar_hue AS host_hue, u.superhost AS host_superhost,
       u.id_verified AS host_verified, u.response_minutes AS host_response
FROM listings l
JOIN users u ON u.id = l.host_id
{RATING_JOIN}
"""


def listing_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["specs"] = json.loads(d.get("specs") or "[]")
    d["included"] = json.loads(d.get("included") or "[]")
    d["rating_avg"] = round(d.get("rating_avg") or 0, 2)
    d["guest_favorite"] = d["rating_avg"] >= 4.85 and d.get("rating_count", 0) >= 8
    return d


def get_listing(conn: sqlite3.Connection, listing_id: int) -> dict | None:
    row = conn.execute(LISTING_SELECT + " WHERE l.id = ?", (listing_id,)).fetchone()
    return listing_dict(row) if row else None


def listing_photos(conn: sqlite3.Connection, listing_id: int) -> list[str]:
    rows = conn.execute(
        "SELECT filename FROM listing_photos WHERE listing_id = ? ORDER BY position, id", (listing_id,)
    ).fetchall()
    return [r["filename"] for r in rows]


def photos_for(conn: sqlite3.Connection, ids: list[int]) -> dict[int, list[str]]:
    if not ids:
        return {}
    marks = ",".join("?" * len(ids))
    rows = conn.execute(
        f"SELECT listing_id, filename FROM listing_photos WHERE listing_id IN ({marks}) ORDER BY position, id",
        ids,
    ).fetchall()
    out: dict[int, list[str]] = {}
    for r in rows:
        out.setdefault(r["listing_id"], []).append(r["filename"])
    return out


# ------------------------------------------------------------ availability ---

def busy_ranges(conn: sqlite3.Connection, listing_id: int, exclude_booking: int | None = None) -> list[tuple[date, date]]:
    """Các khoảng [start, end) đã bị giữ: đơn pending/confirmed + lịch chủ thuê tự khóa."""
    rows = conn.execute(
        f"""SELECT start_date, end_date FROM bookings
            WHERE listing_id = ? AND status IN ({",".join("?" * len(HOLDING_STATUSES))}) AND id != ?
            UNION ALL
            SELECT start_date, end_date FROM blocks WHERE listing_id = ?""",
        (listing_id, *HOLDING_STATUSES, exclude_booking or -1, listing_id),
    ).fetchall()
    return [(date.fromisoformat(r[0]), date.fromisoformat(r[1])) for r in rows]


def blocked_dates(conn: sqlite3.Connection, listing_id: int, horizon_days: int = 400) -> list[str]:
    """Danh sách ngày (ISO) không thể bắt đầu/đang trong một kỳ thuê — dùng cho lịch JS."""
    today = config.today()
    limit = today + timedelta(days=horizon_days)
    out: set[str] = set()
    for start, end in busy_ranges(conn, listing_id):
        d = max(start, today)
        while d < end and d <= limit:
            out.add(d.isoformat())
            d += timedelta(days=1)
    return sorted(out)


def is_available(conn: sqlite3.Connection, listing_id: int, start: date, end: date) -> bool:
    return all(not (s < end and e > start) for s, e in busy_ranges(conn, listing_id))


def expire_stale_pending(conn: sqlite3.Connection) -> int:
    cutoff = (config.now() - timedelta(hours=config.PENDING_EXPIRE_HOURS)).replace(microsecond=0).isoformat()
    cur = conn.execute(
        "UPDATE bookings SET status = 'expired', updated_at = ? WHERE status = 'pending' AND created_at < ?",
        (now_iso(), cutoff),
    )
    return cur.rowcount


def effective_status(booking: dict | sqlite3.Row) -> str:
    """confirmed được chia nhỏ theo thời gian: upcoming / active (đang thuê) / completed."""
    status = booking["status"]
    if status != "confirmed":
        return status
    today = config.today()
    start = date.fromisoformat(booking["start_date"])
    end = date.fromisoformat(booking["end_date"])
    if today >= end:
        return "completed"
    if today >= start:
        return "active"
    return "upcoming"

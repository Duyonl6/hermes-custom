"""Khu vực chủ thuê: dashboard, duyệt đơn, đăng/sửa tin, ảnh, khóa lịch."""
from __future__ import annotations

import io
import json
import sqlite3
import uuid
from datetime import date, timedelta

from fastapi import APIRouter, Depends, Request, UploadFile

from .. import config, db, pricing, security, services
from ..meta import CATEGORY_LABELS, CITIES, LOCATIONS, art_for
from ..web import NotHost, art_url, flash, gallery, not_found, redirect, render, require_user, vnd

router = APIRouter(prefix="/host")

CONDITIONS = ["Như mới", "Rất tốt", "Tốt", "Có vết xước nhẹ"]
ALLOWED_IMAGE = {"JPEG", "PNG", "WEBP"}


def _require_host(request: Request, conn: sqlite3.Connection) -> dict:
    user = require_user(request, conn)
    if not user["is_host"]:
        raise NotHost()
    return user


def _own_listing(conn: sqlite3.Connection, user: dict, listing_id: int) -> dict:
    listing = db.get_listing(conn, listing_id)
    if not listing or listing["host_id"] != user["id"]:
        raise not_found("Không tìm thấy tin đăng.")
    return listing


@router.get("")
def dashboard(request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    user = require_user(request, conn)
    if not user["is_host"]:
        return render(request, conn, "host/onboard.html")
    db.expire_stale_pending(conn)
    today = config.today()
    uid = user["id"]

    def rows(sql: str, *args) -> list[dict]:
        out = []
        for r in conn.execute(sql, args):
            d = dict(r)
            if "status" in d:
                d["effective_status"] = db.effective_status(d)
            out.append(d)
        return out

    base = """SELECT b.*, l.title, l.art, l.id AS lid, u.name AS renter_name, u.avatar_hue AS renter_hue,
                     u.id_verified AS renter_verified, u.phone AS renter_phone
              FROM bookings b JOIN listings l ON l.id = b.listing_id JOIN users u ON u.id = b.renter_id
              WHERE l.host_id = ?"""
    pending = rows(base + " AND b.status = 'pending' ORDER BY b.created_at", uid)
    upcoming = rows(base + " AND b.status = 'confirmed' AND b.end_date >= ? ORDER BY b.start_date LIMIT 12", uid, today.isoformat())
    recent = rows(base + " AND b.status IN ('confirmed','cancelled','declined') ORDER BY b.updated_at DESC LIMIT 8", uid)
    for b in pending:
        b["last_message"] = (conn.execute(
            "SELECT body FROM messages WHERE booking_id = ? ORDER BY id LIMIT 1", (b["id"],)).fetchone() or [""])[0]

    months = []
    for i in range(5, -1, -1):
        yy, mm = today.year, today.month - i
        while mm <= 0:
            mm, yy = mm + 12, yy - 1
        m, nxt = date(yy, mm, 1), date(yy + (mm == 12), mm % 12 + 1, 1)
        total = conn.execute(
            """SELECT COALESCE(SUM(b.host_payout), 0) FROM bookings b JOIN listings l ON l.id = b.listing_id
               WHERE l.host_id = ? AND b.status = 'confirmed' AND b.start_date >= ? AND b.start_date < ?""",
            (uid, m.isoformat(), nxt.isoformat()),
        ).fetchone()[0]
        months.append({"label": f"T{m.month}", "total": total})
    peak = max([m["total"] for m in months] + [1])
    for m in months:
        m["pct"] = round(m["total"] / peak * 100)

    listings = [db.listing_dict(r) for r in conn.execute(
        db.LISTING_SELECT + " WHERE l.host_id = ? ORDER BY l.active DESC, l.created_at DESC", (uid,))]
    photos = db.photos_for(conn, [l["id"] for l in listings])
    for l in listings:
        l["cover"] = gallery(l, photos.get(l["id"], []), 1)[0]
        nb = conn.execute(
            "SELECT start_date FROM bookings WHERE listing_id = ? AND status = 'confirmed' AND start_date >= ? ORDER BY start_date LIMIT 1",
            (l["id"], today.isoformat()),
        ).fetchone()
        l["next_booking"] = nb[0] if nb else None
        l["booked_30"] = sum(
            max(0, (min(date.fromisoformat(e), today + timedelta(days=30)) - max(date.fromisoformat(s), today)).days)
            for s, e in conn.execute(
                "SELECT start_date, end_date FROM bookings WHERE listing_id = ? AND status = 'confirmed' AND end_date > ? AND start_date < ?",
                (l["id"], today.isoformat(), (today + timedelta(days=30)).isoformat()),
            )
        )
    rating = conn.execute(
        "SELECT COUNT(*), COALESCE(AVG(rating), 0) FROM reviews rv JOIN listings l ON l.id = rv.listing_id WHERE l.host_id = ?",
        (uid,),
    ).fetchone()
    occupancy = round(sum(l["booked_30"] for l in listings if l["active"]) / max(1, 30 * sum(1 for l in listings if l["active"])) * 100)
    return render(
        request, conn, "host/dashboard.html",
        pending=pending, upcoming=upcoming, recent=recent, listings=listings, months=months,
        month_total=months[-1]["total"], review_count=rating[0], review_avg=round(rating[1], 2), occupancy=occupancy,
    )


@router.post("/activate")
async def activate(request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    user = require_user(request, conn)
    await security.form_with_csrf(request)
    conn.execute("UPDATE users SET is_host = 1 WHERE id = ?", (user["id"],))
    flash(request, "Bạn đã trở thành chủ thuê! Hãy đăng thiết bị đầu tiên.")
    return redirect("/host/listings/new")


# ---------------------------------------------------------------- bookings ---

@router.post("/bookings/{code}/{action}")
async def booking_action(code: str, action: str, request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    user = require_user(request, conn)
    form = await security.form_with_csrf(request)
    booking = services.get_booking(conn, code)
    if not booking or booking["host_id"] != user["id"]:
        raise not_found("Không tìm thấy đơn thuê.")
    status = booking["effective_status"]
    note = (form.get("note") or "").strip()
    if action == "accept" and status == "pending":
        services.set_status(conn, booking["id"], "confirmed")
        services.add_message(conn, booking["id"], user["id"], note or "[Hệ thống] Chủ thuê đã xác nhận đơn. Hẹn gặp bạn khi nhận máy!")
        flash(request, f"Đã xác nhận đơn {code}.")
    elif action == "decline" and status == "pending":
        services.set_status(conn, booking["id"], "declined", booking["total"])
        services.add_message(conn, booking["id"], user["id"], note or "[Hệ thống] Rất tiếc, chủ thuê không thể nhận đơn này.")
        flash(request, f"Đã từ chối đơn {code}.")
    elif action == "cancel" and status == "upcoming":
        services.set_status(conn, booking["id"], "cancelled", booking["total"])
        services.add_message(conn, booking["id"], user["id"], note or "[Hệ thống] Chủ thuê đã hủy đơn — người thuê được hoàn 100%.")
        flash(request, f"Đã hủy đơn {code}, người thuê được hoàn {vnd(booking['total'])}.", "warning")
    else:
        flash(request, "Thao tác không hợp lệ với trạng thái đơn hiện tại.", "error")
    return redirect(security_safe(form.get("back")) or "/host")


def security_safe(url: str | None) -> str:
    return url if url and url.startswith("/") and not url.startswith("//") else ""


# ---------------------------------------------------------------- listings ---

def _form_defaults(listing: dict | None = None) -> dict:
    if listing:
        d = dict(listing)
        d["specs_text"] = "\n".join(f"{k}: {v}" for k, v in listing["specs"])
        d["included_text"] = "\n".join(listing["included"])
        return d
    city, ward, lat, lng = LOCATIONS["hn-caugiay"]
    return dict(title="", category="mirrorless", brand="", model="", kit="", description="", price_day=300_000,
                discount_3d=10, discount_7d=20, deposit=2_000_000, retail_value=0, city=city, ward=ward, lat=lat, lng=lng,
                instant_book=1, delivery=0, delivery_fee=30_000, min_days=1, condition="Như mới", weight_g=0,
                specs_text="", included_text="", cancellation="flexible")


def _parse_listing_form(form) -> tuple[dict, list[str]]:
    errors: list[str] = []

    def num(name: str, lo: int, hi: int, label: str, default: int = 0) -> int:
        raw = (form.get(name) or "").replace(".", "").replace(",", "").strip()
        try:
            value = int(raw) if raw else default
        except ValueError:
            errors.append(f"{label} phải là số.")
            return default
        if not lo <= value <= hi:
            errors.append(f"{label} phải trong khoảng {lo:,} – {hi:,}.".replace(",", "."))
        return value

    def fnum(name: str, default: float) -> float:
        try:
            return float(form.get(name) or default)
        except ValueError:
            return default

    data = {
        "title": (form.get("title") or "").strip()[:100],
        "category": form.get("category") if form.get("category") in CATEGORY_LABELS else "mirrorless",
        "brand": (form.get("brand") or "").strip()[:40],
        "model": (form.get("model") or "").strip()[:80],
        "kit": (form.get("kit") or "").strip()[:120],
        "description": (form.get("description") or "").strip()[:5000],
        "price_day": num("price_day", 20_000, 20_000_000, "Giá thuê/ngày"),
        "discount_3d": num("discount_3d", 0, 50, "Giảm giá từ 3 ngày"),
        "discount_7d": num("discount_7d", 0, 70, "Giảm giá từ 7 ngày"),
        "deposit": num("deposit", 0, 200_000_000, "Tiền cọc"),
        "retail_value": num("retail_value", 0, 500_000_000, "Giá trị thiết bị"),
        "city": form.get("city") if form.get("city") in CITIES else CITIES[0],
        "ward": (form.get("ward") or "").strip()[:80],
        "lat": fnum("lat", 21.03),
        "lng": fnum("lng", 105.85),
        "instant_book": int(form.get("instant_book") == "1"),
        "delivery": int(form.get("delivery") == "1"),
        "delivery_fee": num("delivery_fee", 0, 1_000_000, "Phí giao máy"),
        "min_days": num("min_days", 1, 30, "Số ngày thuê tối thiểu", 1),
        "condition": form.get("condition") if form.get("condition") in CONDITIONS else CONDITIONS[0],
        "weight_g": num("weight_g", 0, 50_000, "Trọng lượng"),
        "cancellation": form.get("cancellation") if form.get("cancellation") in pricing.CANCELLATION_POLICIES else "flexible",
        "specs_text": (form.get("specs_text") or "")[:3000],
        "included_text": (form.get("included_text") or "")[:2000],
    }
    if len(data["title"]) < 10:
        errors.append("Tiêu đề cần ít nhất 10 ký tự.")
    if not data["brand"] or not data["model"]:
        errors.append("Vui lòng nhập hãng và tên model.")
    if len(data["description"]) < 30:
        errors.append("Mô tả cần ít nhất 30 ký tự — hãy kể về tình trạng máy và phụ kiện.")
    if not data["ward"]:
        errors.append("Vui lòng nhập phường/xã nơi bàn giao máy.")
    if not (8 <= data["lat"] <= 24 and 102 <= data["lng"] <= 110):
        errors.append("Vị trí trên bản đồ phải nằm trong lãnh thổ Việt Nam.")
    if data["discount_7d"] < data["discount_3d"]:
        errors.append("Giảm giá thuê 7 ngày nên lớn hơn hoặc bằng giảm giá 3 ngày.")
    specs = []
    for line in data["specs_text"].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            if k.strip() and v.strip():
                specs.append([k.strip()[:40], v.strip()[:120]])
    data["specs"] = json.dumps(specs[:20], ensure_ascii=False)
    data["included"] = json.dumps([x.strip()[:80] for x in data["included_text"].splitlines() if x.strip()][:20], ensure_ascii=False)
    return data, errors


def _form_context(listing_form: dict, listing_id: int | None = None, photos=None, blocks=None, errors=None) -> dict:
    return dict(
        lf=listing_form, listing_id=listing_id, photos=photos or [], blocks=blocks or [], errors=errors or [],
        conditions=CONDITIONS, locations=LOCATIONS, cities_list=CITIES,
        locations_json=json.dumps({k: v for k, v in LOCATIONS.items()}, ensure_ascii=False),
    )


async def _save_photos(conn: sqlite3.Connection, listing_id: int, files: list[UploadFile]) -> list[str]:
    from PIL import Image, ImageOps  # import muộn để app vẫn chạy khi chưa cài Pillow (chỉ upload cần)

    errors = []
    config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    pos = conn.execute("SELECT COALESCE(MAX(position), -1) + 1 FROM listing_photos WHERE listing_id = ?", (listing_id,)).fetchone()[0]
    count = conn.execute("SELECT COUNT(*) FROM listing_photos WHERE listing_id = ?", (listing_id,)).fetchone()[0]
    for f in files:
        if not f or not f.filename:
            continue
        if count >= 12:
            errors.append("Mỗi tin tối đa 12 ảnh.")
            break
        raw = await f.read(config.MAX_UPLOAD_MB * 1024 * 1024 + 1)
        if len(raw) > config.MAX_UPLOAD_MB * 1024 * 1024:
            errors.append(f"{f.filename}: ảnh vượt quá {config.MAX_UPLOAD_MB}MB.")
            continue
        try:
            img = Image.open(io.BytesIO(raw))
            if img.format not in ALLOWED_IMAGE:
                raise ValueError
            img = ImageOps.exif_transpose(img).convert("RGB")
        except Exception:
            errors.append(f"{f.filename}: không phải ảnh JPG/PNG/WEBP hợp lệ.")
            continue
        img.thumbnail((1800, 1800))
        name = f"{listing_id}-{uuid.uuid4().hex[:12]}.jpg"
        img.save(config.UPLOAD_DIR / name, "JPEG", quality=85, optimize=True, progressive=True)
        conn.execute("INSERT INTO listing_photos (listing_id, filename, position) VALUES (?,?,?)", (listing_id, name, pos))
        pos += 1
        count += 1
    return errors


@router.get("/listings/new")
def new_listing(request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    _require_host(request, conn)
    return render(request, conn, "host/listing_form.html", **_form_context(_form_defaults()))


@router.post("/listings/new")
async def create_listing(request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    user = _require_host(request, conn)
    form = await security.form_with_csrf(request)
    data, errors = _parse_listing_form(form)
    if errors:
        return render(request, conn, "host/listing_form.html", status_code=400, **_form_context(data, errors=errors))
    cur = conn.execute(
        """INSERT INTO listings (host_id, title, category, brand, model, kit, description, price_day, discount_3d, discount_7d,
               deposit, retail_value, city, ward, lat, lng, instant_book, delivery, delivery_fee, min_days, condition, weight_g,
               specs, included, cancellation, art, active, created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1,?)""",
        (user["id"], data["title"], data["category"], data["brand"], data["model"], data["kit"], data["description"],
         data["price_day"], data["discount_3d"], data["discount_7d"], data["deposit"], data["retail_value"], data["city"],
         data["ward"], data["lat"], data["lng"], data["instant_book"], data["delivery"], data["delivery_fee"],
         data["min_days"], data["condition"], data["weight_g"], data["specs"], data["included"], data["cancellation"],
         art_for(data["category"], data["brand"]), db.now_iso()),
    )
    listing_id = cur.lastrowid
    upload_errors = await _save_photos(conn, listing_id, form.getlist("photos"))
    for e in upload_errors:
        flash(request, e, "warning")
    flash(request, "Đã đăng tin! Tin của bạn đã hiển thị trên trang khám phá.")
    return redirect(f"/listing/{listing_id}")


@router.get("/listings/{listing_id}/edit")
def edit_listing(listing_id: int, request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    user = _require_host(request, conn)
    listing = _own_listing(conn, user, listing_id)
    photos = [dict(r) for r in conn.execute(
        "SELECT * FROM listing_photos WHERE listing_id = ? ORDER BY position, id", (listing_id,))]
    blocks = [dict(r) for r in conn.execute(
        "SELECT * FROM blocks WHERE listing_id = ? AND end_date >= ? ORDER BY start_date", (listing_id, config.today().isoformat()))]
    ctx = _form_context(_form_defaults(listing), listing_id, photos, blocks)
    ctx["art_preview"] = [art_url(listing["art"], listing_id, v) for v in range(5)]
    return render(request, conn, "host/listing_form.html", **ctx)


@router.post("/listings/{listing_id}/edit")
async def update_listing(listing_id: int, request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    user = _require_host(request, conn)
    listing = _own_listing(conn, user, listing_id)
    form = await security.form_with_csrf(request)
    data, errors = _parse_listing_form(form)
    if errors:
        photos = [dict(r) for r in conn.execute("SELECT * FROM listing_photos WHERE listing_id = ? ORDER BY position, id", (listing_id,))]
        return render(request, conn, "host/listing_form.html", status_code=400, **_form_context(data, listing_id, photos, errors=errors))
    art = listing["art"] if (data["category"], data["brand"]) == (listing["category"], listing["brand"]) else art_for(data["category"], data["brand"])
    conn.execute(
        """UPDATE listings SET title=?, category=?, brand=?, model=?, kit=?, description=?, price_day=?, discount_3d=?,
               discount_7d=?, deposit=?, retail_value=?, city=?, ward=?, lat=?, lng=?, instant_book=?, delivery=?,
               delivery_fee=?, min_days=?, condition=?, weight_g=?, specs=?, included=?, cancellation=?, art=?
           WHERE id = ?""",
        (data["title"], data["category"], data["brand"], data["model"], data["kit"], data["description"], data["price_day"],
         data["discount_3d"], data["discount_7d"], data["deposit"], data["retail_value"], data["city"], data["ward"],
         data["lat"], data["lng"], data["instant_book"], data["delivery"], data["delivery_fee"], data["min_days"],
         data["condition"], data["weight_g"], data["specs"], data["included"], data["cancellation"], art, listing_id),
    )
    for e in await _save_photos(conn, listing_id, form.getlist("photos")):
        flash(request, e, "warning")
    flash(request, "Đã lưu thay đổi.")
    return redirect(f"/host/listings/{listing_id}/edit")


@router.post("/listings/{listing_id}/toggle")
async def toggle_listing(listing_id: int, request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    user = _require_host(request, conn)
    listing = _own_listing(conn, user, listing_id)
    await security.form_with_csrf(request)
    conn.execute("UPDATE listings SET active = ? WHERE id = ?", (0 if listing["active"] else 1, listing_id))
    flash(request, "Đã tạm ẩn tin đăng." if listing["active"] else "Tin đăng đã hiển thị trở lại.")
    return redirect("/host#listings")


@router.post("/listings/{listing_id}/photos/{photo_id}/delete")
async def delete_photo(listing_id: int, photo_id: int, request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    user = _require_host(request, conn)
    _own_listing(conn, user, listing_id)
    await security.form_with_csrf(request)
    row = conn.execute("SELECT filename FROM listing_photos WHERE id = ? AND listing_id = ?", (photo_id, listing_id)).fetchone()
    if row:
        conn.execute("DELETE FROM listing_photos WHERE id = ?", (photo_id,))
        (config.UPLOAD_DIR / row["filename"]).unlink(missing_ok=True)
        flash(request, "Đã xóa ảnh.")
    return redirect(f"/host/listings/{listing_id}/edit#photos")


@router.post("/listings/{listing_id}/blocks")
async def add_block(listing_id: int, request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    user = _require_host(request, conn)
    _own_listing(conn, user, listing_id)
    form = await security.form_with_csrf(request)
    try:
        s = date.fromisoformat(form.get("start") or "")
        e = date.fromisoformat(form.get("end") or "")
        if e <= s or s < config.today():
            raise ValueError
    except ValueError:
        flash(request, "Khoảng ngày khóa lịch không hợp lệ.", "error")
        return redirect(f"/host/listings/{listing_id}/edit#calendar")
    if not db.is_available(conn, listing_id, s, e):
        flash(request, "Khoảng ngày này đang có đơn thuê — hãy chọn khoảng khác hoặc xử lý đơn trước.", "error")
        return redirect(f"/host/listings/{listing_id}/edit#calendar")
    conn.execute("INSERT INTO blocks (listing_id, start_date, end_date, reason) VALUES (?,?,?,?)",
                 (listing_id, s.isoformat(), e.isoformat(), (form.get("reason") or "").strip()[:120]))
    flash(request, "Đã khóa lịch.")
    return redirect(f"/host/listings/{listing_id}/edit#calendar")


@router.post("/listings/{listing_id}/blocks/{block_id}/delete")
async def delete_block(listing_id: int, block_id: int, request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    user = _require_host(request, conn)
    _own_listing(conn, user, listing_id)
    await security.form_with_csrf(request)
    conn.execute("DELETE FROM blocks WHERE id = ? AND listing_id = ?", (block_id, listing_id))
    flash(request, "Đã mở lại lịch.")
    return redirect(f"/host/listings/{listing_id}/edit#calendar")

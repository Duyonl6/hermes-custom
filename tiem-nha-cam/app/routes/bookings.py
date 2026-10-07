"""Luồng đặt thuê phía người thuê: xác nhận & thanh toán, chuyến thuê, nhắn tin, hủy, đánh giá."""
from __future__ import annotations

import sqlite3
from datetime import date
from urllib.parse import quote, urlencode

from fastapi import APIRouter, Depends, Request

from .. import config, db, pricing, security, services
from ..web import art_url, flash, gallery, not_found, redirect, render, require_user, vnd

router = APIRouter()


def _parse(value: str | None) -> date | None:
    try:
        return date.fromisoformat(value) if value else None
    except ValueError:
        return None


def _back_to_listing(listing_id: int, start: str = "", end: str = "") -> str:
    qs = urlencode({k: v for k, v in (("start", start), ("end", end)) if v})
    return f"/listing/{listing_id}" + (f"?{qs}#book" if qs else "#book")


def vietqr_url(booking: dict) -> str:
    if not (config.VIETQR_BANK_ID and config.VIETQR_ACCOUNT_NO):
        return ""
    params = urlencode({"amount": booking["total"], "addInfo": booking["code"], "accountName": config.VIETQR_ACCOUNT_NAME})
    return f"https://img.vietqr.io/image/{config.VIETQR_BANK_ID}-{config.VIETQR_ACCOUNT_NO}-compact2.png?{params}"


@router.get("/book/{listing_id}")
def checkout(listing_id: int, request: Request, start: str = "", end: str = "", delivery: str = "",
             conn: sqlite3.Connection = Depends(db.get_db)):
    user = require_user(request, conn)
    listing = db.get_listing(conn, listing_id)
    if not listing or not listing["active"]:
        raise not_found("Tin đăng không tồn tại hoặc đã ngưng cho thuê.")
    s, e = _parse(start), _parse(end)
    if not s or not e:
        flash(request, "Hãy chọn ngày nhận và ngày trả máy trước khi đặt.", "error")
        return redirect(_back_to_listing(listing_id))
    try:
        if listing["host_id"] == user["id"]:
            raise services.BookingError("Bạn không thể tự đặt thiết bị của chính mình.")
        services.validate_dates(listing, s, e)
        if not db.is_available(conn, listing_id, s, e):
            raise services.BookingError("Khoảng ngày này đã có người đặt, vui lòng chọn ngày khác.")
    except services.BookingError as exc:
        flash(request, str(exc), "error")
        return redirect(_back_to_listing(listing_id, start, end))
    want_delivery = delivery == "1" and bool(listing["delivery"])
    q = pricing.quote(listing, s, e, want_delivery)
    photos = db.listing_photos(conn, listing_id)
    return render(
        request, conn, "checkout.html",
        listing=listing, q=q, start=s, end=e, delivery=want_delivery, cover=gallery(listing, photos, 1)[0],
        policy=pricing.CANCELLATION_POLICIES[listing["cancellation"]], form={}, errors=[],
    )


@router.post("/book/{listing_id}")
async def create_booking(listing_id: int, request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    user = require_user(request, conn)
    form = await security.form_with_csrf(request)
    listing = db.get_listing(conn, listing_id)
    if not listing:
        raise not_found()
    s, e = _parse(form.get("start")), _parse(form.get("end"))
    delivery = form.get("delivery") == "1"
    phone = (form.get("phone") or user["phone"] or "").replace(" ", "")
    errors = []
    if not s or not e:
        errors.append("Ngày thuê không hợp lệ.")
    if not phone:
        errors.append("Vui lòng nhập số điện thoại để chủ thuê liên hệ bàn giao máy.")
    if form.get("agree_id") != "1":
        errors.append("Bạn cần đồng ý xuất trình CCCD/hộ chiếu bản gốc khi nhận máy.")
    if form.get("agree_rules") != "1":
        errors.append("Bạn cần đồng ý với quy định thuê và chính sách hủy.")
    if not listing["instant_book"] and len((form.get("message") or "").strip()) < 10:
        errors.append("Thiết bị này cần chủ thuê duyệt — hãy gửi lời nhắn (ít nhất 10 ký tự) giới thiệu mục đích thuê.")
    booking = None
    if not errors:
        try:
            booking = services.create_booking(
                conn, listing, user["id"], s, e,
                delivery=delivery, delivery_address=form.get("delivery_address") or "",
                payment_method="cash" if form.get("payment_method") == "cash" else "transfer",
                message=form.get("message") or "",
            )
        except services.BookingError as exc:
            errors.append(str(exc))
    if errors:
        q = pricing.quote(listing, s, e, delivery) if s and e and e > s else None
        if not q:
            flash(request, errors[0], "error")
            return redirect(_back_to_listing(listing_id))
        photos = db.listing_photos(conn, listing_id)
        return render(
            request, conn, "checkout.html", status_code=400,
            listing=listing, q=q, start=s, end=e, delivery=delivery and bool(listing["delivery"]),
            cover=gallery(listing, photos, 1)[0], policy=pricing.CANCELLATION_POLICIES[listing["cancellation"]],
            form=dict(form), errors=errors,
        )
    if phone != user["phone"]:
        conn.execute("UPDATE users SET phone = ? WHERE id = ?", (phone, user["id"]))
    url = f"{config.SITE_URL}/trips/{booking['code']}"
    services.notify(
        ("⚡ Đơn mới (đặt ngay)" if booking["status"] == "confirmed" else "📩 Yêu cầu đặt thuê mới") + f" · {booking['code']}",
        [f"**{listing['title']}**", f"Người thuê: {user['name']} · {phone}",
         f"Ngày: {booking['start_date']} → {booking['end_date']} ({booking['days']} ngày)",
         f"Tổng: {vnd(booking['total'])} · Cọc: {vnd(booking['deposit'])}",
         f"Chủ thuê: {listing['host_name']}"],
        url,
    )
    if booking["status"] == "confirmed":
        flash(request, "Đặt thuê thành công! Đơn đã được xác nhận tự động.")
    else:
        flash(request, f"Đã gửi yêu cầu! {listing['host_name']} sẽ phản hồi trong vòng {config.PENDING_EXPIRE_HOURS} giờ.")
    return redirect(f"/trips/{booking['code']}")


@router.get("/trips")
def trips(request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    user = require_user(request, conn)
    db.expire_stale_pending(conn)
    rows = conn.execute(
        """SELECT b.*, l.title, l.art, l.city, l.ward, l.id AS lid, h.name AS host_name,
                  (SELECT filename FROM listing_photos p WHERE p.listing_id = l.id ORDER BY position, id LIMIT 1) AS photo,
                  (SELECT 1 FROM reviews rv WHERE rv.booking_id = b.id) AS reviewed
           FROM bookings b JOIN listings l ON l.id = b.listing_id JOIN users h ON h.id = l.host_id
           WHERE b.renter_id = ? ORDER BY b.start_date DESC""",
        (user["id"],),
    ).fetchall()
    groups = {"upcoming": [], "past": [], "cancelled": []}
    for r in rows:
        b = dict(r)
        b["effective_status"] = db.effective_status(b)
        b["cover"] = f"/uploads/{b['photo']}" if b["photo"] else art_url(b["art"], b["lid"], 0)
        key = {"completed": "past", "declined": "cancelled", "cancelled": "cancelled", "expired": "cancelled"}.get(
            b["effective_status"], "upcoming")
        groups[key].append(b)
    groups["upcoming"].sort(key=lambda b: b["start_date"])
    return render(request, conn, "trips.html", groups=groups)


def _load_for_party(request: Request, conn: sqlite3.Connection, code: str) -> tuple[dict, dict, str]:
    user = require_user(request, conn)
    db.expire_stale_pending(conn)
    booking = services.get_booking(conn, code)
    if not booking:
        raise not_found("Không tìm thấy đơn thuê.")
    if user["id"] == booking["renter_id"]:
        role = "renter"
    elif user["id"] == booking["host_id"]:
        role = "host"
    else:
        raise not_found("Không tìm thấy đơn thuê.")
    return user, booking, role


@router.get("/trips/{code}")
def trip_detail(code: str, request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    user, booking, role = _load_for_party(request, conn, code)
    messages = [dict(m) for m in conn.execute(
        """SELECT m.*, u.name, u.avatar_hue FROM messages m JOIN users u ON u.id = m.sender_id
           WHERE m.booking_id = ? ORDER BY m.created_at, m.id""",
        (booking["id"],),
    )]
    review = conn.execute("SELECT * FROM reviews WHERE booking_id = ?", (booking["id"],)).fetchone()
    status = booking["effective_status"]
    refund_preview = None
    if role == "renter" and status in {"pending", "upcoming"}:
        refund_preview = pricing.refund_amount(booking, booking["cancellation"], config.today())
    photos = db.listing_photos(conn, booking["listing_id"])
    listing_stub = {"id": booking["listing_id"], "art": booking["art"]}
    return render(
        request, conn, "booking.html",
        b=booking, role=role, messages=messages, review=dict(review) if review else None,
        refund_preview=refund_preview, cover=gallery(listing_stub, photos, 1)[0],
        qr=vietqr_url(booking) if booking["payment_method"] == "transfer" and status in {"pending", "upcoming"} else "",
        policy=pricing.CANCELLATION_POLICIES[booking["cancellation"]],
        maps_url="https://www.google.com/maps/search/?api=1&query=" + quote(f"{booking['ward']}, {booking['city']}"),
    )


@router.post("/trips/{code}/message")
async def trip_message(code: str, request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    user, booking, role = _load_for_party(request, conn, code)
    form = await security.form_with_csrf(request)
    body = (form.get("body") or "").strip()
    if body:
        services.add_message(conn, booking["id"], user["id"], body)
        if role == "renter":
            services.notify(f"💬 Tin nhắn mới · {code}", [f"{user['name']}: {body[:300]}"], f"{config.SITE_URL}/trips/{code}")
    return redirect(f"/trips/{code}#chat")


@router.post("/trips/{code}/cancel")
async def trip_cancel(code: str, request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    user, booking, role = _load_for_party(request, conn, code)
    await security.form_with_csrf(request)
    if role != "renter" or booking["effective_status"] not in {"pending", "upcoming"}:
        flash(request, "Đơn này không thể hủy ở trạng thái hiện tại.", "error")
        return redirect(f"/trips/{code}")
    refund = pricing.refund_amount(booking, booking["cancellation"], config.today())
    services.set_status(conn, booking["id"], "cancelled", refund)
    services.add_message(conn, booking["id"], user["id"], "[Hệ thống] Người thuê đã hủy đơn.")
    services.notify(f"❌ Đơn bị hủy · {code}", [f"{booking['title']}", f"Hoàn cho khách: {vnd(refund)}"])
    flash(request, f"Đã hủy đơn. Số tiền hoàn dự kiến: {vnd(refund)}.")
    return redirect(f"/trips/{code}")


@router.post("/trips/{code}/review")
async def trip_review(code: str, request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    user, booking, role = _load_for_party(request, conn, code)
    form = await security.form_with_csrf(request)
    if role != "renter" or booking["effective_status"] != "completed":
        flash(request, "Bạn chỉ có thể đánh giá sau khi đã trả máy.", "error")
        return redirect(f"/trips/{code}")
    if conn.execute("SELECT 1 FROM reviews WHERE booking_id = ?", (booking["id"],)).fetchone():
        flash(request, "Bạn đã đánh giá đơn này rồi.", "error")
        return redirect(f"/trips/{code}")

    def score(name: str) -> int:
        try:
            return min(5, max(1, int(form.get(name) or 5)))
        except ValueError:
            return 5

    comment = (form.get("comment") or "").strip()
    if len(comment) < 10:
        flash(request, "Hãy viết vài dòng nhận xét (ít nhất 10 ký tự) để giúp người thuê sau.", "error")
        return redirect(f"/trips/{code}#review")
    conn.execute(
        """INSERT INTO reviews (booking_id, listing_id, author_id, rating, r_condition, r_accuracy, r_communication,
               r_handover, r_value, comment, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (booking["id"], booking["listing_id"], user["id"], score("rating"), score("r_condition"), score("r_accuracy"),
         score("r_communication"), score("r_handover"), score("r_value"), comment[:2000], db.now_iso()),
    )
    flash(request, "Cảm ơn bạn đã đánh giá!")
    return redirect(f"/trips/{code}")

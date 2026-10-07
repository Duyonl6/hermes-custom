"""Hồ sơ cá nhân & danh sách yêu thích."""
from __future__ import annotations

import re
import sqlite3

from fastapi import APIRouter, Depends, Request

from .. import db, security
from ..meta import CITIES
from ..web import flash, gallery, redirect, render, require_user

router = APIRouter()


@router.get("/wishlist")
def wishlist(request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    user = require_user(request, conn)
    items = [db.listing_dict(r) for r in conn.execute(
        db.LISTING_SELECT + " JOIN wishlist w ON w.listing_id = l.id WHERE w.user_id = ? ORDER BY w.created_at DESC",
        (user["id"],),
    )]
    photos = db.photos_for(conn, [i["id"] for i in items])
    for i in items:
        i["images"] = gallery(i, photos.get(i["id"], []), 5)
    return render(request, conn, "account/wishlist.html", items=items)


@router.get("/account")
def account(request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    require_user(request, conn)
    return render(request, conn, "account/profile.html", cities_list=CITIES, errors=[])


@router.post("/account")
async def update_account(request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    user = require_user(request, conn)
    form = await security.form_with_csrf(request)
    name = (form.get("name") or "").strip()[:60]
    phone = (form.get("phone") or "").replace(" ", "")[:15]
    errors = []
    if len(name) < 2:
        errors.append("Vui lòng nhập họ tên.")
    if phone and not re.fullmatch(r"(\+?84|0)\d{9,10}", phone):
        errors.append("Số điện thoại không hợp lệ.")
    new_pw = form.get("new_password") or ""
    if new_pw:
        if not security.verify_password(form.get("current_password") or "", user["password_hash"]):
            errors.append("Mật khẩu hiện tại không đúng.")
        elif len(new_pw) < 8:
            errors.append("Mật khẩu mới cần ít nhất 8 ký tự.")
    if errors:
        return render(request, conn, "account/profile.html", status_code=400, cities_list=CITIES, errors=errors)
    conn.execute(
        "UPDATE users SET name = ?, phone = ?, bio = ?, city = ? WHERE id = ?",
        (name, phone, (form.get("bio") or "").strip()[:600], form.get("city") if form.get("city") in CITIES else "", user["id"]),
    )
    if new_pw:
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (security.hash_password(new_pw), user["id"]))
    flash(request, "Đã cập nhật hồ sơ.")
    return redirect("/account")

"""Đăng ký / đăng nhập / đăng xuất."""
from __future__ import annotations

import random
import re
import sqlite3

from fastapi import APIRouter, Depends, Request

from .. import db, security
from ..web import current_user, flash, redirect, render, safe_next

router = APIRouter()
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@router.get("/login")
def login_form(request: Request, next: str = "/", conn: sqlite3.Connection = Depends(db.get_db)):
    if current_user(request, conn):
        return redirect(safe_next(next))
    return render(request, conn, "login.html", next=safe_next(next), email="")


@router.post("/login")
async def login(request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    form = await security.form_with_csrf(request)
    email = (form.get("email") or "").strip().lower()
    nxt = safe_next(form.get("next"))
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if not row or not security.verify_password(form.get("password") or "", row["password_hash"]):
        return render(request, conn, "login.html", status_code=400, next=nxt, email=email,
                      error="Email hoặc mật khẩu không đúng.")
    request.session.clear()
    request.session["uid"] = row["id"]
    flash(request, f"Chào mừng trở lại, {row['name']}!")
    return redirect(nxt)


@router.get("/register")
def register_form(request: Request, next: str = "/", conn: sqlite3.Connection = Depends(db.get_db)):
    if current_user(request, conn):
        return redirect(safe_next(next))
    return render(request, conn, "register.html", next=safe_next(next), form={})


@router.post("/register")
async def register(request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    form = await security.form_with_csrf(request)
    data = {k: (form.get(k) or "").strip() for k in ("name", "email", "phone", "password", "city")}
    data["email"] = data["email"].lower()
    nxt = safe_next(form.get("next"))
    errors = []
    if len(data["name"]) < 2:
        errors.append("Vui lòng nhập họ tên.")
    if not EMAIL_RE.match(data["email"]):
        errors.append("Email không hợp lệ.")
    if len(data["password"]) < 8:
        errors.append("Mật khẩu cần ít nhất 8 ký tự.")
    if data["phone"] and not re.fullmatch(r"(\+?84|0)\d{9,10}", data["phone"].replace(" ", "")):
        errors.append("Số điện thoại không hợp lệ.")
    if not errors and conn.execute("SELECT 1 FROM users WHERE email = ?", (data["email"],)).fetchone():
        errors.append("Email này đã được đăng ký — hãy đăng nhập.")
    if errors:
        return render(request, conn, "register.html", status_code=400, next=nxt, form=data, errors=errors)
    cur = conn.execute(
        "INSERT INTO users (email, password_hash, name, phone, city, avatar_hue, is_host, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (data["email"], security.hash_password(data["password"]), data["name"], data["phone"].replace(" ", ""),
         data["city"], random.randint(0, 359), int(form.get("as_host") == "1"), db.now_iso()),
    )
    request.session.clear()
    request.session["uid"] = cur.lastrowid
    flash(request, "Tạo tài khoản thành công! Chúc bạn có những chuyến đi nhiều ảnh đẹp.")
    return redirect("/host" if form.get("as_host") == "1" else nxt)


@router.post("/logout")
async def logout(request: Request):
    await security.form_with_csrf(request)
    request.session.clear()
    return redirect("/")

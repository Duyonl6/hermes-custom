"""Băm mật khẩu (PBKDF2, stdlib) và chống CSRF bằng token trong session."""
from __future__ import annotations

import hashlib
import hmac
import secrets

from fastapi import HTTPException, Request

_ITERATIONS = 240_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _ITERATIONS).hex()
    return f"pbkdf2_sha256${_ITERATIONS}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, iterations, salt, digest = stored.split("$")
    except ValueError:
        return False
    if algo != "pbkdf2_sha256":
        return False
    calc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iterations)).hex()
    return hmac.compare_digest(calc, digest)


def csrf_token(request: Request) -> str:
    token = request.session.get("csrf")
    if not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf"] = token
    return token


def check_csrf(request: Request, submitted: str | None) -> None:
    expected = request.session.get("csrf")
    if not expected or not submitted or not hmac.compare_digest(expected, submitted):
        raise HTTPException(status_code=403, detail="Phiên làm việc hết hạn, vui lòng tải lại trang và thử lại.")


async def form_with_csrf(request: Request):
    """Đọc form và kiểm tra CSRF trong một bước — dùng cho mọi POST từ HTML form."""
    form = await request.form()
    check_csrf(request, form.get("csrf"))
    return form

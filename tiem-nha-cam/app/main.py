"""Điểm vào ứng dụng Tiệm nhà Cam — marketplace thuê máy ảnh, action cam, flycam kiểu Airbnb.

Chạy dev:   uvicorn app.main:app --reload --port 8010
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from . import config, db
from .routes import account, auth, bookings, host, pages
from .web import LoginRequired, NotHost, login_redirect, render

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("tiemnhacam")


def _startup() -> None:
    conn = db.connect()
    try:
        db.init_db(conn)
        if config.AUTO_SEED:
            from seed.seed import seed

            if seed(conn):
                log.info("Đã tạo dữ liệu demo (AUTO_SEED=1). Tắt bằng AUTO_SEED=0 khi chạy thật.")
        db.expire_stale_pending(conn)
    finally:
        conn.close()
    if config.SECRET_KEY.startswith("dev-"):
        log.warning("SECRET_KEY đang dùng giá trị mặc định — hãy đặt SECRET_KEY trong .env trước khi public!")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _startup()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=config.SITE_NAME, docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
    app.add_middleware(
        SessionMiddleware,
        secret_key=config.SECRET_KEY,
        session_cookie="tnc_session",
        max_age=60 * 60 * 24 * 30,
        same_site="lax",
        https_only=config.SESSION_HTTPS_ONLY,
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response

    config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(config.BASE_DIR / "static")), name="static")
    app.mount("/uploads", StaticFiles(directory=str(config.UPLOAD_DIR)), name="uploads")
    for module in (pages, auth, bookings, host, account):
        app.include_router(module.router)

    @app.exception_handler(LoginRequired)
    async def _login_required(request: Request, exc: LoginRequired):
        return login_redirect(request)

    @app.exception_handler(NotHost)
    async def _not_host(request: Request, exc: NotHost):
        return RedirectResponse("/host", status_code=303)

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(request: Request, exc: StarletteHTTPException):
        if request.url.path.startswith("/api/"):
            return JSONResponse({"error": exc.detail}, status_code=exc.status_code)
        conn = db.connect()
        try:
            title = {404: "Không tìm thấy trang", 403: "Không có quyền truy cập"}.get(exc.status_code, "Đã có lỗi xảy ra")
            return render(request, conn, "error.html", status_code=exc.status_code, code=exc.status_code, title=title,
                          message=exc.detail if isinstance(exc.detail, str) else "")
        finally:
            conn.close()

    return app


app = create_app()

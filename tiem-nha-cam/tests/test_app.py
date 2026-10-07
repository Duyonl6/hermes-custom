import io
import re
from datetime import timedelta

from app import config, db
from app.db import unaccent

from .conftest import csrf_of, login


def _free_range(conn, listing_id, days=2, offset=20):
    start = config.today() + timedelta(days=offset)
    while not db.is_available(conn, listing_id, start, start + timedelta(days=days)):
        start += timedelta(days=1)
    return start, start + timedelta(days=days)


def _listing(conn, instant: bool, exclude_host: str = "cam@demo.vn"):
    row = conn.execute(
        """SELECT l.id FROM listings l JOIN users u ON u.id = l.host_id
           WHERE l.instant_book = ? AND u.email != ? AND l.active = 1 ORDER BY l.id LIMIT 1""",
        (int(instant), exclude_host),
    ).fetchone()
    return row[0]


# ------------------------------------------------------------------ pages

def test_public_pages(client):
    for url in ["/", "/help", "/login", "/register", "/listing/1", "/users/1", "/sitemap.xml", "/robots.txt", "/healthz"]:
        assert client.get(url).status_code == 200, url
    assert client.get("/listing/99999").status_code == 404
    r = client.get("/art.svg?a=drone:dji:grey&p=2&v=3")
    assert r.headers["content-type"].startswith("image/svg+xml") and r.text.startswith("<svg")


def test_unaccent():
    assert unaccent("Phường Hà Đông, Hà Nội") == "phuong ha dong, ha noi"


def test_search_filters(client, conn):
    data = client.get("/api/listings", params={"category": "drone"}).json()
    expected = conn.execute("SELECT COUNT(*) FROM listings WHERE category = 'drone' AND active = 1").fetchone()[0]
    assert data["total"] == expected > 0
    # tìm không dấu
    data = client.get("/api/listings", params={"q": "ha dong"}).json()
    assert data["total"] > 0 and all("Hà Đông" in i["place"] for i in data["items"])
    # lọc giá
    data = client.get("/api/listings", params={"max_price": 200000}).json()
    assert data["total"] > 0
    assert all(i["price"] <= 200_000 for i in data["items"])


def test_search_excludes_booked_listings(client, conn):
    lid = _listing(conn, instant=True)
    booked = conn.execute(
        "SELECT start_date, end_date FROM bookings WHERE listing_id = ? AND status = 'confirmed' AND start_date > ?",
        (lid, config.today().isoformat()),
    ).fetchone()
    if booked:
        ids = [i["id"] for i in client.get("/api/listings", params={"start": booked[0], "end": booked[1]}).json()["items"]]
        assert lid not in ids


def test_protected_routes_redirect_to_login(client):
    for url in ["/trips", "/wishlist", "/account", "/host", "/book/1?start=2030-01-01&end=2030-01-02"]:
        r = client.get(url, follow_redirects=False)
        assert r.status_code == 303 and r.headers["location"].startswith("/login"), url


# ------------------------------------------------------------------- auth

def test_csrf_required(client):
    r = client.post("/login", data={"email": "khach@demo.vn", "password": "demo1234"})
    assert r.status_code == 403


def test_login_wrong_password(client):
    token = csrf_of(client.get("/login").text)
    r = client.post("/login", data={"email": "khach@demo.vn", "password": "sai-mat-khau", "csrf": token})
    assert r.status_code == 400 and "không đúng" in r.text


def test_register_and_duplicate(client):
    token = csrf_of(client.get("/register").text)
    form = {"name": "Người Mới", "email": "moi@example.com", "password": "matkhau123", "csrf": token}
    r = client.post("/register", data=form, follow_redirects=False)
    assert r.status_code == 303
    client.cookies.clear()
    token = csrf_of(client.get("/register").text)
    r = client.post("/register", data={**form, "csrf": token})
    assert r.status_code == 400 and "đã được đăng ký" in r.text


# ---------------------------------------------------------------- booking

def test_instant_booking_flow_and_double_booking(client, conn):
    lid = _listing(conn, instant=True)
    start, end = _free_range(conn, lid)
    token = login(client, "khach@demo.vn")
    r = client.get(f"/book/{lid}", params={"start": start.isoformat(), "end": end.isoformat()})
    assert r.status_code == 200 and "Xác nhận và thanh toán" in r.text
    r = client.post(f"/book/{lid}", data={"csrf": token, "start": start.isoformat(), "end": end.isoformat(),
                                          "phone": "0912345678", "agree_id": "1", "agree_rules": "1",
                                          "payment_method": "transfer"}, follow_redirects=False)
    assert r.status_code == 303
    code = r.headers["location"].rsplit("/", 1)[-1]
    booking = conn.execute("SELECT * FROM bookings WHERE code = ?", (code,)).fetchone()
    assert booking["status"] == "confirmed" and booking["start_date"] == start.isoformat()
    page = client.get(f"/trips/{code}").text
    assert "img.vietqr.io" in page and code in page
    # Ngày đã bị khóa trong lịch
    assert start.isoformat() in db.blocked_dates(conn, lid)

    # Người khác đặt trùng → bị từ chối
    client.cookies.clear()
    token2 = login(client, "renter2@demo.vn")
    r = client.post(f"/book/{lid}", data={"csrf": token2, "start": start.isoformat(), "end": end.isoformat(),
                                          "phone": "0911111111", "agree_id": "1", "agree_rules": "1"})
    assert r.status_code == 400 and "có người đặt" in r.text


def test_booking_requires_agreements(client, conn):
    lid = _listing(conn, instant=True)
    start, end = _free_range(conn, lid, offset=40)
    token = login(client, "khach@demo.vn")
    r = client.post(f"/book/{lid}", data={"csrf": token, "start": start.isoformat(), "end": end.isoformat(), "phone": "0912345678"})
    assert r.status_code == 400 and "CCCD" in r.text


def test_request_to_book_then_host_accepts(client, conn):
    lid = _listing(conn, instant=False)
    host_email = conn.execute("SELECT u.email FROM listings l JOIN users u ON u.id = l.host_id WHERE l.id = ?", (lid,)).fetchone()[0]
    start, end = _free_range(conn, lid, offset=30)
    token = login(client, "renter3@demo.vn")
    base = {"csrf": token, "start": start.isoformat(), "end": end.isoformat(), "phone": "0912000000", "agree_id": "1", "agree_rules": "1"}
    r = client.post(f"/book/{lid}", data=base)
    assert r.status_code == 400 and "lời nhắn" in r.text  # cần lời nhắn khi chủ thuê duyệt
    r = client.post(f"/book/{lid}", data={**base, "message": "Mình thuê để quay phóng sự tốt nghiệp ạ."}, follow_redirects=False)
    code = r.headers["location"].rsplit("/", 1)[-1]
    assert conn.execute("SELECT status FROM bookings WHERE code = ?", (code,)).fetchone()[0] == "pending"

    client.cookies.clear()
    token = login(client, host_email)
    assert code in client.get("/host").text
    r = client.post(f"/host/bookings/{code}/accept", data={"csrf": token}, follow_redirects=False)
    assert r.status_code == 303
    assert conn.execute("SELECT status FROM bookings WHERE code = ?", (code,)).fetchone()[0] == "confirmed"


def test_renter_cancel_gets_refund(client, conn):
    lid = _listing(conn, instant=True)
    start, end = _free_range(conn, lid, offset=50)
    token = login(client, "renter4@demo.vn")
    r = client.post(f"/book/{lid}", data={"csrf": token, "start": start.isoformat(), "end": end.isoformat(),
                                          "phone": "0913000000", "agree_id": "1", "agree_rules": "1"}, follow_redirects=False)
    code = r.headers["location"].rsplit("/", 1)[-1]
    r = client.post(f"/trips/{code}/cancel", data={"csrf": token}, follow_redirects=False)
    assert r.status_code == 303
    row = conn.execute("SELECT status, refund, total FROM bookings WHERE code = ?", (code,)).fetchone()
    assert row["status"] == "cancelled" and 0 < row["refund"] <= row["total"]
    # Ngày được mở lại sau khi hủy
    assert db.is_available(conn, lid, start, end)


def test_cannot_book_own_listing(client, conn):
    lid = conn.execute("SELECT l.id FROM listings l JOIN users u ON u.id = l.host_id WHERE u.email = 'cam@demo.vn' LIMIT 1").fetchone()[0]
    start, end = _free_range(conn, lid, offset=60)
    login(client, "cam@demo.vn")
    r = client.get(f"/book/{lid}", params={"start": start.isoformat(), "end": end.isoformat()}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"].startswith(f"/listing/{lid}")


def test_other_user_cannot_view_booking(client, conn):
    code = conn.execute("SELECT code FROM bookings b JOIN users u ON u.id = b.renter_id WHERE u.email = 'khach@demo.vn' LIMIT 1").fetchone()[0]
    login(client, "renter9@demo.vn")
    assert client.get(f"/trips/{code}").status_code == 404


# --------------------------------------------------------------- wishlist

def test_wishlist_toggle(client):
    assert client.post("/api/wishlist/1").status_code == 401
    token = login(client, "khach@demo.vn")
    assert client.post("/api/wishlist/1").status_code == 403  # thiếu header CSRF
    r1 = client.post("/api/wishlist/1", headers={"X-CSRF-Token": token}).json()
    r2 = client.post("/api/wishlist/1", headers={"X-CSRF-Token": token}).json()
    assert r1["saved"] != r2["saved"]


# ------------------------------------------------------------------- host

def test_host_creates_listing_with_photo(client, conn):
    from PIL import Image

    token = login(client, "cam@demo.vn")
    buf = io.BytesIO()
    Image.new("RGB", (640, 480), (255, 120, 40)).save(buf, "PNG")
    form = {
        "csrf": token, "title": "Sony A6400 + lens kit — máy cho người mới", "category": "mirrorless", "brand": "Sony",
        "model": "Alpha A6400", "description": "Máy còn đẹp 98%, đã vệ sinh cảm biến, kèm 2 pin và thẻ nhớ 64GB.",
        "price_day": "250.000", "deposit": "3.000.000", "discount_3d": "10", "discount_7d": "20", "city": "Hà Nội",
        "ward": "Phường Cầu Giấy", "lat": "21.033", "lng": "105.793", "instant_book": "1", "min_days": "1",
        "condition": "Như mới", "cancellation": "flexible", "specs_text": "Cảm biến: APS-C 24MP\nVideo: 4K 30p",
        "included_text": "Body\n2 pin",
    }
    r = client.post("/host/listings/new", data=form, files={"photos": ("a.png", buf.getvalue(), "image/png")}, follow_redirects=False)
    assert r.status_code == 303
    lid = int(re.search(r"/listing/(\d+)", r.headers["location"]).group(1))
    listing = db.get_listing(conn, lid)
    assert listing["price_day"] == 250_000 and listing["art"] == "mirrorless:sony:black"
    assert listing["specs"][0] == ["Cảm biến", "APS-C 24MP"]
    photos = db.listing_photos(conn, lid)
    assert len(photos) == 1 and (config.UPLOAD_DIR / photos[0]).exists()
    assert f"/uploads/{photos[0]}" in client.get(f"/listing/{lid}").text

    # khóa lịch → ngày bị chặn
    start, end = _free_range(conn, lid, offset=10)
    r = client.post(f"/host/listings/{lid}/blocks", data={"csrf": token, "start": start.isoformat(), "end": end.isoformat()}, follow_redirects=False)
    assert r.status_code == 303 and not db.is_available(conn, lid, start, end)


def test_host_validation_and_ownership(client, conn):
    token = login(client, "cam@demo.vn")
    r = client.post("/host/listings/new", data={"csrf": token, "title": "ngắn"})
    assert r.status_code == 400 and "Tiêu đề" in r.text
    other = conn.execute("SELECT l.id FROM listings l JOIN users u ON u.id = l.host_id WHERE u.email != 'cam@demo.vn' LIMIT 1").fetchone()[0]
    assert client.get(f"/host/listings/{other}/edit").status_code == 404


def test_rejects_non_image_upload(client, conn):
    token = login(client, "cam@demo.vn")
    lid = conn.execute("SELECT l.id FROM listings l JOIN users u ON u.id = l.host_id WHERE u.email = 'cam@demo.vn' LIMIT 1").fetchone()[0]
    before = len(db.listing_photos(conn, lid))
    listing = db.get_listing(conn, lid)
    form = {"csrf": token, "title": listing["title"], "category": listing["category"], "brand": listing["brand"],
            "model": listing["model"], "description": listing["description"], "price_day": str(listing["price_day"]),
            "deposit": str(listing["deposit"]), "city": listing["city"], "ward": listing["ward"], "lat": str(listing["lat"]),
            "lng": str(listing["lng"]), "min_days": "1", "discount_3d": "10", "discount_7d": "20"}
    r = client.post(f"/host/listings/{lid}/edit", data=form, files={"photos": ("x.png", b"<?php echo 1; ?>", "image/png")}, follow_redirects=True)
    assert r.status_code == 200 and "không phải ảnh" in r.text
    assert len(db.listing_photos(conn, lid)) == before

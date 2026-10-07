"""Trang công khai: khám phá/tìm kiếm, chi tiết thiết bị, hồ sơ chủ thuê, trợ giúp, ảnh SVG, API bản đồ."""
from __future__ import annotations

import json
import sqlite3
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, PlainTextResponse, Response

from .. import config, db, illustrations, pricing, search, security
from ..meta import CATEGORY_LABELS
from ..web import art_url, current_user, gallery, not_found, render

router = APIRouter()

REVIEW_CATEGORIES = [
    ("r_condition", "Tình trạng máy", "condition"),
    ("r_accuracy", "Đúng mô tả", "accuracy"),
    ("r_communication", "Giao tiếp", "chat"),
    ("r_handover", "Giao nhận", "handover"),
    ("r_value", "Đáng tiền", "value"),
]


def _with_photos(conn: sqlite3.Connection, items: list[dict], count: int = 5) -> list[dict]:
    photos = db.photos_for(conn, [i["id"] for i in items])
    for item in items:
        item["images"] = gallery(item, photos.get(item["id"], []), count)
    return items


@router.get("/")
def home(request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    f = search.resolve_query(conn, search.Filters.from_params(request.query_params))
    items, total = search.search(conn, f)
    _with_photos(conn, items)
    pages = max(1, -(-total // search.PAGE_SIZE))
    base_args = f.query_args()
    return render(
        request, conn, "index.html",
        f=f, items=items, total=total, page=f.page, pages=pages,
        sorts=search.SORTS,
        histogram=search.price_histogram(conn, f),
        brands=search.brand_facets(conn, f),
        city_counts=search.city_counts(conn),
        qs=urlencode(base_args),
        next_qs=urlencode(f.query_args(page=f.page + 1)) if f.page < pages else "",
        prev_qs=urlencode(f.query_args(page=f.page - 1)) if f.page > 1 else "",
        clear_qs=urlencode(f.query_args(min_price=None, max_price=None, instant="", delivery="", superhost="",
                                        top_rated="", sort="", brand_list=[])),
        cat_qs={key: urlencode(f.query_args(category=key, page="")) for key in CATEGORY_LABELS} | {"": urlencode(f.query_args(category="", page=""))},
    )


@router.get("/api/listings")
def api_listings(request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    f = search.resolve_query(conn, search.Filters.from_params(request.query_params))
    items, total = search.search(conn, f, limit=300, offset=0)
    return {
        "total": total,
        "items": [
            {
                "id": i["id"], "title": i["title"], "price": i["price_day"], "lat": i["lat"], "lng": i["lng"],
                "rating": i["rating_avg"], "reviews": i["rating_count"], "place": f"{i['ward']}, {i['city']}",
                "img": art_url(i["art"], i["id"], 0), "url": f"/listing/{i['id']}",
            }
            for i in items
        ],
    }


@router.get("/listing/{listing_id}")
def listing_detail(listing_id: int, request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    listing = db.get_listing(conn, listing_id)
    user = current_user(request, conn)
    if not listing or (not listing["active"] and not (user and user["id"] == listing["host_id"])):
        raise not_found("Tin đăng không tồn tại hoặc đã ngưng cho thuê.")
    photos = db.listing_photos(conn, listing_id)
    images = gallery(listing, photos, 5)
    host = dict(conn.execute("SELECT * FROM users WHERE id = ?", (listing["host_id"],)).fetchone())
    host_stats = conn.execute(
        """SELECT COUNT(DISTINCT l.id) AS listings, COUNT(r.id) AS reviews, COALESCE(AVG(r.rating), 0) AS rating
           FROM listings l LEFT JOIN reviews r ON r.listing_id = l.id WHERE l.host_id = ? AND l.active = 1""",
        (host["id"],),
    ).fetchone()
    reviews = [dict(r) for r in conn.execute(
        """SELECT rv.*, u.name AS author_name, u.avatar_hue AS author_hue, u.city AS author_city
           FROM reviews rv JOIN users u ON u.id = rv.author_id WHERE rv.listing_id = ?
           ORDER BY rv.created_at DESC LIMIT 60""",
        (listing_id,),
    )]
    cat_scores = []
    if reviews:
        row = conn.execute(
            "SELECT " + ", ".join(f"AVG({c})" for c, _, _ in REVIEW_CATEGORIES) + " FROM reviews WHERE listing_id = ?",
            (listing_id,),
        ).fetchone()
        cat_scores = [(label, icon, round(row[i], 1)) for i, (_, label, icon) in enumerate(REVIEW_CATEGORIES)]
    star_dist = {s: 0 for s in range(5, 0, -1)}
    for r in reviews:
        star_dist[r["rating"]] += 1

    similar, _ = search.search(conn, search.Filters(category=listing["category"], sort="rating"), limit=9, offset=0)
    similar = _with_photos(conn, [s for s in similar if s["id"] != listing_id][:8], 3)

    booking_cfg = {
        "id": listing["id"],
        "priceDay": listing["price_day"],
        "discount3d": listing["discount_3d"],
        "discount7d": listing["discount_7d"],
        "servicePct": config.SERVICE_FEE_PCT,
        "deliveryFee": listing["delivery_fee"] if listing["delivery"] else 0,
        "deposit": listing["deposit"],
        "minDays": listing["min_days"],
        "blocked": db.blocked_dates(conn, listing_id),
        "today": config.today().isoformat(),
    }
    q = request.query_params
    return render(
        request, conn, "listing.html",
        listing=listing, images=images, host=host, host_stats=dict(host_stats), reviews=reviews,
        cat_scores=cat_scores, star_dist=star_dist, similar=similar,
        booking_json=json.dumps(booking_cfg), policy=pricing.CANCELLATION_POLICIES[listing["cancellation"]],
        is_owner=bool(user and user["id"] == listing["host_id"]),
        pre_start=q.get("start", ""), pre_end=q.get("end", ""),
        drone_exempt=listing["category"] == "drone" and 0 < listing["weight_g"] < 250,
    )


@router.get("/users/{user_id}")
def user_profile(user_id: int, request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        raise not_found("Không tìm thấy người dùng.")
    profile = dict(row)
    listings = [db.listing_dict(r) for r in conn.execute(
        db.LISTING_SELECT + " WHERE l.host_id = ? AND l.active = 1 ORDER BY l.created_at DESC", (user_id,))]
    _with_photos(conn, listings)
    reviews = [dict(r) for r in conn.execute(
        """SELECT rv.*, u.name AS author_name, u.avatar_hue AS author_hue, l.title AS listing_title, l.id AS lid
           FROM reviews rv JOIN users u ON u.id = rv.author_id JOIN listings l ON l.id = rv.listing_id
           WHERE l.host_id = ? ORDER BY rv.created_at DESC LIMIT 8""",
        (user_id,),
    )]
    stats = conn.execute(
        "SELECT COUNT(*), COALESCE(AVG(rating), 0) FROM reviews rv JOIN listings l ON l.id = rv.listing_id WHERE l.host_id = ?",
        (user_id,),
    ).fetchone()
    rentals = conn.execute(
        "SELECT COUNT(*) FROM bookings b JOIN listings l ON l.id = b.listing_id WHERE l.host_id = ? AND b.status = 'confirmed'",
        (user_id,),
    ).fetchone()[0]
    return render(request, conn, "user.html", profile=profile, listings=listings, reviews=reviews,
                  review_count=stats[0], review_avg=round(stats[1], 2), rentals=rentals)


@router.get("/help")
def help_page(request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    from seed.catalog import PRODUCTS  # bảng giá tham khảo dùng để seed — hiển thị minh bạch nguồn

    price_refs = sorted(
        ({"name": f"{p['brand']} {p['model']}", "category": CATEGORY_LABELS[p["category"]], "low": p["rent_ref"][0],
          "high": p["rent_ref"][1], "src": p["rent_src"], "retail": p["retail"]} for p in PRODUCTS.values()),
        key=lambda x: (x["category"], x["name"]),
    )
    return render(request, conn, "help.html", price_refs=price_refs)


@router.post("/api/wishlist/{listing_id}")
def toggle_wishlist(listing_id: int, request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    user = current_user(request, conn)
    if not user:
        return JSONResponse({"error": "login", "url": f"/login?next=/listing/{listing_id}"}, status_code=401)
    security.check_csrf(request, request.headers.get("X-CSRF-Token"))
    if not conn.execute("SELECT 1 FROM listings WHERE id = ?", (listing_id,)).fetchone():
        return JSONResponse({"error": "not_found"}, status_code=404)
    exists = conn.execute("SELECT 1 FROM wishlist WHERE user_id = ? AND listing_id = ?", (user["id"], listing_id)).fetchone()
    if exists:
        conn.execute("DELETE FROM wishlist WHERE user_id = ? AND listing_id = ?", (user["id"], listing_id))
    else:
        conn.execute("INSERT INTO wishlist (user_id, listing_id, created_at) VALUES (?,?,?)", (user["id"], listing_id, db.now_iso()))
    return {"saved": not exists}


@router.get("/art.svg")
def art(a: str = "mirrorless:generic:black", p: int = 0, v: int = 0):
    svg = illustrations.render(a[:60], p, v)
    return Response(svg, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=604800"})


@router.get("/healthz")
def healthz(conn: sqlite3.Connection = Depends(db.get_db)):
    conn.execute("SELECT 1").fetchone()
    return {"ok": True}


@router.get("/robots.txt", response_class=PlainTextResponse)
def robots():
    return f"User-agent: *\nDisallow: /host\nDisallow: /trips\nDisallow: /account\nSitemap: {config.SITE_URL}/sitemap.xml\n"


@router.get("/sitemap.xml")
def sitemap(conn: sqlite3.Connection = Depends(db.get_db)):
    urls = [f"{config.SITE_URL}/", f"{config.SITE_URL}/help"] + [
        f"{config.SITE_URL}/listing/{r[0]}" for r in conn.execute("SELECT id FROM listings WHERE active = 1")
    ]
    body = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + \
        "".join(f"<url><loc>{u}</loc></url>" for u in urls) + "</urlset>"
    return Response(body, media_type="application/xml")

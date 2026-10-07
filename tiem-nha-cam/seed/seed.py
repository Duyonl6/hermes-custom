"""Tạo dữ liệu demo: chủ thuê, người thuê, 50+ tin đăng, đánh giá, lịch đã đặt.

Chạy:  python -m seed.seed           (bỏ qua nếu DB đã có dữ liệu)
       python -m seed.seed --reset   (xóa DB cũ và seed lại)

Mọi ngày tháng được tính tương đối so với hôm nay để lịch luôn "sống".
"""
from __future__ import annotations

import json
import random
import sys
from datetime import date, datetime, time, timedelta

from app import config, db, security, services
from seed.catalog import (HOSTS, INCLUDED, LISTINGS, LOCATIONS, PRODUCTS, RENTERS, REVIEW_CLOSERS, REVIEW_OPENERS,
                          REVIEW_SNIPPETS)

DEMO_PASSWORD = "demo1234"
SNIPPET_GROUP = {"mirrorless": "camera", "dslr": "camera", "compact": "camera", "film": "camera",
                 "action": "action", "cam360": "action", "drone": "drone", "vlog": "vlog", "lens": "lens"}


def _ts(d: date, hour: int = 10) -> str:
    return datetime.combine(d, time(hour, 0), tzinfo=config.TZ).isoformat()


def _deposit(rng: random.Random, product: dict) -> int:
    cat, retail = product["category"], product["retail"]
    if cat in {"action", "cam360", "vlog"}:
        return rng.choice([1_000_000, 2_000_000, 3_000_000])
    if cat == "film":
        return rng.choice([1_000_000, 1_500_000, 2_000_000])
    pct = rng.choice([0.3, 0.4, 0.5])
    return max(1_000_000, int(retail * pct / 500_000) * 500_000)


def _description(product: dict, host: dict, kit: str, city: str) -> str:
    parts = [product["blurb"]]
    if kit:
        parts.append(f"Bộ cho thuê: {kit}.")
    parts.append(f"Nhận máy tại {city} — {host['name']} kiểm tra máy cùng bạn khi bàn giao, có biên bản ghi rõ tình trạng.")
    if product["category"] == "drone":
        parts.append("Lưu ý: bạn tự chịu trách nhiệm tuân thủ quy định bay (khu vực cấm bay, xin phép với máy từ 250 g trở lên). "
                     "Chủ thuê sẽ hướng dẫn kiểm tra vùng bay trước khi giao máy.")
    return "\n\n".join(parts)


def seed(conn, reset: bool = False) -> bool:
    db.init_db(conn)
    if not reset and conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
        return False
    pw = security.hash_password(DEMO_PASSWORD)  # dùng chung 1 hash cho user demo để seed nhanh
    rng = random.Random(2026)
    today = config.today()

    # Khóa ghi rồi kiểm tra lại: chạy nhiều worker uvicorn thì chỉ một tiến trình được seed
    conn.execute("BEGIN IMMEDIATE")
    if reset:
        for table in ("messages", "reviews", "wishlist", "blocks", "bookings", "listing_photos", "listings", "users"):
            conn.execute(f"DELETE FROM {table}")
    elif conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
        conn.execute("ROLLBACK")
        return False
    host_ids: dict[str, int] = {}
    for i, h in enumerate(HOSTS):
        city = LOCATIONS[h["loc"]][0]
        cur = conn.execute(
            """INSERT INTO users (email, password_hash, name, phone, bio, city, avatar_hue, is_host, id_verified, superhost,
                                  response_minutes, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (h["email"], pw, h["name"], f"09{rng.randint(10_000_000, 99_999_999)}", h["bio"], city, (i * 47) % 360, 1,
             h["verified"], h["superhost"], h["response"], _ts(today - timedelta(days=rng.randint(200, 1400)))),
        )
        host_ids[h["key"]] = cur.lastrowid

    renter_ids = []
    for i, name in enumerate(RENTERS):
        cur = conn.execute(
            "INSERT INTO users (email, password_hash, name, city, avatar_hue, id_verified, created_at) VALUES (?,?,?,?,?,?,?)",
            (f"renter{i + 1}@demo.vn", pw, name, rng.choice(["Hà Nội", "TP. Hồ Chí Minh", "Đà Nẵng"]), (i * 31 + 13) % 360,
             rng.random() > .3, _ts(today - timedelta(days=rng.randint(30, 900)))),
        )
        renter_ids.append(cur.lastrowid)
    demo_renter = conn.execute(
        "INSERT INTO users (email, password_hash, name, phone, city, avatar_hue, id_verified, created_at) VALUES (?,?,?,?,?,?,?,?)",
        ("khach@demo.vn", pw, "Khách Demo", "0912345678", "Hà Nội", 200, 1, _ts(today - timedelta(days=120))),
    ).lastrowid

    listing_rows: list[dict] = []
    for idx, (hkey, pkey, lkey, price, title, kit, instant, delivery, dfee, condition) in enumerate(LISTINGS):
        p = PRODUCTS[pkey]
        host = next(h for h in HOSTS if h["key"] == hkey)
        city, ward, lat, lng = LOCATIONS[lkey]
        d3, d7 = rng.choice([(10, 20), (10, 20), (5, 15), (15, 25)])
        cancellation = rng.choice(["flexible", "flexible", "moderate", "strict"]) if p["category"] != "drone" else rng.choice(["moderate", "strict"])
        included = list(INCLUDED[p["category"]])
        if kit:
            included.insert(1, kit)
        cur = conn.execute(
            """INSERT INTO listings (host_id, title, category, brand, model, kit, description, price_day, discount_3d,
                   discount_7d, deposit, retail_value, city, ward, lat, lng, instant_book, delivery, delivery_fee, min_days,
                   condition, weight_g, specs, included, cancellation, art, active, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1,?)""",
            (host_ids[hkey], title, p["category"], p["brand"], p["model"], kit, _description(p, host, kit, f"{ward}, {city}"),
             price, d3, d7, _deposit(rng, p), p["retail"], city, ward,
             round(lat + rng.uniform(-.006, .006), 5), round(lng + rng.uniform(-.006, .006), 5),
             instant, delivery, dfee, 1, condition, p["weight"], json.dumps(p["specs"], ensure_ascii=False),
             json.dumps(included, ensure_ascii=False), cancellation, p["art"],
             _ts(today - timedelta(days=rng.randint(40, 700)))),
        )
        listing_rows.append(dict(id=cur.lastrowid, host_id=host_ids[hkey], category=p["category"]))

    # Đánh giá demo (không gắn đơn) — phân bố lệch về 5★ như thực tế các sàn
    for lst in listing_rows:
        n = rng.choice([0, 3, 5, 8, 12, 16, 22, 30]) if lst["id"] % 7 else rng.randint(9, 34)
        group = SNIPPET_GROUP[lst["category"]]
        authors = rng.sample(renter_ids, k=min(n, len(renter_ids)))
        for author in authors:
            overall = rng.choices([5, 4, 3], weights=[78, 19, 3])[0]
            sub = [min(5, max(1, overall + rng.choice([0, 0, 0, -1, 1]))) for _ in range(5)]
            parts = [rng.choice(REVIEW_OPENERS), *rng.sample(REVIEW_SNIPPETS["common"], rng.choice([1, 1, 2])),
                     *rng.sample(REVIEW_SNIPPETS[group], 1)]
            if overall < 5:
                parts.append(rng.choice(["Hơi tiếc là pin dự phòng bị chai nhẹ.", "Túi đựng hơi cũ một chút.",
                                         "Giao máy trễ khoảng 15 phút.", "Thẻ nhớ đi kèm hơi chậm."]))
            parts.append(rng.choice(REVIEW_CLOSERS))
            text = " ".join(p for p in parts if p)
            conn.execute(
                """INSERT INTO reviews (listing_id, author_id, rating, r_condition, r_accuracy, r_communication, r_handover,
                       r_value, comment, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (lst["id"], author, overall, *sub, text, _ts(today - timedelta(days=rng.randint(5, 330)), rng.randint(8, 21))),
            )
    conn.execute("COMMIT")

    # Lịch đã đặt của người khác → để lịch có ngày bị khóa
    for lst in listing_rows:
        listing = db.get_listing(conn, lst["id"])
        for _ in range(rng.randint(0, 3)):
            start = today + timedelta(days=rng.randint(1, 50))
            end = start + timedelta(days=rng.randint(1, 5))
            if db.is_available(conn, lst["id"], start, end):
                services.create_booking(conn, listing, rng.choice(renter_ids), start, end, status="confirmed",
                                        payment_method=rng.choice(["transfer", "cash"]))

    # Kịch bản cho tài khoản demo
    cam_host = host_ids["tiemnhacam"]
    cam_listings = [l for l in listing_rows if l["host_id"] == cam_host]
    other = [l for l in listing_rows if l["host_id"] != cam_host]

    def _book(listing_id, renter, start, days, status, msg="", created=None, allow_past=False):
        listing = db.get_listing(conn, listing_id)
        s = today + timedelta(days=start)
        # Trùng lịch với đơn seed ngẫu nhiên → lùi dần tới khi trống (giữ nguyên chiều quá khứ/tương lai)
        step = -1 if start < 0 else 1
        for _ in range(30):
            if db.is_available(conn, listing_id, s, s + timedelta(days=days)):
                break
            s += timedelta(days=step)
        else:
            return None
        if start >= 0 and s <= today:
            return None
        e = s + timedelta(days=days)
        return services.create_booking(conn, listing, renter, s, e, status=status, message=msg, allow_past=allow_past,
                                       created_at=created, payment_method="transfer")

    # Khách demo: 1 đơn đã hoàn tất (chưa đánh giá), 1 đơn sắp tới, 1 đơn chờ duyệt
    done = _book(other[3]["id"], demo_renter, -9, 3, "confirmed", "Mình nhận máy buổi sáng được không ạ?",
                 created=_ts(today - timedelta(days=14)), allow_past=True)
    if done:
        services.add_message(conn, done["id"], other[3]["host_id"], "Được bạn nhé, 8h sáng mình có mặt ở tiệm.")
    _book(other[0]["id"], demo_renter, 6, 2, "confirmed", "Cho mình xin thêm 1 thẻ nhớ dự phòng nha.")
    _book(other[11]["id"], demo_renter, 12, 3, "pending", "Mình bay ở Ba Vì, cần tư vấn thêm về vùng bay ạ.")

    # Chủ thuê demo (Tiệm nhà Cam): 2 yêu cầu chờ duyệt + 1 đơn đang thuê + lịch sử doanh thu
    _book(cam_listings[4]["id"], renter_ids[0], 4, 2, "pending", "Chào tiệm, cuối tuần này mình đi Tam Đảo, máy còn không ạ?")
    _book(cam_listings[0]["id"], renter_ids[1], 9, 3, "pending", "Mình muốn thuê X100VI chụp kỷ yếu lớp ạ.")
    _book(cam_listings[2]["id"], renter_ids[2], -1, 3, "confirmed", "", created=_ts(today - timedelta(days=5)), allow_past=True)
    for k in range(6):
        lst = rng.choice(cam_listings)
        _book(lst["id"], rng.choice(renter_ids), -rng.randint(15, 80), rng.randint(1, 4), "confirmed",
              created=_ts(today - timedelta(days=90)), allow_past=True)
    return True


def main() -> None:
    reset = "--reset" in sys.argv
    if reset and config.DB_PATH.exists():
        for suffix in ("", "-wal", "-shm"):
            p = config.DB_PATH.with_name(config.DB_PATH.name + suffix)
            if p.exists():
                p.unlink()
    conn = db.connect()
    created = seed(conn)
    counts = {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("users", "listings", "reviews", "bookings")}
    conn.close()
    print(("Đã seed dữ liệu demo: " if created else "DB đã có dữ liệu, bỏ qua seed: ") + str(counts))
    if created:
        print(f"Tài khoản demo — khách: khach@demo.vn / {DEMO_PASSWORD} · chủ thuê: cam@demo.vn / {DEMO_PASSWORD}")


if __name__ == "__main__":
    main()

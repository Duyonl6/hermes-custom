"""Tìm kiếm & lọc tin đăng (dùng cho trang chủ, API bản đồ)."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import date

from . import db
from .meta import CATEGORY_LABELS, CITIES

SORTS = {
    "recommended": "Gợi ý",
    "price_asc": "Giá thấp → cao",
    "price_desc": "Giá cao → thấp",
    "rating": "Đánh giá cao nhất",
    "newest": "Mới đăng",
}
_ORDER = {
    "recommended": "(COALESCE(r.rating_avg, 4.6) * 2 + MIN(COALESCE(r.rating_count, 0), 30) / 10.0 "
                   "+ u.superhost * 0.6 + l.instant_book * 0.3) DESC, l.id",
    "price_asc": "l.price_day ASC, l.id",
    "price_desc": "l.price_day DESC, l.id",
    "rating": "COALESCE(r.rating_avg, 0) DESC, COALESCE(r.rating_count, 0) DESC, l.id",
    "newest": "l.created_at DESC, l.id",
}
PAGE_SIZE = 24
_TEXT = "l.title || ' ' || l.brand || ' ' || l.model || ' ' || l.kit || ' ' || l.ward || ' ' || l.city"


def _int(value, default=None):
    try:
        return int(str(value).replace(".", "").replace(",", "").strip())
    except (TypeError, ValueError):
        return default


def _date(value) -> date | None:
    try:
        return date.fromisoformat(str(value)) if value else None
    except ValueError:
        return None


@dataclass
class Filters:
    q: str = ""
    city: str = ""
    category: str = ""
    start: date | None = None
    end: date | None = None
    min_price: int | None = None
    max_price: int | None = None
    brands: list[str] = field(default_factory=list)
    instant: bool = False
    delivery: bool = False
    superhost: bool = False
    top_rated: bool = False
    sort: str = "recommended"
    page: int = 1
    q_phrase: bool = False  # True → khớp nguyên cụm từ (xem resolve_query)

    @classmethod
    def from_params(cls, params) -> "Filters":
        start, end = _date(params.get("start")), _date(params.get("end"))
        if start and end and end <= start:
            start = end = None
        sort = params.get("sort", "recommended")
        return cls(
            q=(params.get("q") or "").strip()[:80],
            city=params.get("city") if params.get("city") in CITIES else "",
            category=params.get("category") if params.get("category") in CATEGORY_LABELS else "",
            start=start,
            end=end if start else None,
            min_price=_int(params.get("min_price")),
            max_price=_int(params.get("max_price")),
            brands=[b for b in params.getlist("brand") if b][:10] if hasattr(params, "getlist") else [],
            instant=params.get("instant") == "1",
            delivery=params.get("delivery") == "1",
            superhost=params.get("superhost") == "1",
            top_rated=params.get("top_rated") == "1",
            sort=sort if sort in SORTS else "recommended",
            page=max(1, _int(params.get("page"), 1) or 1),
        )

    @property
    def active_count(self) -> int:
        """Số bộ lọc nâng cao đang bật (hiện badge trên nút Bộ lọc)."""
        return sum([
            self.min_price is not None or self.max_price is not None,
            bool(self.brands), self.instant, self.delivery, self.superhost, self.top_rated,
            self.sort != "recommended",
        ])

    def query_args(self, **override) -> list[tuple[str, str]]:
        data = {
            "q": self.q, "city": self.city, "category": self.category,
            "start": self.start.isoformat() if self.start else "", "end": self.end.isoformat() if self.end else "",
            "min_price": self.min_price, "max_price": self.max_price,
            "instant": "1" if self.instant else "", "delivery": "1" if self.delivery else "",
            "superhost": "1" if self.superhost else "", "top_rated": "1" if self.top_rated else "",
            "sort": "" if self.sort == "recommended" else self.sort,
        }
        data.update(override)
        out = [(k, str(v)) for k, v in data.items() if v not in ("", None)]
        out += [("brand", b) for b in (override.get("brand_list", self.brands))]
        return [(k, v) for k, v in out if k != "brand_list"]


def resolve_query(conn: sqlite3.Connection, f: Filters) -> Filters:
    """Ưu tiên khớp nguyên cụm ("ha dong" → Phường Hà Đông, không lẫn "Đống Đa, Hà Nội");
    không có kết quả mới tách từng từ (cho phép gõ "a7 sony")."""
    phrase = " ".join(db.unaccent(f.q).split())
    if phrase and " " in phrase:
        hit = conn.execute(f"SELECT 1 FROM listings l WHERE l.active = 1 AND unaccent({_TEXT}) LIKE ? LIMIT 1", (f"%{phrase}%",)).fetchone()
        f.q_phrase = bool(hit)
    return f


def _where(f: Filters, *, with_price: bool = True, with_category: bool = True) -> tuple[str, list]:
    clauses, args = ["l.active = 1"], []
    if f.q:
        tokens = [" ".join(db.unaccent(f.q).split())] if f.q_phrase else db.unaccent(f.q).split()
        for token in tokens:
            clauses.append(f"unaccent({_TEXT}) LIKE ?")
            args.append(f"%{token}%")
    if f.city:
        clauses.append("l.city = ?")
        args.append(f.city)
    if f.category and with_category:
        clauses.append("l.category = ?")
        args.append(f.category)
    if f.start and f.end:
        clauses.append(
            f"""NOT EXISTS (SELECT 1 FROM bookings b WHERE b.listing_id = l.id
                    AND b.status IN ({",".join("?" * len(db.HOLDING_STATUSES))})
                    AND b.start_date < ? AND b.end_date > ?)
                AND NOT EXISTS (SELECT 1 FROM blocks k WHERE k.listing_id = l.id AND k.start_date < ? AND k.end_date > ?)
                AND l.min_days <= ?"""
        )
        args += [*db.HOLDING_STATUSES, f.end.isoformat(), f.start.isoformat(), f.end.isoformat(), f.start.isoformat(),
                 (f.end - f.start).days]
    if with_price and f.min_price is not None:
        clauses.append("l.price_day >= ?")
        args.append(f.min_price)
    if with_price and f.max_price is not None:
        clauses.append("l.price_day <= ?")
        args.append(f.max_price)
    if f.brands:
        clauses.append(f"l.brand IN ({','.join('?' * len(f.brands))})")
        args += f.brands
    if f.instant:
        clauses.append("l.instant_book = 1")
    if f.delivery:
        clauses.append("l.delivery = 1")
    if f.superhost:
        clauses.append("u.superhost = 1")
    if f.top_rated:
        clauses.append("COALESCE(r.rating_avg, 0) >= 4.8 AND COALESCE(r.rating_count, 0) >= 3")
    return " WHERE " + " AND ".join(clauses), args


def search(conn: sqlite3.Connection, f: Filters, limit: int = PAGE_SIZE, offset: int | None = None) -> tuple[list[dict], int]:
    where, args = _where(f)
    total = conn.execute(f"SELECT COUNT(*) FROM listings l JOIN users u ON u.id = l.host_id {db.RATING_JOIN} {where}", args).fetchone()[0]
    offset = (f.page - 1) * limit if offset is None else offset
    rows = conn.execute(f"{db.LISTING_SELECT} {where} ORDER BY {_ORDER[f.sort]} LIMIT ? OFFSET ?", [*args, limit, offset]).fetchall()
    return [db.listing_dict(r) for r in rows], total


def price_histogram(conn: sqlite3.Connection, f: Filters, bins: int = 24) -> dict:
    """Biểu đồ phân bố giá (giống bộ lọc giá Airbnb) — tính trên tập kết quả, bỏ qua bộ lọc giá."""
    where, args = _where(f, with_price=False)
    prices = [r[0] for r in conn.execute(
        f"SELECT l.price_day FROM listings l JOIN users u ON u.id = l.host_id {db.RATING_JOIN} {where}", args)]
    top = max(prices or [1_000_000])
    step = max(50_000, -(-top // bins // 50_000) * 50_000)
    counts = [0] * bins
    for p in prices:
        counts[min(bins - 1, p // step)] += 1
    peak = max(counts) or 1
    return {"step": step, "max": step * bins, "bars": [round(c / peak * 100) for c in counts]}


def brand_facets(conn: sqlite3.Connection, f: Filters) -> list[tuple[str, int]]:
    where, args = _where(Filters(q=f.q, city=f.city, category=f.category, start=f.start, end=f.end, q_phrase=f.q_phrase))
    rows = conn.execute(
        f"SELECT l.brand, COUNT(*) FROM listings l JOIN users u ON u.id = l.host_id {db.RATING_JOIN} {where} "
        "GROUP BY l.brand ORDER BY COUNT(*) DESC, l.brand",
        args,
    ).fetchall()
    return [(r[0], r[1]) for r in rows]


def city_counts(conn: sqlite3.Connection) -> dict[str, int]:
    return {r[0]: r[1] for r in conn.execute("SELECT city, COUNT(*) FROM listings WHERE active = 1 GROUP BY city")}

"""Tính giá thuê — logic duy nhất, phía JS (listing.js) dùng cùng công thức để hiển thị tức thì.

Quy ước theo thực tế các shop cho thuê ở VN:
- 1 ngày thuê = 24h kể từ lúc nhận máy; ngày trả = ngày nhận + số ngày.
- Thuê dài được giảm: từ 3 ngày giảm `discount_3d`%, từ 7 ngày giảm `discount_7d`%.
- Tiền cọc thu khi nhận máy và hoàn lại khi trả máy nguyên vẹn (không tính vào tổng thanh toán).
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from datetime import date

from . import config

CANCELLATION_POLICIES = {
    "flexible": {
        "name": "Linh hoạt",
        "summary": "Hủy miễn phí trước ngày nhận máy 1 ngày.",
        "detail": "Hoàn 100% nếu hủy trước ngày nhận máy ít nhất 1 ngày. Hủy trong ngày nhận máy: hoàn 50%.",
    },
    "moderate": {
        "name": "Trung bình",
        "summary": "Hủy miễn phí trước ngày nhận máy 3 ngày.",
        "detail": "Hoàn 100% nếu hủy trước ngày nhận máy ít nhất 3 ngày; sau đó hoàn 50%.",
    },
    "strict": {
        "name": "Nghiêm ngặt",
        "summary": "Hoàn 50% nếu hủy trước ngày nhận máy 7 ngày.",
        "detail": "Hoàn 50% nếu hủy trước ngày nhận máy ít nhất 7 ngày; sau đó không hoàn tiền thuê.",
    },
}


def round_k(value: float) -> int:
    """Làm tròn tới 1.000₫ kiểu half-up (khớp Math.round bên JS, tránh banker's rounding của round())."""
    return int(math.floor(value / 1000.0 + 0.5)) * 1000


@dataclass
class Quote:
    days: int
    price_day: int
    subtotal: int
    discount_pct: int
    discount: int
    service_fee: int
    delivery_fee: int
    total: int
    deposit: int
    host_payout: int

    def as_dict(self) -> dict:
        return asdict(self)


def discount_pct_for(days: int, discount_3d: int, discount_7d: int) -> int:
    if days >= 7:
        return discount_7d
    if days >= 3:
        return discount_3d
    return 0


def quote(listing: dict, start: date, end: date, delivery: bool = False) -> Quote:
    days = (end - start).days
    if days < 1:
        raise ValueError("Ngày trả phải sau ngày nhận ít nhất 1 ngày.")
    price_day = int(listing["price_day"])
    subtotal = price_day * days
    pct = discount_pct_for(days, int(listing["discount_3d"]), int(listing["discount_7d"]))
    discount = round_k(subtotal * pct / 100)
    rent = subtotal - discount
    service_fee = round_k(rent * config.SERVICE_FEE_PCT / 100)
    delivery_fee = int(listing["delivery_fee"]) if (delivery and listing["delivery"]) else 0
    host_payout = rent - round_k(rent * config.HOST_FEE_PCT / 100) + delivery_fee
    return Quote(
        days=days,
        price_day=price_day,
        subtotal=subtotal,
        discount_pct=pct,
        discount=discount,
        service_fee=service_fee,
        delivery_fee=delivery_fee,
        total=rent + service_fee + delivery_fee,
        deposit=int(listing["deposit"]),
        host_payout=host_payout,
    )


def refund_amount(booking: dict, policy: str, cancel_day: date) -> int:
    """Số tiền hoàn khi người thuê hủy đơn (phí dịch vụ không hoàn trừ khi hoàn 100%)."""
    if booking["status"] == "pending":
        return booking["total"]  # chưa được xác nhận → hoàn toàn bộ
    start = date.fromisoformat(booking["start_date"])
    days_before = (start - cancel_day).days
    rent_part = booking["total"] - booking["service_fee"]
    if policy == "flexible":
        if days_before >= 1:
            return booking["total"]
        return round_k(rent_part * 0.5) if days_before == 0 else 0
    if policy == "moderate":
        if days_before >= 3:
            return booking["total"]
        return round_k(rent_part * 0.5) if days_before >= 0 else 0
    # strict
    if days_before >= 7:
        return round_k(rent_part * 0.5)
    return 0

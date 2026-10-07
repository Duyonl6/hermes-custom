from datetime import date

import pytest

from app import pricing

LISTING = {"price_day": 600_000, "discount_3d": 10, "discount_7d": 20, "delivery": 1, "delivery_fee": 40_000, "deposit": 14_000_000}


def test_quote_one_day_no_discount():
    q = pricing.quote(LISTING, date(2026, 11, 2), date(2026, 11, 3))
    assert q.days == 1
    assert q.discount == 0
    assert q.service_fee == 48_000  # 8% của 600k
    assert q.total == 648_000
    assert q.deposit == 14_000_000


def test_quote_three_days_discount_and_delivery():
    q = pricing.quote(LISTING, date(2026, 11, 2), date(2026, 11, 5), delivery=True)
    assert q.days == 3 and q.subtotal == 1_800_000
    assert q.discount_pct == 10 and q.discount == 180_000
    assert q.service_fee == 130_000  # 8% × 1.620.000 = 129.600 → làm tròn 130.000
    assert q.delivery_fee == 40_000
    assert q.total == 1_620_000 + 130_000 + 40_000
    assert q.host_payout == 1_620_000 - 49_000 + 40_000  # trừ phí host 3%


def test_quote_week_discount():
    q = pricing.quote(LISTING, date(2026, 11, 2), date(2026, 11, 9))
    assert q.discount_pct == 20 and q.discount == 840_000


def test_delivery_ignored_when_listing_has_no_delivery():
    q = pricing.quote({**LISTING, "delivery": 0}, date(2026, 11, 2), date(2026, 11, 3), delivery=True)
    assert q.delivery_fee == 0


def test_quote_rejects_same_day():
    with pytest.raises(ValueError):
        pricing.quote(LISTING, date(2026, 11, 2), date(2026, 11, 2))


def test_round_half_up_matches_js():
    assert pricing.round_k(114_500) == 115_000  # round() của Python sẽ ra 114.000 (banker's rounding)
    assert pricing.round_k(115_499) == 115_000


@pytest.mark.parametrize("policy,days_before,expected", [
    ("flexible", 1, 1_000_000), ("flexible", 0, 460_000), ("flexible", -1, 0),
    ("moderate", 3, 1_000_000), ("moderate", 2, 460_000),
    ("strict", 7, 460_000), ("strict", 6, 0),
])
def test_refund_policies(policy, days_before, expected):
    booking = {"status": "confirmed", "start_date": "2026-11-10", "total": 1_000_000, "service_fee": 80_000}
    cancel_day = date(2026, 11, 10 - days_before)
    assert pricing.refund_amount(booking, policy, cancel_day) == expected


def test_pending_booking_always_full_refund():
    booking = {"status": "pending", "start_date": "2026-11-10", "total": 1_000_000, "service_fee": 80_000}
    assert pricing.refund_amount(booking, "strict", date(2026, 11, 10)) == 1_000_000

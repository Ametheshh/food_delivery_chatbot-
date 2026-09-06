"""Coupon / offer helpers backed by in-memory mock data."""

from __future__ import annotations

from typing import Any

from chatbot.data.coupons import COUPONS


class CouponService:
    """Read-only access to predefined coupons."""

    @staticmethod
    def get_all() -> list[dict[str, Any]]:
        return COUPONS

    @staticmethod
    def format_coupons() -> str:
        lines = ["🎉 Here are some available offers:"]
        for coupon in COUPONS:
            code = coupon["code"]
            description = coupon["description"]
            max_discount = coupon["max_discount"]
            if code == "FREEDEL":
                lines.append(f"{code}")
                lines.append(f"{description}.")
            else:
                lines.append(f"{code}")
                lines.append(f"{description}, up to ₹{max_discount}")
        return "\n".join(lines)

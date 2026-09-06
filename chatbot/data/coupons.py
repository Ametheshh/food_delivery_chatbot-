"""Predefined coupons / offers for the food delivery chatbot."""

COUPONS = [
    {
        "code": "WELCOME50",
        "description": "50% off for new users",
        "max_discount": 100,
    },
    {
        "code": "FOOD20",
        "description": "20% off on orders above ₹500",
        "max_discount": 150,
    },
    {
        "code": "FREEDEL",
        "description": "Free delivery on orders above ₹299",
        "max_discount": 50,
    },
    {
        "code": "WEEKEND15",
        "description": "15% off on weekend orders",
        "max_discount": 120,
    },
]

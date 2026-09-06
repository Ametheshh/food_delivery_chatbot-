"""Predefined mock orders for the food delivery chatbot."""

ORDERS = {
    "123": {
        "status": "Out for Delivery",
        "restaurant": "Pizza Palace",
        "items": ["Margherita Pizza", "Garlic Bread"],
        "estimated_delivery": "20 minutes",
    },
    "456": {
        "status": "Preparing",
        "restaurant": "Burger House",
        "items": ["Cheese Burger", "French Fries"],
        "estimated_delivery": "35 minutes",
    },
    "789": {
        "status": "Delivered",
        "restaurant": "Indian Spice",
        "items": ["Butter Chicken", "Naan"],
        "estimated_delivery": "Delivered",
    },
    "101": {
        "status": "Order Confirmed",
        "restaurant": "Sushi Central",
        "items": ["Salmon Roll", "Miso Soup"],
        "estimated_delivery": "45 minutes",
    },
    "202": {
        "status": "Delayed",
        "restaurant": "Taco Town",
        "items": ["Chicken Tacos", "Guacamole"],
        "estimated_delivery": "55 minutes",
    },
    "303": {
        "status": "Ready for Pickup",
        "restaurant": "Pasta Place",
        "items": ["Penne Arrabbiata", "Tiramisu"],
        "estimated_delivery": "Ready now",
    },
    "404": {
        "status": "Cancelled",
        "restaurant": "Salad Spot",
        "items": ["Caesar Salad", "Iced Tea"],
        "estimated_delivery": "Cancelled",
    },
}

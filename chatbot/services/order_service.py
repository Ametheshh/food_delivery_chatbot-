"""Order lookup helpers backed by in-memory mock data."""

from __future__ import annotations

from typing import Any

from chatbot.data.orders import ORDERS


class OrderService:
    """Read-only access to predefined orders."""

    @staticmethod
    def get_all() -> dict[str, dict[str, Any]]:
        return ORDERS

    @staticmethod
    def get_order(order_id: str) -> dict[str, Any] | None:
        return ORDERS.get(str(order_id))

    @staticmethod
    def format_order_status(order_id: str, order: dict[str, Any]) -> str:
        items = ", ".join(order["items"])
        return (
            f"Your order #{order_id} is currently {order['status']}.\n"
            f"Restaurant: {order['restaurant']}\n"
            f"Items: {items}\n"
            f"Estimated delivery: {order['estimated_delivery']}"
        )

    @staticmethod
    def not_found_message(order_id: str) -> str:
        return (
            f"I couldn't find order #{order_id}.\n"
            "Please check the order ID and try again."
        )

    @staticmethod
    def missing_id_message() -> str:
        return (
            "Sure! Please provide your order ID so I can check the status.\n"
            'For example: "Where is my order 123?"'
        )

"""In-memory support ticket storage."""

from __future__ import annotations

from typing import Any


TICKETS: list[dict[str, Any]] = []
_NEXT_TICKET_NUMBER = 1001

PRIORITY_BY_SENTIMENT = {
    "ANGRY": "HIGH",
    "NEGATIVE": "MEDIUM",
    "NEUTRAL": "LOW",
    "POSITIVE": "LOW",
}

ISSUE_LABELS = {
    "DELIVERY_DELAY": "Delivery delay",
    "ORDER_NOT_READY": "Order preparation delay",
    "COMPLAINT": "Service complaint",
    "ORDER_ISSUE": "Order problem",
}


class TicketService:
    """Create and list support tickets stored in memory."""

    @classmethod
    def reset(cls) -> None:
        """Clear tickets — used by tests."""
        global _NEXT_TICKET_NUMBER
        TICKETS.clear()
        _NEXT_TICKET_NUMBER = 1001

    @classmethod
    def get_all(cls) -> list[dict[str, Any]]:
        return list(TICKETS)

    @classmethod
    def create_ticket(
        cls,
        *,
        order_id: str | None,
        issue_type: str,
        description: str,
        sentiment: str,
    ) -> dict[str, Any]:
        global _NEXT_TICKET_NUMBER
        ticket_id = f"TKT-{_NEXT_TICKET_NUMBER}"
        _NEXT_TICKET_NUMBER += 1

        priority = PRIORITY_BY_SENTIMENT.get(sentiment.upper(), "LOW")
        ticket = {
            "ticket_id": ticket_id,
            "order_id": order_id or "",
            "issue_type": issue_type,
            "description": description,
            "sentiment": sentiment.upper(),
            "priority": priority,
            "status": "OPEN",
        }
        TICKETS.append(ticket)
        return ticket

    @staticmethod
    def issue_label(issue_type: str) -> str:
        return ISSUE_LABELS.get(issue_type, "Support issue")

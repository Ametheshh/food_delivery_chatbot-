"""Intent detection and response generation for the chatbot."""

from __future__ import annotations

import re
from typing import Any

from chatbot.services.coupon_service import CouponService
from chatbot.services.order_service import OrderService
from chatbot.services.sentiment_service import SentimentService
from chatbot.services.ticket_service import TicketService


ORDER_STATUS = "ORDER_STATUS"
COUPON = "COUPON"
COMPLAINT = "COMPLAINT"
DELIVERY_ISSUE = "DELIVERY_ISSUE"
ORDER_NOT_READY = "ORDER_NOT_READY"
GENERAL_QUERY = "GENERAL_QUERY"
UNKNOWN = "UNKNOWN"

ORDER_ID_PATTERN = re.compile(
    r"(?:order\s*(?:id\s*)?|#)\s*(\d+)|(?:\b(?:track|check|status)\b.*?\b)(\d+)\b|\b(\d{2,})\b",
    re.IGNORECASE,
)

COUPON_KEYWORDS = (
    "coupon",
    "coupons",
    "discount",
    "discounts",
    "offer",
    "offers",
    "promo",
    "promocode",
    "deal",
    "deals",
)

ORDER_KEYWORDS = (
    "order",
    "track",
    "status",
    "where is",
    "where's",
    "delivery status",
)

DELIVERY_ISSUE_KEYWORDS = (
    "hasn't arrived",
    "has not arrived",
    "not arrived",
    "very late",
    "extremely late",
    "too late",
    "hours late",
    "late and",
    " is late",
    "food is late",
    "order is late",
    "still waiting",
    "waiting forever",
    "delayed",
    "delay",
    "food hasn't",
    "food has not",
    "where's my food",
    "where is my food",
    "cold",
)

ORDER_NOT_READY_KEYWORDS = (
    "not ready",
    "still not ready",
    "hasn't prepared",
    "has not prepared",
    "haven't prepared",
    "restaurant hasn't",
    "preparation",
    "still preparing",
)

COMPLAINT_KEYWORDS = (
    "complain",
    "complaint",
    "problem",
    "issue",
    "wrong order",
    "order is wrong",
    "missing",
    "hate",
    "terrible",
    "awful",
    "ridiculous",
    "unhappy",
    "frustrated",
    "angry",
    "furious",
    "unacceptable",
    "refund",
)

GREETING_KEYWORDS = (
    "hello",
    "hi",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
    "thanks",
    "thank you",
    "help",
)


class ChatbotService:
    """Orchestrates intent detection, sentiment, and response building."""

    def __init__(
        self,
        sentiment_service: SentimentService | None = None,
    ) -> None:
        self.sentiment_service = sentiment_service or SentimentService()
        self.order_service = OrderService()
        self.coupon_service = CouponService()
        self.ticket_service = TicketService()

    def process_message(self, message: str | None) -> dict[str, Any]:
        if message is None or not str(message).strip():
            return {
                "message": "Please enter a message so I can help you.",
                "intent": UNKNOWN,
                "sentiment": "NEUTRAL",
                "ticket_created": False,
            }

        text = str(message).strip()
        sentiment_result = self.sentiment_service.analyze(text)
        sentiment = sentiment_result["sentiment"]
        intent = self.detect_intent(text)
        order_id = self.extract_order_id(text)

        if intent == ORDER_STATUS:
            return self._handle_order_status(order_id, sentiment)

        if intent == COUPON:
            return {
                "message": self.coupon_service.format_coupons(),
                "intent": COUPON,
                "sentiment": sentiment,
                "ticket_created": False,
            }

        if intent in {DELIVERY_ISSUE, ORDER_NOT_READY, COMPLAINT}:
            return self._handle_issue(text, intent, order_id, sentiment)

        if intent == GENERAL_QUERY:
            return {
                "message": (
                    "Hi! 👋 How can I help you today?\n"
                    "I can help with order tracking, coupons, and delivery issues."
                ),
                "intent": GENERAL_QUERY,
                "sentiment": sentiment,
                "ticket_created": False,
            }

        return {
            "message": (
                "I'm sorry, I didn't quite understand that.\n"
                "I can help you with:\n"
                "• Order tracking\n"
                "• Coupons and offers\n"
                "• Delivery issues\n"
                "• Order complaints"
            ),
            "intent": UNKNOWN,
            "sentiment": sentiment,
            "ticket_created": False,
        }

    def detect_intent(self, message: str) -> str:
        lower = message.lower()

        if any(keyword in lower for keyword in ORDER_NOT_READY_KEYWORDS):
            return ORDER_NOT_READY

        if any(keyword in lower for keyword in DELIVERY_ISSUE_KEYWORDS):
            return DELIVERY_ISSUE

        if any(keyword in lower for keyword in COMPLAINT_KEYWORDS):
            return COMPLAINT

        if any(keyword in lower for keyword in COUPON_KEYWORDS):
            return COUPON

        if any(keyword in lower for keyword in ORDER_KEYWORDS) or self.extract_order_id(
            message
        ):
            return ORDER_STATUS

        if any(keyword in lower for keyword in GREETING_KEYWORDS):
            return GENERAL_QUERY

        return UNKNOWN

    def extract_order_id(self, message: str) -> str | None:
        match = ORDER_ID_PATTERN.search(message)
        if not match:
            return None
        for group in match.groups():
            if group:
                return group
        return None

    def _handle_order_status(
        self,
        order_id: str | None,
        sentiment: str,
    ) -> dict[str, Any]:
        if not order_id:
            return {
                "message": self.order_service.missing_id_message(),
                "intent": ORDER_STATUS,
                "sentiment": sentiment,
                "ticket_created": False,
            }

        order = self.order_service.get_order(order_id)
        if not order:
            return {
                "message": self.order_service.not_found_message(order_id),
                "intent": ORDER_STATUS,
                "sentiment": sentiment,
                "ticket_created": False,
            }

        return {
            "message": self.order_service.format_order_status(order_id, order),
            "intent": ORDER_STATUS,
            "sentiment": sentiment,
            "ticket_created": False,
        }

    def _handle_issue(
        self,
        message: str,
        intent: str,
        order_id: str | None,
        sentiment: str,
    ) -> dict[str, Any]:
        issue_type = {
            DELIVERY_ISSUE: "DELIVERY_DELAY",
            ORDER_NOT_READY: "ORDER_NOT_READY",
            COMPLAINT: "COMPLAINT",
        }.get(intent, "ORDER_ISSUE")

        ticket = self.ticket_service.create_ticket(
            order_id=order_id,
            issue_type=issue_type,
            description=message,
            sentiment=sentiment,
        )

        apology = self._empathy_line(sentiment)
        issue_label = self.ticket_service.issue_label(issue_type)
        order_line = f"Order: #{order_id}\n" if order_id else ""

        reply = (
            f"{apology}\n"
            f"I've created a support ticket for you.\n"
            f"Ticket ID: {ticket['ticket_id']}\n"
            f"Issue: {issue_label}\n"
            f"{order_line}"
            f"Priority: {ticket['priority']}\n"
            f"Status: Open\n"
            f"Our support team will look into this."
        )

        return {
            "message": reply,
            "intent": intent,
            "sentiment": sentiment,
            "ticket_created": True,
            "ticket_id": ticket["ticket_id"],
        }

    @staticmethod
    def _empathy_line(sentiment: str) -> str:
        if sentiment == "ANGRY":
            return (
                "I'm really sorry about this. I understand how frustrating "
                "it is to wait for an order that hasn't arrived."
            )
        if sentiment == "NEGATIVE":
            return "I'm sorry about the delay. I understand how frustrating that can be."
        return "I'm sorry about the inconvenience."

from django.test import SimpleTestCase, Client, override_settings
from unittest.mock import patch

from chatbot.services.chatbot_service import ChatbotService, COUPON, DELIVERY_ISSUE, ORDER_STATUS
from chatbot.services.sentiment_service import SentimentService
from chatbot.services.ticket_service import TicketService


class ChatbotIntentTests(SimpleTestCase):
    def setUp(self) -> None:
        TicketService.reset()
        self.service = ChatbotService(
            sentiment_service=SentimentService(api_key=""),  # force NEUTRAL fallback
        )

    def test_order_status_intent(self) -> None:
        result = self.service.process_message("Where is order 123?")
        self.assertEqual(result["intent"], ORDER_STATUS)
        self.assertIn("Out for Delivery", result["message"])
        self.assertIn("#123", result["message"])

    def test_unknown_order(self) -> None:
        result = self.service.process_message("Where is order 999?")
        self.assertEqual(result["intent"], ORDER_STATUS)
        self.assertIn("couldn't find order #999", result["message"].lower())

    def test_missing_order_id(self) -> None:
        result = self.service.process_message("Where is my order?")
        self.assertEqual(result["intent"], ORDER_STATUS)
        self.assertIn("provide your order ID", result["message"])

    def test_coupon_intent(self) -> None:
        result = self.service.process_message("Do you have coupons?")
        self.assertEqual(result["intent"], COUPON)
        self.assertIn("WELCOME50", result["message"])

    def test_delivery_issue_creates_ticket(self) -> None:
        result = self.service.process_message("My food is very late")
        self.assertEqual(result["intent"], DELIVERY_ISSUE)
        self.assertTrue(result["ticket_created"])
        self.assertTrue(result["ticket_id"].startswith("TKT-"))
        tickets = TicketService.get_all()
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0]["issue_type"], "DELIVERY_DELAY")

    def test_empty_message(self) -> None:
        result = self.service.process_message("")
        self.assertEqual(result["message"], "Please enter a message so I can help you.")
        self.assertFalse(result["ticket_created"])


class SentimentServiceTests(SimpleTestCase):
    def test_fallback_without_api_key(self) -> None:
        service = SentimentService(api_key="")
        result = service.analyze("This is ridiculous!")
        self.assertEqual(result["sentiment"], "NEUTRAL")
        self.assertEqual(result["source"], "fallback")

    @patch("chatbot.services.sentiment_service.requests.post")
    def test_positive_sentiment(self, mock_post) -> None:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"sentiment": "POSITIVE", "confidence": 0.91}'
                    }
                }
            ]
        }
        mock_post.return_value.raise_for_status = lambda: None
        service = SentimentService(api_key="test-key")
        result = service.analyze("Thanks, the delivery was really fast!")
        self.assertEqual(result["sentiment"], "POSITIVE")

    @patch("chatbot.services.sentiment_service.requests.post")
    def test_neutral_sentiment(self, mock_post) -> None:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [
                {"message": {"content": '{"sentiment": "NEUTRAL", "confidence": 0.8}'}}
            ]
        }
        mock_post.return_value.raise_for_status = lambda: None
        service = SentimentService(api_key="test-key")
        result = service.analyze("Where is my order 123?")
        self.assertEqual(result["sentiment"], "NEUTRAL")

    @patch("chatbot.services.sentiment_service.requests.post")
    def test_negative_sentiment(self, mock_post) -> None:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"sentiment": "NEGATIVE", "confidence": 0.88}'
                    }
                }
            ]
        }
        mock_post.return_value.raise_for_status = lambda: None
        service = SentimentService(api_key="test-key")
        result = service.analyze("I'm unhappy with the service.")
        self.assertEqual(result["sentiment"], "NEGATIVE")

    @patch("chatbot.services.sentiment_service.requests.post")
    def test_angry_sentiment(self, mock_post) -> None:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [
                {"message": {"content": '{"sentiment": "ANGRY", "confidence": 0.94}'}}
            ]
        }
        mock_post.return_value.raise_for_status = lambda: None
        service = SentimentService(api_key="test-key")
        result = service.analyze("My order is extremely late. This is ridiculous!")
        self.assertEqual(result["sentiment"], "ANGRY")

    @patch("chatbot.services.sentiment_service.requests.post")
    def test_api_failure_falls_back(self, mock_post) -> None:
        mock_post.side_effect = Exception("network down")
        service = SentimentService(api_key="test-key")
        result = service.analyze("Anything")
        self.assertEqual(result["sentiment"], "NEUTRAL")
        self.assertEqual(result["source"], "fallback")


class TicketPriorityTests(SimpleTestCase):
    def setUp(self) -> None:
        TicketService.reset()

    def test_angry_is_high_priority(self) -> None:
        ticket = TicketService.create_ticket(
            order_id="123",
            issue_type="DELIVERY_DELAY",
            description="late",
            sentiment="ANGRY",
        )
        self.assertEqual(ticket["priority"], "HIGH")
        self.assertEqual(ticket["ticket_id"], "TKT-1001")


@override_settings(
    NVIDIA_API_KEY="",
)
class APIEndpointTests(SimpleTestCase):
    def setUp(self) -> None:
        TicketService.reset()
        self.client = Client()

    def test_chat_api_order(self) -> None:
        response = self.client.post(
            "/api/chat/",
            data={"message": "Where is order 123?"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["intent"], "ORDER_STATUS")
        self.assertIn("123", payload["message"])

    def test_chat_api_empty(self) -> None:
        response = self.client.post(
            "/api/chat/",
            data={"message": ""},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Please enter a message", response.json()["message"])

    def test_orders_api(self) -> None:
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("123", response.json())

    def test_coupons_api(self) -> None:
        response = self.client.get("/api/coupons/")
        self.assertEqual(response.status_code, 200)
        codes = [c["code"] for c in response.json()]
        self.assertIn("FOOD20", codes)

    def test_tickets_api_after_complaint(self) -> None:
        self.client.post(
            "/api/chat/",
            data={"message": "My food is very late"},
            content_type="application/json",
        )
        response = self.client.get("/api/tickets/")
        self.assertEqual(response.status_code, 200)
        tickets = response.json()
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0]["issue_type"], "DELIVERY_DELAY")

    def test_chat_ui_route_and_template(self) -> None:
        from pathlib import Path

        from django.urls import reverse

        self.assertEqual(reverse("chat-ui"), "/")
        template = (
            Path(__file__).resolve().parents[1]
            / "templates"
            / "chatbot"
            / "index.html"
        )
        self.assertTrue(template.exists())
        self.assertIn("Food Delivery Assistant", template.read_text(encoding="utf-8"))

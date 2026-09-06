"""HTTP views for the chatbot UI and REST API."""

from __future__ import annotations

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render
from django.views import View

from chatbot.services.chatbot_service import ChatbotService
from chatbot.services.coupon_service import CouponService
from chatbot.services.order_service import OrderService
from chatbot.services.ticket_service import TicketService


class ChatPageView(View):
    """Serve the chatbot web UI."""

    def get(self, request):
        return render(request, "chatbot/index.html")


class ChatAPIView(APIView):
    """POST /api/chat/ — process a user message."""

    authentication_classes = []
    permission_classes = []

    def post(self, request: Request) -> Response:
        message = request.data.get("message", "")
        result = ChatbotService().process_message(message)
        return Response(result, status=status.HTTP_200_OK)


class OrdersAPIView(APIView):
    """GET /api/orders/ — list mock orders."""

    authentication_classes = []
    permission_classes = []

    def get(self, request: Request) -> Response:
        return Response(OrderService.get_all())


class CouponsAPIView(APIView):
    """GET /api/coupons/ — list available coupons."""

    authentication_classes = []
    permission_classes = []

    def get(self, request: Request) -> Response:
        return Response(CouponService.get_all())


class TicketsAPIView(APIView):
    """GET /api/tickets/ — list in-memory support tickets."""

    authentication_classes = []
    permission_classes = []

    def get(self, request: Request) -> Response:
        tickets = TicketService.get_all()
        # Return the public ticket shape used in the acceptance criteria.
        payload = [
            {
                "ticket_id": t["ticket_id"],
                "order_id": t["order_id"],
                "issue_type": t["issue_type"],
                "sentiment": t["sentiment"],
                "priority": t["priority"],
                "status": t["status"],
            }
            for t in tickets
        ]
        return Response(payload)

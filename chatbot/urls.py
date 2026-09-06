from django.urls import path

from chatbot.views import (
    ChatAPIView,
    ChatPageView,
    CouponsAPIView,
    OrdersAPIView,
    TicketsAPIView,
)

urlpatterns = [
    path("", ChatPageView.as_view(), name="chat-ui"),
    path("api/chat/", ChatAPIView.as_view(), name="api-chat"),
    path("api/orders/", OrdersAPIView.as_view(), name="api-orders"),
    path("api/coupons/", CouponsAPIView.as_view(), name="api-coupons"),
    path("api/tickets/", TicketsAPIView.as_view(), name="api-tickets"),
]

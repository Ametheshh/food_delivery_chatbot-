# Food Delivery Customer Support Chatbot

A Django-based food delivery customer support chatbot with natural-language intent detection, mock order/coupon data, in-memory support tickets, and NVIDIA AI sentiment analysis.

**No database is used.** Orders, coupons, and tickets live in Python data structures. Tickets are stored in memory and are cleared when the container restarts.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)
- An [NVIDIA API key](https://build.nvidia.com/) (optional — the app falls back to `NEUTRAL` sentiment if the key is missing or the API is unavailable)

---

## Configuration

Copy the example environment file and set your NVIDIA API key:

```shell
cp .env.example .env
```

Edit `.env`:

```env
DEBUG=True
SECRET_KEY=change-me
NVIDIA_API_KEY=your_nvidia_api_key
NVIDIA_MODEL=nvidia/nemotron-3-nano-omni-30b-a3b-reasoning
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

> Never commit `.env` or hardcode the API key in source files.

---

## Run

```shell
docker compose up --build
```

Then open:

```text
http://localhost:8000
```

The container installs dependencies and starts Django automatically. No migrations or database setup are required.

---

## Features

| Feature | Description |
| --- | --- |
| Order tracking | Extract order IDs from natural language and return mock status |
| Coupons | List predefined offers and discount codes |
| Complaints / delivery issues | Create support tickets with unique IDs |
| Sentiment analysis | NVIDIA AI classifies POSITIVE / NEUTRAL / NEGATIVE / ANGRY |
| Ticket priority | ANGRY→HIGH, NEGATIVE→MEDIUM, NEUTRAL/POSITIVE→LOW |

### Sample order IDs

| Order ID | Status |
| --- | --- |
| `123` | Out for Delivery |
| `456` | Preparing |
| `789` | Delivered |
| `101` | Order Confirmed |
| `202` | Delayed |
| `303` | Ready for Pickup |
| `404` | Cancelled |

---

## API Documentation

### `POST /api/chat/`

Process a user message.

**Request**

```json
{
  "message": "Where is my order 123?"
}
```

**Response**

```json
{
  "message": "Your order #123 is currently Out for Delivery.\nRestaurant: Pizza Palace\nItems: Margherita Pizza, Garlic Bread\nEstimated delivery: 20 minutes",
  "intent": "ORDER_STATUS",
  "sentiment": "NEUTRAL",
  "ticket_created": false
}
```

**Issue example**

```json
{
  "message": "I'm really sorry about this...\nI've created a support ticket for you.\nTicket ID: TKT-1001\n...",
  "intent": "DELIVERY_ISSUE",
  "sentiment": "ANGRY",
  "ticket_created": true,
  "ticket_id": "TKT-1001"
}
```

**Empty message**

```json
{
  "message": "Please enter a message so I can help you.",
  "intent": "UNKNOWN",
  "sentiment": "NEUTRAL",
  "ticket_created": false
}
```

### `GET /api/orders/`

Returns all predefined mock orders.

```shell
curl http://localhost:8000/api/orders/
```

### `GET /api/coupons/`

Returns available coupons.

```shell
curl http://localhost:8000/api/coupons/
```

### `GET /api/tickets/`

Returns support tickets created during the current process lifetime.

```shell
curl http://localhost:8000/api/tickets/
```

```json
[
  {
    "ticket_id": "TKT-1001",
    "order_id": "123",
    "issue_type": "DELIVERY_DELAY",
    "sentiment": "ANGRY",
    "priority": "HIGH",
    "status": "OPEN"
  }
]
```

---

## Architecture

```text
User
 ↓
Chat UI (HTML/CSS/JS)
 ↓
Django Chat API  POST /api/chat/
 ↓
Intent Detection (keyword / rule-based)
 ↓
 ├── Order Service
 ├── Coupon Service
 ├── Ticket Service (in-memory)
 └── NVIDIA Sentiment Analysis
 ↓
JSON Response
 ↓
Chat UI
```

Business logic lives under `chatbot/services/`. Views stay thin and only wire HTTP to services.

---

## Project Structure

```text
food_delivery_chatbot/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── README.md
├── chatbot/
│   ├── services/
│   │   ├── chatbot_service.py
│   │   ├── sentiment_service.py
│   │   ├── order_service.py
│   │   ├── coupon_service.py
│   │   └── ticket_service.py
│   ├── data/
│   │   ├── orders.py
│   │   └── coupons.py
│   ├── templates/chatbot/index.html
│   ├── views.py
│   ├── urls.py
│   └── tests/
└── config/
    ├── settings.py
    ├── urls.py
    ├── asgi.py
    └── wsgi.py
```

---

## Testing

Run tests inside the container:

```shell
docker compose run --rm web python manage.py test chatbot.tests -v 2
```

Or locally (with dependencies installed):

```shell
pip install -r requirements.txt
python manage.py test chatbot.tests -v 2
```

Covered cases include order tracking, unknown orders, coupons, delivery complaints (ticket creation), sentiment fallbacks, and empty input handling.

---

## Error Handling

| Situation | Behavior |
| --- | --- |
| NVIDIA API unavailable / invalid key | Log error, use `NEUTRAL`, continue chatting |
| Unknown order ID | Friendly “order not found” message |
| Empty message | Ask the user to enter a message |
| Unrecognized intent | Suggest supported topics |

---

## Notes

- Tickets are **in-memory only** and reset when the container restarts. This is intentional for the demo.
- There is **no database service** in Docker Compose.
- `NVIDIA_API_KEY` must come from the environment — it is never hardcoded in application code.

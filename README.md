# Food Delivery Customer Support Chatbot

A simple customer-support chatbot for a food delivery app. You chat in natural language; the bot tracks mock orders, lists coupons, opens support tickets for complaints, and uses NVIDIA AI to detect sentiment (happy, neutral, upset, angry).

Built with **Python**, **Django**, and **Docker Compose**. There is **no database** — orders, coupons, and tickets live in memory / Python data.

---

## What it does

| You ask about… | Bot does… |
| --- | --- |
| Order status | Looks up a mock order ID and returns status, restaurant, items, ETA |
| Coupons / discounts | Lists available promo codes |
| Late food / problems / complaints | Creates an in-memory support ticket with a priority |
| Greeting / thanks | Replies politely |

Sentiment from NVIDIA sets ticket priority:

- **ANGRY** → HIGH  
- **NEGATIVE** → MEDIUM  
- **NEUTRAL / POSITIVE** → LOW  

If the NVIDIA key is missing or the API fails, sentiment falls back to **NEUTRAL** and chat still works.

---

## What to type in the chat

Open http://localhost:8000 and try these messages.

### Order tracking

Use one of the sample order IDs below.

```text
Where is my order 123?
Can you check order 456?
What is the status of my order 789?
Track order 202
```

### Coupons & offers

```text
Do you have any coupons?
Are there any discounts available?
Show me offers
Any promo codes?
```

### Delivery issues & complaints (creates a ticket)

```text
My order is very late
My food hasn't arrived
I have a problem with my order
I am very unhappy with the service
I am furious! My food is 2 hours late and cold. This is unacceptable!
```

### Greetings

```text
Hi
Hello
Thanks! The food was amazing.
```

### Sample order IDs

| Order ID | Status | Restaurant |
| --- | --- | --- |
| `123` | Out for Delivery | Pizza Palace |
| `456` | Preparing | Burger House |
| `789` | Delivered | Indian Spice |
| `101` | Order Confirmed | Sushi Central |
| `202` | Delayed | Taco Town |
| `303` | Ready for Pickup | Pasta Place |
| `404` | Cancelled | Salad Spot |

### Sample coupons

| Code | Offer |
| --- | --- |
| `WELCOME50` | 50% off for new users (up to ₹100) |
| `FOOD20` | 20% off on orders above ₹500 (up to ₹150) |
| `FREEDEL` | Free delivery on orders above ₹299 |
| `WEEKEND15` | 15% off on weekend orders (up to ₹120) |

---

## How to run

### 1. Clone the repo

```shell
git clone https://github.com/Ametheshh/food_delivery_chatbot-.git
cd food_delivery_chatbot-
```

### 2. Configure environment

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

Get a free API key from [build.nvidia.com](https://build.nvidia.com/). The key is optional — without it, chat still works with `NEUTRAL` sentiment.

> Never commit `.env` or put the API key in source code.

### 3. Start with Docker (recommended)

**Prerequisites:** [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/).

```shell
docker compose up --build
```

Then open:

```text
http://localhost:8000
```

No migrations or database setup are required.

Stop with `Ctrl+C`, or in another terminal:

```shell
docker compose down
```

### 4. Or run locally (without Docker)

```shell
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8000
```

Open http://localhost:8000

---

## Quick API examples

Chat (same backend the UI uses):

```shell
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message":"Where is my order 123?"}'
```

List orders, coupons, and tickets:

```shell
curl http://localhost:8000/api/orders/
curl http://localhost:8000/api/coupons/
curl http://localhost:8000/api/tickets/
```

---

## Testing

```shell
# Docker
docker compose run --rm web python manage.py test chatbot -v 2

# Local
python manage.py test chatbot -v 2
```

---

## Project structure

```text
food_delivery_chatbot/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── README.md
├── chatbot/
│   ├── services/          # Intent, orders, coupons, tickets, sentiment
│   ├── data/              # Mock orders & coupons
│   ├── templates/chatbot/ # Chat UI
│   ├── views.py
│   └── tests/
└── config/                # Django settings & URLs
```

Flow:

```text
Chat UI → POST /api/chat/ → Intent detection
                         → Order / Coupon / Ticket services
                         → NVIDIA sentiment
                         → JSON reply → Chat UI
```

---

## Notes

- Tickets are **in-memory only** and reset when the app/container restarts.
- There is **no database** in this project.
- Unknown order IDs get a friendly “not found” message.
- Empty messages ask you to type something.
- Unrecognized intents get a short help reply (orders, coupons, issues).

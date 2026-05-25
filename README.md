# Quote Generator AI Vision

Real-time computer vision quote generation across WhatsApp and Telegram.

> Customer sends a product photo → Claude Sonnet 4.6 extracts SKU details → catalog match → dynamic quote → instant reply → live operator dashboard.

## Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.12 + FastAPI (async) |
| Vision | Claude Sonnet 4.6 (Anthropic API) |
| WhatsApp | Twilio Sandbox |
| Telegram | Bot API |
| Auth | Clerk (`@clerk/clerk-react`) |
| Frontend | Vite + React + TypeScript + Tailwind |
| Storage | SQLite via `aiosqlite` |

## Quick start

### 1. Python backend

```bash
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
uvicorn app.main:app --reload
```

### 2. React dashboard

```bash
cd web
cp .env.example .env   # set VITE_CLERK_PUBLISHABLE_KEY
npm install
npm run dev
# → http://localhost:5173
```

### 3. Expose webhooks

```bash
ngrok http 8000
```

Set the HTTPS URL in:
- Twilio Sandbox → "When a message comes in": `https://<ngrok>/webhook/whatsapp`
- Telegram → register webhook: `curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" -d "url=https://<ngrok>/webhook/telegram"`

### 4. Smoke test (no phone needed)

```bash
python scripts/send_test_image.py path/to/product.jpg
```

## WhatsApp setup (Twilio Sandbox)

### Step 1 — Create a Twilio account

1. Go to [twilio.com](https://twilio.com) and sign up for a free account.
2. Verify your phone number during onboarding.

### Step 2 — Activate the WhatsApp Sandbox

1. In the Twilio Console, open **Messaging → Try it out → Send a WhatsApp message**.
2. Follow the on-screen instructions: send the displayed join code (e.g. `join <word>-<word>`) from your WhatsApp to the sandbox number shown.
3. You should receive a confirmation reply — the sandbox is now active for your number.

### Step 3 — Collect your credentials

From the Twilio Console home page copy:

| Variable | Where to find it |
|---|---|
| `TWILIO_ACCOUNT_SID` | Dashboard → Account Info |
| `TWILIO_AUTH_TOKEN` | Dashboard → Account Info (click to reveal) |
| `TWILIO_WHATSAPP_FROM` | The sandbox number in the format `whatsapp:+14155238886` |

Paste these into your `.env` file.

### Step 4 — Point the sandbox at your webhook

1. In **Messaging → Sandbox Settings**, set **"When a message comes in"** to:
   ```
   https://<your-ngrok-subdomain>.ngrok-free.app/webhook/whatsapp
   ```
   Method: **HTTP POST**
2. Click **Save**.

### Step 5 — Test

Send any WhatsApp message (or a product photo) from the joined number and confirm a reply appears in your terminal logs.

---

## Telegram setup (Bot API)

### Step 1 — Create a bot

1. Open Telegram and message [@BotFather](https://t.me/botfather).
2. Send `/newbot`, choose a name and username (must end in `bot`).
3. Copy the **token** BotFather gives you.

### Step 2 — Collect your credentials

| Variable | Where to find it |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Token from BotFather (step 1) |
| `TELEGRAM_WEBHOOK_SECRET` | Any random string you invent — sent as `X-Telegram-Bot-Api-Secret-Token` header |

Paste these into your `.env` file.

### Step 3 — Register the webhook

```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d "url=https://<your-ngrok-subdomain>.ngrok-free.app/webhook/telegram" \
  -d "secret_token=<TELEGRAM_WEBHOOK_SECRET>"
```

### Step 4 — Test

Send a photo to your bot from any Telegram account. Confirm the message appears in your terminal logs and a quote reply is sent back.

---

## Smoke-test CLI

```
[1/3] Sending sneaker.jpg to Claude Sonnet 4.6…
[2/3] Matching SKU…
[3/3] Building quote…
*Quote for Air Zoom Pro Sneaker*
Qty: 1 × $129.99
Subtotal: $129.99
Tax (8%): $10.40
Shipping: $5.99
*Total: $146.38 USD*
```

## Architecture

```
WhatsApp/Telegram → /webhook/* → BackgroundTask
  → download image → Claude vision → catalog match → quote → channel reply
  → SSE broadcast → React dashboard (live feed)
```

## Deployment notes

For true serverless: wrap FastAPI with [Mangum](https://mangum.io/) for AWS Lambda, or deploy to [Modal](https://modal.com/). The SSE broker would need Redis pub/sub for multi-instance setups.

# Quote Generator AI Vision

Real-time computer vision quote generation across WhatsApp and Instagram.

> Customer sends a product photo → Claude Sonnet 4.6 extracts SKU details → catalog match → dynamic quote → instant reply → live operator dashboard.

## Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.12 + FastAPI (async) |
| Vision | Claude Sonnet 4.6 (Anthropic API) |
| WhatsApp | Twilio Sandbox |
| Instagram | Meta Graph API |
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
- Meta → Webhook URL: `https://<ngrok>/webhook/instagram`, Verify token matches `META_VERIFY_TOKEN`

### 4. Smoke test (no phone needed)

```bash
python scripts/send_test_image.py path/to/product.jpg
```

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
WhatsApp/Instagram → /webhook/* → BackgroundTask
  → download image → Claude vision → catalog match → quote → channel reply
  → SSE broadcast → React dashboard (live feed)
```

## Deployment notes

For true serverless: wrap FastAPI with [Mangum](https://mangum.io/) for AWS Lambda, or deploy to [Modal](https://modal.com/). The SSE broker would need Redis pub/sub for multi-instance setups.

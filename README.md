# Quote Generator AI Vision

Real-time computer vision quote generation across WhatsApp and Facebook Messenger.

> Customer sends a product photo → Claude Sonnet 4.6 extracts SKU details → catalog match → dynamic quote → instant reply → live operator dashboard.

## Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.12 + FastAPI (async) |
| Vision | Claude Sonnet 4.6 (Anthropic API) |
| WhatsApp | Twilio Programmable Messaging |
| Messenger | Twilio Programmable Messaging (Facebook Messenger) |
| Auth | Operator password → FastAPI JWT |
| Frontend | Vite + React + TypeScript + Tailwind (TailAdmin) |
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
npm install
npm run dev
# → http://localhost:5173
```

### 3. Expose webhooks

```bash
ngrok http 8000
```

Set the HTTPS URL in:
- Twilio WhatsApp Sandbox → "When a message comes in": `https://<ngrok>/webhook/whatsapp`
- Twilio Messenger Sender → "When a message comes in": `https://<ngrok>/webhook/messenger`

### 4. Smoke test (no phone needed)

```bash
python scripts/send_test_image.py path/to/product.jpg
```

---

## WhatsApp setup (Twilio Sandbox)

### Step 1 — Create a Twilio account

1. Go to [twilio.com](https://twilio.com) and sign up for a free account.
2. Verify your phone number during onboarding.

### Step 2 — Activate the WhatsApp Sandbox

1. In the Twilio Console, open **Messaging → Try it out → Send a WhatsApp message**.
2. Follow the on-screen instructions: send the displayed join code (e.g. `join <word>-<word>`) from your WhatsApp to the sandbox number shown.
3. You should receive a confirmation reply — the sandbox is now active for your number.

### Step 3 — Collect your credentials

| Variable | Where to find it |
|---|---|
| `TWILIO_ACCOUNT_SID` | Console home → Account Info |
| `TWILIO_AUTH_TOKEN` | Console home → Account Info (click to reveal) |
| `TWILIO_WHATSAPP_FROM` | The sandbox number in format `whatsapp:+14155238886` |

Paste these into your `.env` file.

### Step 4 — Point the sandbox at your webhook

1. In **Messaging → Sandbox Settings**, set **"When a message comes in"** to:
   ```
   https://<your-ngrok-subdomain>.ngrok-free.app/webhook/whatsapp
   ```
   Method: **HTTP POST**
2. Click **Save**.

### Step 5 — Test

Send a product photo from the joined WhatsApp number and confirm a quote reply appears.

---

## Facebook Messenger setup (Twilio)

Twilio acts as the bridge between your Facebook Page and the app. No Meta Developer App approval is required for this flow — only a Facebook Page and a Twilio account.

### Step 1 — Create or use a Facebook Page

You need a Facebook Page (not a personal profile) to receive Messenger messages.

1. Go to [facebook.com/pages/create](https://facebook.com/pages/create) if you don't have one.
2. Note your **Page ID** — visible in **Page Settings → About → Page transparency** or in the page URL for older pages.

### Step 2 — Connect the Page to Twilio

1. In the Twilio Console, go to **Messaging → Senders → Facebook Messenger**.
2. Click **Connect a Facebook Page**.
3. Log in with the Facebook account that manages the Page and grant Twilio the requested permissions.
4. Select the Page you want to use and confirm. Twilio will display a **Messenger Sender** entry once connected.
5. Copy the sender identifier — it appears in format `messenger:<Facebook_Page_ID>`.

### Step 3 — Collect your credentials

| Variable | Where to find it |
|---|---|
| `TWILIO_ACCOUNT_SID` | Console home → Account Info |
| `TWILIO_AUTH_TOKEN` | Console home → Account Info (click to reveal) |
| `TWILIO_MESSENGER_FROM` | The sender from step 2, e.g. `messenger:123456789012345` |

Paste these into your `.env` file.

### Step 4 — Point the Messenger Sender at your webhook

1. In **Messaging → Senders → Facebook Messenger**, click the sender you just connected.
2. Under **Messaging Configuration**, set **"A message comes in"** to:
   ```
   https://<your-ngrok-subdomain>.ngrok-free.app/webhook/messenger
   ```
   Method: **HTTP POST**
3. Save. Twilio will verify the URL with a test request.

### Step 5 — Test

1. Open Facebook and go to your Page.
2. Click **Send Message** and send a product photo via Messenger.
3. Confirm the quote reply arrives and the event appears in the operator dashboard.

> **Note:** Users must initiate the conversation first — Pages cannot cold-message users via the Messenger API. For testing, simply send a message from your own Facebook account to the Page.

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
WhatsApp/Messenger → /webhook/* → BackgroundTask
  → download image → Claude vision → catalog match → quote → channel reply
  → SSE broadcast → React dashboard (live feed)
```

Both channels go through the same Twilio Programmable Messaging API. The webhook payload format is identical — `From`, `To`, `MediaUrl0` — only the sender prefix differs (`whatsapp:` vs `messenger:`).

## Environment variables

```env
ANTHROPIC_API_KEY=

TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_MESSENGER_FROM=messenger:<your-page-id>

OPERATOR_PASSWORD=
JWT_SECRET=

PUBLIC_BASE_URL=https://<ngrok>.ngrok-free.app
ALLOWED_ORIGINS=http://localhost:5173
```

## Deployment notes

For true serverless: wrap FastAPI with [Mangum](https://mangum.io/) for AWS Lambda, or deploy to [Modal](https://modal.com/). The SSE broker would need Redis pub/sub for multi-instance setups.

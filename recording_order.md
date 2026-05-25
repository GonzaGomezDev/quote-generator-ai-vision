 Build order (recommended for filming)

 1. Skeleton — main.py, config, health check, .env.example, requirements.txt, CORS for localhost:5173.
 2. Catalog + quoting — seed JSON, catalog.py, quoting.py, a couple of unit tests. Pure logic, no I/O.
 3. Vision — claude_client.py + a CLI script that takes a local image and prints JSON. Great B-roll for the video.
 4. Storage + SSE broker — minimum schema, in-memory fan-out.
 5. Clerk auth — create Clerk app, wire app/auth/clerk.py JWT verifier, protect /api/*.
 6. React dashboard scaffold — npm create vite@latest web -- --template react-ts, install Clerk + Tailwind, sign-in flow, empty dashboard
 reading /api/quotes.
 7. Live feed — useEventStream hook + EventCard + LatencyBars. Drive from CLI script feeding fake events.
 8. WhatsApp via Twilio — webhook + reply; verify with ngrok + Twilio Sandbox join code.
 9. Telegram via Bot API — webhook + reply; create bot with @BotFather, register setWebhook with ngrok URL.
 10. Polish — filters, empty/error states, README walkthrough.

 Each step is a clean YouTube checkpoint.
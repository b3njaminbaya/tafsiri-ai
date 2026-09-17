# Backend — Tafsiri AI API

FastAPI service: auth (cookie-based, OAuth, password reset, email
verification)/roles/API keys, translation (proxied to `ml-service`, cached in
Redis, persisted to Postgres), dataset upload (MinIO/S3), an active-learning
review queue, community stats, personal analytics, and a Stripe billing
scaffold. See [../docs/AUDIT.md](../docs/AUDIT.md) for the full history and
honest caveats behind each of these.

**Every optional integration below (email, OAuth, billing) is safe to leave
unconfigured.** The app boots and every other feature works normally; the
specific dependent endpoint degrades gracefully (logs instead of emailing,
returns a clean 503 instead of crashing, etc.) rather than failing at
startup or under load.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Key settings (see `app/core/config.py` for all of them):

| Setting | Purpose |
|---|---|
| `DATABASE_URL` | Postgres connection string, sync-driver form (`postgresql+psycopg2://...`) — the app converts it to `postgresql+asyncpg://` internally; Alembic uses the sync form directly. |
| `SECRET_KEY` | JWT signing key. |
| `FIRST_ADMIN_EMAIL` | Optional. That email is promoted to admin automatically at registration — the only other way to get a first admin account is a direct DB edit. |
| `FRONTEND_BASE_URL` / `BACKEND_BASE_URL` | Used to build password-reset/verification links and OAuth redirect URIs. |
| `ML_SERVICE_URL` | Where `ml-service` is reachable. |
| `REDIS_URL` | Translation response cache. Optional in the sense that a Redis outage degrades to no caching, not a failure — but the app doesn't run without a reachable value configured. |
| `MINIO_*` | Dataset object storage (see the two-endpoint split documented in `app/core/config.py` — internal vs. browser-facing). `MINIO_REGION` defaults to `us-east-1` for local MinIO; production sets it to `auto`, Cloudflare R2's documented region for SigV4 signing. |
| `SMTP_*` | Password reset / verification email — see below. |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Google OAuth login — see below. |
| `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` | GitHub OAuth login — see below. |
| `STRIPE_*` | Billing — see below. |

## Auth: cookies, OAuth, password reset, email verification

- The browser SPA authenticates via an httpOnly `access_token` cookie (set on
  `/auth/login`, cleared on `/auth/logout`) rather than a token held in
  `localStorage` — not readable by JS, so not stealable via XSS. API/CLI
  consumers keep using a plain `Authorization: Bearer` header; an explicit
  header always wins over the cookie if a request somehow carries both (see
  `deps.py`'s `get_token_from_request`).
- **Password reset / email verification** (`app/email_client.py`): if
  `SMTP_HOST` isn't set, the app logs the email it would have sent (link
  included) instead of failing — enough to fully exercise both flows with
  zero mail infrastructure. Set `SMTP_HOST`/`SMTP_PORT`/`SMTP_USERNAME`/
  `SMTP_PASSWORD`/`SMTP_FROM_ADDRESS` to actually send.
- **OAuth (Google/GitHub)** (`app/oauth_client.py`): a plain Authorization
  Code flow over `httpx`, not a third-party OAuth library. `GET
  /api/v1/auth/oauth/providers` reports which are configured; the frontend
  login page uses this to disable/label buttons for providers that aren't,
  rather than offering a button that 503s. Each provider needs its client
  ID/secret from that provider's own developer console, with the redirect
  URI registered there set to `{BACKEND_BASE_URL}/api/v1/auth/oauth/google/callback`
  (or `.../github/callback`). Signing in with a provider links to an
  existing password-based account sharing that email if one exists, rather
  than creating a duplicate.

## Database: async, with one subtlety worth knowing

The app uses `AsyncSession` throughout (`app/database.py`, `app/deps.py`).
One thing to keep in mind if you add a new query: SQLAlchemy's async mode
can't lazy-load a relationship outside an `await` (it raises
`MissingGreenlet`) — so any relationship read after the fact (e.g.
`user.role.name` in `require_role`) must be eager-loaded at query time via
`selectinload(...)`. See `app/deps.py`'s `_user_from_token` for the pattern.

## Migrations (Alembic)

```bash
alembic upgrade head            # apply all migrations
alembic revision -m "message"   # create a new empty migration
```

Migrations run against the sync driver (`postgresql+psycopg2://...`) — this
is deliberate; the app's runtime async engine is separate (see
`database.py`'s `to_async_url`, which also strips the connection string's
query params for the async driver — asyncpg doesn't understand
`channel_binding`, which Neon includes by default; TLS intent is preserved
separately via `connect_args`). `alembic upgrade head` runs automatically
before uvicorn starts both in `docker-compose` (via its command override)
and in `Dockerfile`'s own `CMD` — the latter matters because Cloud Run (and
any other host building straight from the Dockerfile) uses that `CMD`
directly, not docker-compose's.

Production also runs uvicorn with `--proxy-headers
--forwarded-allow-ips='*'`: both Cloud Run and Render terminate TLS in front
of the container, and without trusting the proxy's `X-Forwarded-Proto`
header, Starlette's automatic trailing-slash redirects build their
`Location` URL from the scheme they see internally (`http`), downgrading
real HTTPS clients.

## Billing (Stripe) — unverified against the real API

`app/billing_client.py` and `app/api/v1/routes/billing.py` implement Stripe
Checkout session creation and webhook handling, mapping a purchased price ID
to an API key's `quota_limit`. This is tested against a fake Stripe client
(`tests/test_billing.py`) but **has not been exercised against the real
Stripe API** — there are no Stripe test-mode credentials available in this
project's development environment. Before relying on this:

1. Set `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, and
   `STRIPE_PRICE_QUOTA_MAP` (format: `price_basic:1000,price_pro:100000` —
   Stripe price IDs are opaque per-project strings from your own dashboard).
2. Point a real Stripe webhook at `/api/v1/billing/webhook`.
3. Walk through an actual test-mode checkout and confirm the target API key's
   `quota_limit` updates.

The frontend Pricing page is intentionally **not** wired to a "Subscribe"
button yet — doing that before the Stripe side is verified would repeat
exactly the "UI that pretends to work" pattern this project's audit exists to
call out.

## Tests

```bash
pytest
```

Tests use an isolated in-memory SQLite database via `aiosqlite` (see
`tests/conftest.py`) so they don't touch your local Postgres instance. A
handful of tests need to poke the DB directly, bypassing the API (no
endpoint sets API key quotas directly, etc.) — see `conftest.py`'s `run_db`
helper for how that bridges into the async session from an ordinary
synchronous test function.

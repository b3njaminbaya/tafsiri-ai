# Tafsiri AI

_Tafsiri_ is Swahili for "translation." A full-stack neural machine
translation platform that is **Kenya-only**: Swahili (the national/official
language) and Somali (spoken in northeastern Kenya) are fully supported
today, because they're the only two of Kenya's ~68 living languages with
pretrained coverage in the underlying M2M100 model. English is kept as the
one deliberate exception — it's Kenya's other constitutional official
language, and the practical bridge for the real use case (Kenyan
language↔English). Every other language M2M100 happens to support (Spanish,
French, Amharic, ...) has been deliberately removed; this is not a
general-purpose translator.

Kikuyu, Luo, Kalenjin, Kamba, Kisii, Maasai, Luhya, Meru, Mijikenda,
Turkana, and other Kenyan languages are an explicit, honestly-labeled
roadmap (see `GET /languages/roadmap`) rather than something the app
pretends to support. There's a real, tested, end-to-end pipeline for
closing that gap — pulling contributed parallel text from the Datasets
page, LoRA fine-tuning the model on a language it's never seen, evaluating
the result, and serving it — see
[`ml-service/training/README.md`](ml-service/training/README.md). What it
doesn't have yet is real data: that starts with contributions through the
Datasets page. The platform has real persistence, a trained multilingual
model, and the account/community/billing infrastructure a production
product needs around it.

The project is organized as three cooperating services — a React frontend, a
FastAPI backend, and a dedicated translation microservice — plus the Docker
Compose infrastructure that ties them together with Postgres, Redis, and
MinIO.

## What it does

Visitors can translate text between Swahili, Somali, and English, with
optional domain-specific terminology forcing (medical, legal, technical glossaries)
that guarantees a chosen term appears in the output regardless of general
model quality. Every translation is persisted with a confidence score, so
registered users get a real history and personal analytics, and low-confidence
translations automatically enter an active-learning review queue where
translators and admins can submit corrections that feed back into future
model improvement.

Beyond translation, the platform includes a community forum for discussion,
a real blog with an admin-authored CMS, dataset upload and sharing for
parallel corpora, GDPR-compliant data export and account erasure, configurable
privacy/consent settings, and a Stripe-backed subscription/billing layer. An
admin panel provides user management (role changes, account activation), full
control over the domain glossary, and blog publishing — all gated behind role-
based access control.

Every optional third-party integration — email delivery, Google/GitHub OAuth,
and Stripe billing — is designed to degrade gracefully. The application boots
and every core feature works normally whether or not those credentials are
configured; the dependent endpoint either logs what it would have done (email)
or returns a clean, honest error (OAuth, billing) instead of crashing.

## Architecture

**Frontend** (`/src`) — React 18 with TypeScript, Vite, Tailwind CSS, and
shadcn/ui components. Authenticates against the backend via an httpOnly
session cookie (with Bearer-token support for API/CLI use), and communicates
exclusively through the backend's REST API — it never talks to the ML service
or the database directly.

**Backend** (`/backend`) — FastAPI with fully async SQLAlchemy over Postgres,
Alembic-managed migrations, Redis-backed translation caching, and MinIO/S3
object storage for dataset uploads. Owns every piece of business logic: auth
and session management, role-based access control, the domain glossary, GDPR
request handling, billing, community content (forum and blog), and analytics
aggregation. Proxies actual translation requests to the ML service over an
async HTTP client.

**ML service** (`/ml-service`) — A dedicated FastAPI microservice wrapping
Meta's M2M100 multilingual translation model via Hugging Face Transformers,
with automatic source-language detection and constrained beam search for
glossary term forcing. Kept separate from the backend so the (large,
GPU-friendly) model dependency and its resource footprint never has to ship
alongside ordinary API traffic.

**Infrastructure** (`/infra`) — Docker Compose definitions for Postgres,
Redis, MinIO, the backend, and the ML service, plus the `.env`-based
configuration that lets every optional integration be enabled or left off
independently. This is the **local development** stack; see "Deployment"
below for what actually runs in production. See `infra/README.md` for exact
setup steps.

## Features

Authentication is cookie-based for the browser SPA and Bearer-token based for
API and CLI clients, with email/password registration, password reset and
email verification (both logged instead of emailed when no SMTP server is
configured), and optional Google/GitHub OAuth login that automatically links
to an existing account sharing the same email address. A designated bootstrap
admin email can be configured so the very first account created is
automatically granted the admin role, without ever needing a direct database
edit.

Translation supports both single and batch requests, automatic source
language detection, per-domain glossary term forcing, response caching to
avoid redundant model calls for identical requests, and a full personal
history with user-submitted feedback ratings. Registered translators and
admins additionally see an active-learning review queue surfacing the
lowest-confidence translations still awaiting a human correction.

Dataset management allows any authenticated user to upload parallel-corpus
files (TSV, CSV, TXT, JSON, JSONL, TMX, or XLIFF, validated by extension
before ever reaching storage) with associated language pair and domain
metadata, and to browse or download what others have contributed via
time-limited presigned URLs.

The community layer includes a real, database-backed discussion forum
organized into fixed categories with posts and threaded replies, public
contribution statistics and leaderboards, and a blog with genuine draft and
published states — content is authored and managed entirely through the
admin panel rather than hardcoded into the frontend.

Privacy and compliance features include per-user consent settings for
analytics, marketing, and data collection; an immediate, real JSON export of
everything a user's account touches; and account erasure that anonymizes
rather than hard-deletes a user, preserving the referential integrity of
translations, corrections, and dataset uploads that other parts of the
platform legitimately still reference. Formal GDPR data-subject requests are
logged, with access and portability requests fulfilled automatically through
the export endpoint.

Billing is built on Stripe Checkout for subscription purchases, with API key
quota tiers updated automatically via webhook on successful payment. Every
billing-related endpoint checks that Stripe credentials are actually
configured before attempting a call, so an unconfigured deployment fails fast
and cleanly rather than hanging on a doomed request to Stripe's API.

The admin panel brings user management (listing every account, changing
roles, activating or deactivating accounts — with a guard against an admin
locking themselves out), full glossary term management, and blog publishing
together in one place, with platform-wide analytics available alongside each
admin's personal usage statistics.

## Tech stack

The frontend is built with React, TypeScript, Vite, Tailwind CSS, shadcn/ui,
React Router, TanStack Query, and Recharts for data visualization. The
backend runs on FastAPI with async SQLAlchemy, asyncpg, Alembic, Pydantic,
python-jose for JWTs, passlib/bcrypt for password hashing, slowapi for rate
limiting, boto3 for S3-compatible storage, and the official Stripe SDK. The
ML service runs FastAPI alongside Hugging Face Transformers, PyTorch, and
SentencePiece to serve the M2M100 multilingual model, with langdetect for
automatic source-language identification. Persistence and infrastructure are
Postgres, Redis, and MinIO, all orchestrated locally through Docker Compose.

## Getting started

The fastest path to a fully running stack is Docker Compose, which brings up
Postgres, Redis, MinIO, the backend, and the ML service together:

```bash
cd infra
cp .env.example .env
# edit .env — every value is optional; see the comments in that file for
# what each one unlocks and where to get it
docker compose up --build
```

The backend becomes available at `http://localhost:8000` (interactive API
docs at `/docs`), and the ML service at `http://localhost:8001`. The ML
service downloads the model (roughly 1.6GB for M2M100) and loads it at
startup, before it starts accepting requests — `GET /ready` on the ML
service reports 503 until that finishes. The download is cached in a Docker
volume, so only the first `docker compose up` pays for it.

The frontend runs separately as a Vite dev server:

```bash
npm install
npm run dev
```

By default it expects the backend at `http://localhost:8000/api/v1` —
override this via `VITE_API_BASE_URL` in a `.env.local` file if needed.

See `backend/README.md` and `infra/README.md` for a deeper look at
configuration, migrations, and what each optional integration requires to
turn on.

## Deployment

The live deployment does **not** use Docker Compose — that's the local-dev
stack described above. Production runs as five independently-hosted pieces,
chosen to stay on free tiers end to end:

| Service | Host | Why |
|---|---|---|
| Frontend | [Vercel](https://vercel.com) | Static Vite build, free Hobby plan |
| Backend | [Google Cloud Run](https://cloud.google.com/run) (Frankfurt) | Scale-to-zero, genuinely free monthly quota (180,000 vCPU-seconds / 360,000 GiB-seconds / 2M requests) |
| ML service | Google Cloud Run (Frankfurt) | Same as backend — needs real memory (~2GB+) for M2M100 + PyTorch, which ruled out Render's free/Starter tiers (512MB cap on both) |
| Database | [Neon](https://neon.tech) | Serverless Postgres, scale-to-zero |
| Cache | [Upstash](https://upstash.com) | Serverless Redis, TLS-only |
| Object storage | [Cloudflare R2](https://developers.cloudflare.com/r2/) | S3-compatible, no egress fees |

Both Cloud Run services build directly from their own `Dockerfile`
(`backend/Dockerfile`, `ml-service/Dockerfile`) via `gcloud run deploy
--source=...` — no separate CI/CD pipeline. A few things about those
Dockerfiles only matter in this deployed context, not for local
`docker compose` use:

- `backend/Dockerfile`'s `CMD` runs `alembic upgrade head` before starting
  uvicorn, and uvicorn itself runs with `--proxy-headers
  --forwarded-allow-ips='*'` — both Cloud Run and Render terminate TLS in
  front of the container and forward plain HTTP internally, so without
  trusting `X-Forwarded-Proto` from that proxy, FastAPI's automatic
  trailing-slash redirects built their `Location` header with `http://`,
  silently downgrading real HTTPS clients.
- `ml-service/Dockerfile` downloads and bakes the model weights into the
  image at build time (`ARG MODEL_NAME`) rather than leaving `from_pretrained`
  to fetch them from the Hub on first request. Cloud Run's container
  filesystem is ephemeral — every scale-to-zero cold start was
  re-downloading the ~1.6GB model, pushing cold-start latency to ~55-58
  seconds, right at the edge of even a generous request timeout.

Each of the three application services needs its own environment
configuration wired in at its host (Cloud Run env vars, Vercel project
environment variables) — see `backend/README.md`'s settings table and
`ml-service/README.md` for what each one does. `VITE_API_BASE_URL` on the
frontend and `CORS_ORIGINS`/`FRONTEND_BASE_URL` on the backend have to agree
with each other's real deployed URLs, or the browser build will either call
the wrong backend or get rejected by CORS.

## Project structure

`src/` holds the entire frontend application — pages, components, the API
client, and auth context. `backend/app/` holds the FastAPI application,
organized into versioned API routes (`api/v1/routes/`), SQLAlchemy models,
Pydantic schemas, and the dependency-injectable clients for every external
integration (email, OAuth, Stripe, S3, Redis, the ML service). `backend/
alembic/` holds every database migration in sequence. `ml-service/app/`
holds the translation microservice. `infra/` holds the Docker Compose stack
and its environment configuration. `docs/AUDIT.md` is a detailed, continually
updated engineering log covering architecture decisions, known gaps, and a
full history of every development phase this project has gone through.

## Testing

The backend test suite runs against an in-memory SQLite database with every
external integration replaced by an in-process fake, so it never requires a
running Postgres, Redis, MinIO, or ML service instance:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest
```

The ML service has its own independent test suite under `ml-service/tests/`,
runnable the same way. The frontend is checked with `npm run lint` and
`npx tsc --noEmit`, and built for production with `npm run build`.

## Documentation

`docs/AUDIT.md` is the authoritative source for architectural context,
security and performance considerations, and a phase-by-phase log of what has
been built and verified, including exactly how each feature was tested
against real infrastructure — including the production deployment itself.
`backend/README.md` documents every backend configuration value and how each
optional integration behaves when left unconfigured. `infra/README.md`
covers the Docker Compose **local development** setup end to end; see
"Deployment" above for what actually runs in production.

## Contributing

Issues and pull requests are welcome. Please run the relevant test suite(s)
and, for backend changes touching the database, include an Alembic migration
before submitting.

## License

This project is licensed under the MIT License — see `LICENSE` for details.

## Contact

**Project Lead:** Benjamin Mweri Baya — b3njaminbaya@gmail.com

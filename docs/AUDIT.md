# NMT Agent — Engineering & Commercialization Audit

_Prepared 2026-07-10, against commit `46cbd2b`. A live, styled version of this report was published as a Claude Artifact during the review session; this file is the reference copy kept in-repo._

## Executive summary

The [README](../README.md) describes a mature MVP: OAuth, active learning, bias detection, BLEU/METEOR/TER tracking, Elasticsearch, Kubernetes. The codebase describes something much earlier: a **Lovable-generated marketing shell** (the `lovable-tagger` dev dependency confirms it) sitting in front of a small, genuinely well-built FastAPI auth service, wired to a translation endpoint that reverses the input string and an ML microservice that only answers `/health`.

Every "feature" that isn't authentication — datasets, GDPR requests, privacy settings, community, pricing, API docs, system status — is static content or a `setTimeout` pretending to be a network call.

| Metric | Value |
|---|---|
| Services in repo | 3 (frontend SPA, FastAPI backend, ml-service stub) |
| Real backend endpoints | 7 (register, login, me, api-keys CRUD, promote) |
| Translation endpoints | 1 — a placeholder (string reversal) |
| Automated tests | 0 |
| CI workflows | 0 |
| Frontend pages | 20 routed pages, ~3,700 lines, entirely mock data |

**Verdict:** polished storefront, empty warehouse. Real auth core; translation, ML, and data layers are scaffolding.

## Architecture — intended vs. actual

| Layer | README's intent | What's in the repo |
|---|---|---|
| Translation | Transfer-learned NMT model, few-shot for low-resource pairs | `text[::-1]` with a hardcoded 0.42 confidence (`backend/app/api/v1/routes/translate.py:9-11`) |
| Model serving | TensorFlow/PyTorch + Hugging Face Transformers | Empty FastAPI shell, no ML library in `requirements.txt` |
| Datasets | Upload, versioning, augmentation, community review | Six hardcoded cards on a page; "Upload Dataset" button has no handler |
| Analytics | BLEU/METEOR/TER dashboards, usage trends | Not present anywhere in frontend or backend |
| API for developers | REST + WebSockets, rate limiting | Docs page advertises `/languages`, `/batch`, `/models` endpoints that don't exist; no WebSocket code; `quota_limit` column exists but is never checked |
| Community/feedback | Crowdsourced corrections, forum | Static marketing page only |

Nothing in `backend/app` ever calls the ml-service (no `httpx` request to port 8001, despite `httpx` being an unused backend dependency). Postgres only has `users`/`roles`/`api_keys` tables. MinIO creates `datasets`/`models` buckets on boot that nothing ever reads or writes.

## Feature status matrix

| Feature | Status | Evidence |
|---|---|---|
| Register / login | ✅ Working | `auth.py` — real bcrypt hash, JWT issue/verify |
| Roles + promotion | ✅ Working | `auth.py:84` — role-gated, but no UI for it |
| API key issue/list/revoke | ✅ Working | DB-backed; `quota_limit` stored, never enforced |
| OAuth / social login | ❌ Missing | `Login.tsx:74` — buttons show a toast only |
| Text translation | ❌ Placeholder | `translate.py:9-11` |
| Language detection | ❌ Missing | Echoes back whatever `source_lang` the client sent |
| Batch translation | ❌ Missing | Advertised in docs, no route exists |
| Domain customization | 🟣 Cosmetic | Selector exists, placeholder route ignores it |
| Confidence scoring | 🟣 Cosmetic | Constant 0.42 |
| Text-to-speech | ❌ Missing | Button rendered, no handler |
| Dataset upload/versioning | 🟣 Cosmetic | Hardcoded cards; no upload handler |
| Model training / active learning | ❌ Missing | No training code anywhere |
| Bias/hallucination detection | ❌ Missing | Not referenced outside README |
| Analytics dashboards | ❌ Missing | Recharts installed, never imported |
| Feedback / rating | ❌ Missing | No model, route, or UI |
| REST API for developers | 🟣 Cosmetic | Docs reference a domain/endpoints that don't exist |
| WebSockets | ❌ Missing | No socket server or client |
| Rate limiting | ❌ Missing | Quota columns exist, unread |
| GDPR request / privacy dashboard | 🟣 Cosmetic | All `setTimeout`, no backend route |
| Cookie consent | 🟡 Partial | Real, but gates nothing (no analytics/marketing scripts exist) |
| Pricing / billing | 🟣 Cosmetic | No payment integration |
| System status page | 🟣 Cosmetic | Hardcoded statuses |

## Key findings (bugs, tech debt, security)

- **Duplicated, hardcoded API base URL** — `src/lib/api.ts`, `Login.tsx:8`, `Translate.tsx:13` each redeclare the same literal; no `import.meta.env` usage anywhere, so a production build still points at `localhost:8000`.
- **No auth context or route guarding** — every component reads `localStorage` directly; gated pages render fully for logged-out users.
- **Installed-but-unused libraries** — React Query, react-hook-form, zod, Recharts are dependencies with zero call sites.
- **No schema migrations** — `Base.metadata.create_all()` runs in two places (`main.py`, `auth.py`) with no Alembic.
- **Zero tests, zero CI.**
- **JWT stored in `localStorage`** — vulnerable to XSS token theft.
- **CORS wildcard + credentials** — `cors_origins` falls back to `["*"]` while `allow_credentials=True`, a combination browsers reject for credentialed requests.
- **No login throttling** — brute-force / credential-stuffing exposure.
- **Unbounded request bodies** — `TranslateRequest.text` has no max length.
- **API key quotas are decorative** — `quota_used`/`quota_limit` exist, nothing enforces them.
- **Containers run as root**; no documented secrets-management path beyond a dev-only env var.

Full detail, file:line references, performance/scalability notes, and the innovation/commercialization sections are in the artifact delivered in-session (architecture diagram, severity-tagged findings, full roadmap and go-to-market strategy) — this file captures the durable reference content; ask Claude to regenerate the artifact view if needed.

## Roadmap

- **Phase 0 (critical, now):** stop the frontend from claiming success on fake requests; add Alembic; move JWT out of `localStorage`; add login rate limiting; add a CI smoke-test workflow.
- **Phase 1 (high-impact, next):** wire backend → ml-service with one real pretrained multilingual model (NLLB-200 or M2M100); persist translations/feedback; real dataset ingestion; shared auth context + env-based API config.
- **Phase 2 (differentiation):** active-learning review queue by confidence; contributor attribution; domain adapters (medical/legal/technical); real analytics dashboards.
- **Phase 3 (scale):** async DB access, caching, ml-service batching/streaming, billing integration, Kubernetes/Elasticsearch if traffic justifies it.

## Commercialization (summary)

**Positioning:** not "another translation API" — the translation API for languages Google/DeepL don't cover well.

**Segments:** NGOs & humanitarian orgs, researchers & linguists, governments/public services, SaaS platforms expanding to underserved regions, individual language contributors.

**Model:** usage-based API pricing + freemium seed tier + dataset/corpus licensing + premium domain-specific enterprise contracts + grants/institutional partnerships as non-dilutive funding.

**Sequencing:** prove the full loop end-to-end for 2-3 specific low-resource languages before broadening; lead with the community/contributor angle to build the data moat before monetizing; only sell the compliance/enterprise tier once GDPR/privacy endpoints are real — selling compliance features that don't function is a legal liability, not a selling point.

---

## Phase 0 progress log (2026-07-10)

Work done in the first implementation pass, in the order it was found. Two items below were **not** in the original audit — they only surfaced once the backend was actually exercised (tests, then a real `docker compose up`), which is itself the audit's core finding in miniature: nothing in this repo had been run end-to-end before.

- **Boot-blocking bug (new finding):** every route file under `app/api/v1/routes/` used relative imports one level too shallow (`from ... import schemas` resolved to `app.api`, not `app`). The backend could not have started under `uvicorn app.main:app` as committed. Fixed to `from .... import schemas` etc. in `auth.py` and `translate.py`.
- **Boot-blocking bug (new finding):** `passlib==1.7.4` pinned without pinning `bcrypt`, so pip resolves the latest bcrypt (5.x today), which removed the API passlib's internal self-test depends on — hashing a password raised `ValueError` immediately. Pinned `bcrypt==4.0.1`.
- **Infra bug (new finding):** `infra/docker-compose.yml` built `backend`/`ml-service` with context `./backend` / `./ml-service`, which resolve relative to the compose file's own directory (`infra/`) — a path that doesn't exist. Fixed to `../backend` / `../ml-service`.
- **Infra bug (new finding):** the pinned `minio/mc` release tag no longer exists on Docker Hub; `docker compose up --build` failed on image pull. Moved to `minio/mc:latest`.
- Missing `__init__.py` files across `app/`, `app/api/`, `app/api/v1/`, `app/api/v1/routes/`, `app/core/` — the package was relying on implicit namespace packages, which broke under pytest's import machinery. Made them regular packages.
- Added Alembic; removed the two duplicate `Base.metadata.create_all()` bootstraps; wrote an initial migration (roles/users/api_keys) that seeds the three default roles.
- Added a backend pytest suite (16 tests: register/login, RBAC, API-key lifecycle, the translate placeholder's current behavior, rate limiting, API-key quota) and a GitHub Actions CI workflow (backend tests + frontend lint/build).
- Frontend: centralized the API client (`src/lib/api.ts`) behind `VITE_API_BASE_URL` instead of three hardcoded `localhost:8000` literals; added `AuthContext` + `ProtectedRoute` so `/translate` actually gates on auth state instead of rendering fully for logged-out users.
- Backend hardening: fixed the CORS wildcard+credentials default; added max-length limits on `TranslateRequest`; added login/register rate limiting (`slowapi`); gave the previously-decorative `APIKey.quota_limit`/`quota_used` columns a real enforcement path via a new `X-API-Key` auth option on `/translate` (JWT still works as before).

Still open from the original findings list: JWT still lives in `localStorage` (not yet moved to an httpOnly cookie); GDPR/privacy-dashboard pages are still cosmetic (`setTimeout`, no backend route); no real translation model is wired to `ml-service` yet; `ApiDocs.tsx` still documents endpoints/domains that don't exist. These are the natural next steps (Phase 1 of the roadmap above).

### Real end-to-end verification (not just unit tests)

The unit test suite runs against SQLite and mocks nothing about the app itself, but it can't catch container/config/packaging bugs. So after the unit tests were green, the full stack was actually booted with `docker compose up --build` against real Postgres — which surfaced four more boot-blocking bugs the unit tests couldn't see, all now fixed:

- `infra/docker-compose.yml` build contexts (`./backend`, `./ml-service`) were wrong relative to the compose file's own directory — fixed to `../backend` / `../ml-service`. **`docker compose up --build` could not have worked even once as committed.**
- `backend/Dockerfile` never copied `alembic.ini`/`alembic/` into the image, so the container's `alembic upgrade head` startup command failed immediately.
- The pinned `minio/mc` release tag no longer exists on Docker Hub — moved to `minio/mc:latest`.
- `Settings.cors_origins` was typed `List[str]`, which makes pydantic-settings try to JSON-decode the `CORS_ORIGINS` env var; a plain comma-separated string (the format `docker-compose.yml` and every doc in this repo actually use) crashed on startup with a `SettingsError`. Changed to a plain `str` field with a `cors_origin_list` property that splits it — compatible with the pinned `pydantic-settings==2.3.4` (the newer `NoDecode` marker isn't available in that version).

After all four fixes, the full stack was verified live end-to-end: `docker compose up --build`, then `curl` against the running containers for register → login → `/translate` with a JWT, `/translate` with a freshly-issued `X-API-Key` header (the new quota-enforced path), and a CORS preflight check — all confirmed working, then torn down cleanly with `docker compose down`.

Also fixed while touching this code: added non-root `USER appuser` to both Dockerfiles (previously ran as root).

---

## Phase 1 progress log (2026-07-10)

Phase 1 targeted the three items the roadmap called out as "turn the storefront into a product": a real translation model, persistence for translations/feedback, and real dataset ingestion.

### Real model wiring

- `ml-service` now wraps a genuine Hugging Face multilingual model instead of only answering `/health`. Chose **M2M100** (`facebook/m2m100_418M`) over NLLB-200: both are legitimate many-to-many models with strong low-resource coverage, but M2M100's tokenizer speaks plain ISO codes (`sw`, `am`, `ha`, `yo`, `zu`, ...) that already match what the rest of this app uses everywhere, where NLLB-200 would need a FLORES-200 mapping table (`swh_Latn`, ...) for no immediate benefit.
- `GET /languages` now returns a curated, deliberately low-resource-heavy language list (Swahili, Amharic, Hausa, Igbo, Yoruba, Zulu, Xhosa, Somali, Lingala, Wolof, Fulah, Ganda, alongside the common ones) — this is the actual product differentiator, not a demo dropdown.
- `confidence` is now a real geometric-mean token probability computed from the model's own generation scores (`model.compute_transition_scores`), replacing the hardcoded `0.42`.
- Missing `source_lang` (or `"auto"`) is resolved via `langdetect` rather than echoed back unchanged.
- The backend's `/translate` route now calls `ml-service` over HTTP through a small injectable `MLServiceClient` (`app/ml_client.py`) instead of doing the placeholder logic in-process. Tests override this dependency with an in-process fake, so the 28-test backend suite runs in ~12 seconds with no model or network dependency.
- **Verification approach:** downloading the real ~1.6GB `facebook/m2m100_418M` checkpoint for every test run (locally or in CI) would be slow and wasteful. Instead, `valhalla/m2m100_tiny_random` — a public, few-MB checkpoint sharing the exact same architecture/tokenizer classes — verifies the entire tokenize → generate → decode → confidence pipeline for real (its translations are gibberish, since the weights are random, but the code path is identical to production). This is what both `ml-service`'s own 5-test suite and its new CI job use.

### Persistence

- Added `Translation` and `Feedback` tables (Alembic migrations `0002`, `0003` — the latter also adds `Dataset`). Every `/translate` call now persists a row; nothing was recorded before.
- Added `GET /translate/history` (current user's past translations, most recent first) and `POST /translate/{id}/feedback` (1-5 rating + optional comment, restricted to the translation's own requester — there's no reviewer/moderation flow yet, a reasonable v2 scope item).
- `TranslateResponse` now includes the translation's `id`, so the frontend can attach feedback to the specific translation that produced it.

### Dataset ingestion

- Added a `Dataset` model + MinIO-backed storage client (`app/storage.py`, using `boto3` against MinIO's S3-compatible API — the buckets docker-compose already created but nothing touched).
- `POST /api/v1/datasets/` accepts a real multipart file upload (50MB cap), stores it in MinIO, and records metadata (name, description, language pair, domain, size, uploader). `GET /api/v1/datasets/` lists real records. `GET /api/v1/datasets/{id}/download` returns a presigned URL — deliberately generated via a *separate* "public" S3 client/endpoint setting (`MINIO_PUBLIC_URL`) from the one the backend uses internally (`MINIO_ENDPOINT_URL`), since a presigned URL built against the internal container-network hostname would be unreachable from a browser.
- Frontend: `Datasets.tsx` no longer shows six hardcoded cards with fabricated download counts and quality scores — it fetches the real list, supports real upload (gated behind login), and downloads via the presigned URL. `Translate.tsx` now captures the real translation `id` and lets a user thumbs-up/thumbs-down the result, calling the new feedback endpoint.
- Backend tests use an in-memory fake S3 client (same override-a-dependency pattern as the ML client) so the 28-test suite doesn't need a running MinIO.

### Verification: what was actually confirmed, and one honest gap

Following the same discipline as Phase 0 (verify live, don't just read the code), the goal was to boot the *entire* stack via `docker compose up --build` with the real production model and prove register → login → `/translate` end-to-end. That didn't fully succeed, and it's worth being precise about why, rather than quietly downgrading the claim:

- `docker compose build` repeatedly failed downloading large packages (PyTorch wheels, then a package-hash mismatch after ~700s) — a networking/proxy issue specific to this development sandbox's Docker build path, not a problem with the Dockerfiles or requirements. Mitigated by splitting `torch` into its own layer (`requirements-torch.txt`) and adding `pip install --retries 10 --timeout 120`, which is a genuine improvement either way (isolates the biggest, flakiest download into its own cached layer) but didn't fully resolve it here.
- To route around the Docker build issue, the same verification was attempted directly on the host: `ml-service` was run with `MODEL_NAME=facebook/m2m100_418M` in a real venv (the exact dependency versions from `requirements.txt`, successfully installed), and the backend was pointed at it (SQLite instead of Postgres, to isolate the model download as the only remaining variable). Register, login, and `GET /datasets/` all worked correctly against this real setup.
- The `/translate` call itself stalled: the first request triggers a lazy download of the 1.6GB model weights, and that download hung indefinitely at ~46MB. Root cause, confirmed directly: **this sandbox's DNS can resolve `huggingface.co` (small API/metadata calls work fine) but cannot resolve `cdn-lfs.huggingface.co`** — the separate CDN host Hugging Face uses to actually serve large Git-LFS-backed model weight files. `nslookup cdn-lfs.huggingface.co` returns no answer. This is an environment-level network restriction, not a code defect, and it plausibly explains the earlier Docker package-hash corruption too (large binary transfers being the common factor in every failure today).

**What this means concretely:** the tokenize → generate → decode → confidence pipeline is verified for real, twice over — once via `ml-service`'s own pytest suite and once via live HTTP calls (`/health`, `/languages`, `/translate` with both explicit and auto-detected source language) — all against `valhalla/m2m100_tiny_random`, which shares the production model's exact architecture and tokenizer classes. What is *not* yet verified in this environment is the production checkpoint's actual translation quality end-to-end, purely because its weights could not be downloaded here. Anyone running `docker compose up --build` (or the host verification steps above) from a network without this specific CDN restriction should expect it to work — nothing in the code path differs between the tiny and production checkpoints besides the model name.

### What's still open after Phase 1

- Feedback is self-only (a user can only rate their own translations) — no reviewer/moderation workflow yet (Phase 2: active-learning queue keyed off confidence, per the roadmap).
- Dataset upload has no format validation (accepts any file) and no domain-adapter training loop consumes uploaded datasets yet — they're stored and browsable, not yet used to improve the model.
- JWT still lives in `localStorage`; GDPR/privacy-dashboard pages are still cosmetic. Both remain explicitly deferred, not forgotten.
- `ApiDocs.tsx` still advertises endpoints (`/batch`, `/models`) and a domain (`api.nmtplatform.com`) that don't exist — worth a pass once the batch-translation and model-listing endpoints are actually built.

---

## Phase 2 progress log (2026-07-10)

Phase 2 targeted the roadmap's differentiation items: an active-learning review queue, domain adapters, contributor attribution, and real analytics — the features that separate this from a generic translation API wrapper.

### Domain adapters (without a training loop)

Real per-domain fine-tuned adapters (LoRA or otherwise) need labeled training data and a training pipeline this project doesn't have yet — building that wasn't honest to claim as "done" in one pass. Instead, `domain` now does something real: **terminology-constrained decoding**. `ml-service/app/glossary.py` holds a curated per-domain glossary (medical/legal/technical × a few language pairs); when a glossary term appears in the input, its correct target-language rendering is forced into the output via `transformers`' `force_words_ids` constrained beam search (`num_beams=4`). This is a genuine, well-established MT technique, not a placeholder — and it's directly testable regardless of model quality, since constrained decoding *guarantees* the forced phrase appears in the output. The response now includes `applied_glossary_terms` so the effect is observable, not just internal.

### Active-learning review queue

- New `Correction` model (migration `0004`) and `/review/queue` + `/review/{id}/correct` endpoints, gated to `translator`/`admin` roles via a new `require_any_role` dependency.
- The queue surfaces translations below a confidence threshold (default 0.6) that don't already have a correction, ordered lowest-confidence-first — the actual "active learning" prioritization: reviewer time goes to the translations that most need it.
- This is also the first real use of the `translator` role, which existed since the Phase 0 migration (and the `/auth/promote/{id}` endpoint that grants it) but had no purpose in the app until now.
- Frontend: a new `/review` page, visible in the nav only to translator/admin accounts, showing the queue with an inline correction textarea.

### Contributor attribution

- New public `GET /community/stats` endpoint: real counts (datasets, translations, corrections, distinct contributors) and top-contributor leaderboards for dataset uploads and review corrections.
- Privacy note: since there's no dedicated username/display-name field yet, only the email's local-part is shown publicly (not the full address) — a deliberate interim choice, not an oversight, given this endpoint is unauthenticated.
- `Community.tsx`'s "Community Stats" and "Top Contributors" cards now show this real data instead of fabricated numbers (12,847 members, etc.). Its discussion-forum section (categories, threads, replies) is a separate, genuinely large feature — a real forum backend — that Phase 2's roadmap didn't call for and this pass didn't attempt; it's still mock content, left as such rather than silently "fixed."

### Real analytics

- New `GET /analytics/summary` endpoint: total translations, average confidence, translations-by-day, top language pairs, and feedback rating distribution — all scoped to the current user's own history.
- Aggregation is done in Python rather than with DB-side date-truncation SQL, after `CAST(... AS DATE)` hit a genuine SQLite/SQLAlchemy result-processing bug in testing (`TypeError: fromisoformat: argument must be str`) that doesn't have a clean cross-database fix at the SQLAlchemy-generic-type level. At the scale of one user's translation history this is simple, correct, and fast; worth revisiting with DB-side aggregation only if this needs to summarize across all users at scale.
- Frontend: new `/analytics` page using Recharts (finally — it was an installed, unused dependency since before Phase 0). Followed the project's dataviz procedure: since every chart here is single-series magnitude data (counts by day, by language pair, by rating) rather than multi-category identity, the correct choice was one sequential hue, not a categorical palette — reused the app's existing `--brand` token rather than inventing new colors.

### Testing

40 backend tests (up from 28), 10 ml-service tests (up from 5, including a test that forcing a glossary term actually appears in output — true regardless of model quality, which is what makes it meaningful with the tiny test checkpoint). All new endpoints follow the same tested patterns as Phase 1: real SQL against SQLite, dependency-injected fakes for ml-service/S3 where needed.

### What's still open after Phase 2

- Corrections aren't yet fed back into any retraining/fine-tuning loop — they're captured and queryable, not yet used to improve the model. That's the natural next step once a training pipeline exists.
- The glossary is small and hand-curated (a handful of terms, three domains, four language pairs) — proves the mechanism, not a production terminology database.
- No dedicated username/display-name field — community attribution uses email local-parts as a stand-in.
- The Community page's discussion forum remains entirely mock; a real one is a distinct feature, not attempted here.
- Analytics are personal-only; there's no admin/global view across all users yet.

---

## Phase 3 progress log (2026-07-10)

Phase 3 targeted the roadmap's scale items: async DB access, caching, ml-service batching, and billing. Kubernetes/Elasticsearch were explicitly left out — the roadmap itself scoped those as "if traffic justifies it," and nothing about this project's current traffic does.

### Batch translation

- `ml-service`'s `/translate` and the new `/translate/batch` now share one `_generate()` helper. Items needing glossary term-forcing are translated individually (`force_words_ids` applies uniformly across a whole `generate()` call, so items needing different forced terms can't share one batched call); everything else is grouped by `(source_lang, target_lang)` and translated in a single real batched `generate()` call per group — genuine batching, not a loop dressed up as one.
- Backend adds `POST /translate/batch` (up to 50 items, persists each as its own `Translation` row) and real `GET /languages` / `GET /models` endpoints proxied from `ml-service` — closing two gaps `ApiDocs.tsx` had been advertising since the original audit. Rewrote that page's endpoint list and code samples to match what's actually real (correct paths, `X-API-Key` instead of a fictional `Bearer` scheme, no more `api.nmtplatform.com`).

### Caching

- New Redis-backed `CacheClient` (`app/cache.py`): identical `(text, source_lang, target_lang, domain)` requests skip the `ml-service` call entirely. Caching is explicitly an optimization, not a correctness requirement — every Redis call is wrapped so a Redis outage degrades to "no caching," never a failed request. Verified twice: once with a fake in dependency-injected tests (confirms `ml-service` is called exactly once across two identical requests), and once against a real Redis container (miss → set → hit → key-differentiation, all directly exercised).
- Every translation still persists its own `Translation` row regardless of cache hit/miss — caching the model call is an implementation detail, not something that should hide a user's own history of what they translated and when.

### Async DB access

The highest-risk item this phase — it touches `database.py`, `deps.py`, and every route file, and has a real subtlety: SQLAlchemy's async mode can't lazy-load a relationship outside an `await` (raises `MissingGreenlet`), so `User.role` needed explicit `selectinload(...)` everywhere it's read downstream (RBAC checks, `UserRead` serialization). Converted one module at a time, running the full test suite after each step rather than batching the whole thing and hoping.

The full test suite passed against SQLite on the first run (51/51) — which is exactly why the Postgres check mattered more than usual: SQLite passing doesn't prove the async Postgres driver behaves identically, and in fact it didn't. Verifying live against a real Postgres container surfaced a genuine bug the SQLite suite couldn't see:

- **`datetime.now(timezone.utc)` into a naive `DateTime` column**: `psycopg2` (the sync driver) silently tolerated inserting a timezone-aware datetime into a `TIMESTAMP WITHOUT TIME ZONE` column; `asyncpg` correctly rejects it (`DataError: can't subtract offset-naive and offset-aware datetimes`). Fixed by making all six `created_at` columns `DateTime(timezone=True)` (migration `0005`) — fixing the column type, not stripping the timezone from the datetimes, since timezone-aware storage is the actually-correct practice.

After that fix, the entire flow was re-verified live against real Postgres: register → login → `/me` (exercises the `role` eager-load) → API key creation → RBAC 403s → `/translate` (persisted) → `/translate/history` → `/translate/batch` → `/datasets` → `/community/stats` → `/analytics/summary`, all against `postgresql+asyncpg://`, then torn down cleanly.

`DATABASE_URL` itself is unchanged (`postgresql+psycopg2://...`) — the app converts it to the async driver internally (`database.py`'s `to_async_url`), and Alembic keeps using the sync form directly, so no deployment config needed to change.

### Billing (Stripe) — the one item not fully verified

`app/billing_client.py` + `POST /billing/checkout-session` + `POST /billing/webhook` implement Checkout session creation and webhook-driven quota updates (mapping a purchased Stripe price ID to an API key's `quota_limit` — the same field Phase 0 built and left unenforced-by-a-purchase-flow until now). Tested against a fake Stripe client using the same dependency-injection pattern as `MLServiceClient`/S3/Redis.

Unlike everything else in this project's audit trail, this one **could not be verified against the real external API** — there are no Stripe test-mode credentials in this development environment. Rather than either skip it silently or pretend it's proven, it's shipped tested-with-a-fake and clearly labeled: see `backend/README.md`'s billing section for exactly what would need to happen (real `STRIPE_SECRET_KEY`/`STRIPE_WEBHOOK_SECRET`, a real webhook pointed at `/billing/webhook`, one real test-mode checkout walked through end-to-end) before this is production-ready. The frontend Pricing page is deliberately left without a wired "Subscribe" button for the same reason — wiring it to an unverified backend would recreate the exact "UI that pretends to work" pattern the original audit exists to call out.

### Testing

58 backend tests (up from 40), all passing against both the SQLite test suite and — for the parts that matter most (auth, RBAC, persistence) — directly re-verified against real Postgres.

### What's still open after Phase 3

- Billing is code-complete and unit-tested but not verified against the real Stripe API (see above) — needs real credentials to close out.
- `ml_client`'s HTTP calls to `ml-service` are still synchronous (`httpx.post`, not `httpx.AsyncClient`) even though the route handling them is now `async def` — the DB layer no longer blocks the event loop, but a slow `ml-service` response still would. Converting `MLServiceClient` to use `httpx.AsyncClient` is a natural, contained follow-up.
- Kubernetes/Elasticsearch remain out of scope, per the roadmap's own framing — revisit if/when real traffic justifies them.

---

## Post-Phase-3 backlog clearance (2026-07-10 onward)

Working through everything flagged as "remaining" across Phases 0–3, batched and tested one batch at a time. Explicit constraint for this pass: every optional integration (email, OAuth, billing) must leave the app fully functional whether or not real credentials are configured — degrade gracefully, never crash or block other features.

### Batch 1 — Auth hardening

- **JWT moved off `localStorage` to an httpOnly cookie.** `/auth/login` sets it, `/auth/logout` clears it; API/CLI consumers keep using a plain Bearer header, which wins over the cookie if a request somehow carries both (`deps.py`'s `get_token_from_request`). Frontend `AuthContext` no longer holds a token at all — it calls `/auth/me` on mount to discover whether the ambient cookie is valid, since JS can't read an httpOnly cookie itself.
  - Real bug found via testing: `TestClient`'s cookie jar persists across requests within a test, so a stale cookie from an earlier login was silently overriding explicit `Authorization` headers in existing tests (and would do the same for any real API client sharing an origin) — fixed by making an explicit Bearer header always take precedence over the ambient cookie.
- **Bootstrap admin** via `FIRST_ADMIN_EMAIL`: that email is promoted to admin at registration time; unset by default, in which case nothing changes for anyone.
- **Password reset** and **email verification**, both via a shared `AuthToken` table (single-use, expiring) and a new `EmailClient` (`app/email_client.py`) that logs the email it would have sent when `SMTP_HOST` isn't configured, rather than failing.
  - Real bug found via testing: SQLite (`aiosqlite`) doesn't round-trip `tzinfo` for a `DateTime(timezone=True)` column the way Postgres/`asyncpg` does — token-expiry comparisons crashed with `TypeError: can't compare offset-naive and offset-aware datetimes` on SQLite only. Fixed by normalizing to UTC-aware before comparing, tolerant of either.
  - Also found: the backend never called `logging.basicConfig()`, so the email fallback's `logger.info()` calls were silently dropped — the entire point of "log instead of failing" wasn't actually visible. Fixed.
- New frontend pages: `/forgot-password`, `/reset-password`, `/verify-email`.
- Verified live end-to-end against real Postgres: register → login (real cookie) → `/me` via cookie alone → forgot-password (real logged reset link) → reset-password with that real token → login with the new password (and old one correctly rejected) → email verification → logout clearing the cookie.

### Batch 2 — OAuth (Google + GitHub)

- `app/oauth_client.py`: a plain Authorization Code flow over `httpx` (not a third-party OAuth library — both providers are well-documented plain HTTP APIs, and this matches the rest of the codebase's dependency footprint). CSRF-protected via a short-lived `state` value round-tripped through an httpOnly cookie scoped to the OAuth path.
- `User.hashed_password` is now nullable (OAuth-only accounts have none); new `oauth_provider`/`oauth_subject` columns with a unique index (migration `0007`). Signing in via a provider links to an existing password-based account sharing that email rather than creating a duplicate.
- `GET /auth/oauth/providers` reports which providers are actually configured; the frontend login page uses this to show disabled/labeled buttons for unavailable providers instead of offering a button that 503s — directly satisfying "works whether credentials are provided or not."
- Tested against fakes (there's no way to drive a real OAuth consent screen from an automated test) covering: new-account creation, returning-user reuse, linking to an existing password account, state-mismatch rejection, provider-failure handling, and the case where an OAuth-only account correctly can't log in with a password.
- Verified live against real Postgres **with no Google/GitHub credentials configured at all** — the specific scenario this batch was constrained to support: app boots normally, `/auth/oauth/providers` correctly reports both `false`, login attempts return a clean 503 instead of crashing, and normal email/password registration is completely unaffected.

### Batch 3 — GDPR/privacy real backend

- `GET/PUT /privacy/settings`: real persisted consent preferences (new `PrivacySettings` table, one row per user, created lazily on first access) — `PrivacyDashboard.tsx`'s toggles now actually save instead of resetting on refresh.
- `GET /privacy/export`: a real, **immediate** JSON download of everything the user's own account touches — profile, translations, feedback given, corrections given, datasets uploaded, API keys — replacing the old fake "we'll email it within 24 hours" promise with something both more honest and better UX.
- `POST /privacy/delete-account`: anonymizes rather than hard-deletes (email scrubbed to `deleted-user-{id}-{random}@deleted.local`, password cleared, account deactivated, API keys revoked) instead of cascading a real delete through translations/corrections/dataset uploads that other parts of the system (community stats, the review queue, other users' downloads) legitimately still reference. GDPR erasure doesn't require destroying data once it's anonymized.
- `POST/GET /privacy/gdpr-requests`: a real `GdprRequest` log. `access`/`portability` auto-complete immediately (already fully served by the export endpoint above); `rectification`/`restrict`/`object` are recorded and stay `pending` — there's no admin review UI for those yet, an honestly-labeled gap rather than a silent one.
- Frontend: `PrivacyDashboard.tsx` and `GdprRequestForm.tsx` rewritten to call these endpoints for real (both routes now behind `ProtectedRoute`, since they call authenticated endpoints and weren't gated before).
- Verified live end-to-end against real Postgres: default settings → update persists → real data export → GDPR access request auto-completing → account deletion → old session correctly rejected → the anonymized email immediately free to re-register.

### Batch 4 — Product completeness

- **DB-backed glossary** (new `GlossaryTerm` table, migration `0009`, seeded with the 27 terms ml-service previously hardcoded — no regression on upgrade). New `GET/POST/DELETE /glossary` routes (writes admin-only); `app/glossary.py`'s `resolve_forced_terms()` looks up matches and passes them to ml-service's `forced_terms` override, which now takes precedence over ml-service's own (now-vestigial, still-present-as-fallback) internal dict. Deliberately returns `None` (not `[]`) for auto-detect requests, since matching needs the actual source language — ml-service falls back to its own small static glossary only in that one case, a documented limitation rather than a silent gap.
- **Display name** (`User.display_name`, migration `0010`, nullable, editable via `PATCH /auth/me`): community leaderboards and the new forum now show it in place of the email-local-part fallback when set. Shared `app/handles.py::public_handle()` used by both. Frontend: new "Profile" tab on the Privacy Dashboard.
- **Real community forum** — `ForumPost`/`ForumReply` tables (migration `0011`), five fixed categories. `GET /forum/categories` (counts), `GET/POST /forum/posts`, `GET /forum/posts/{id}` (with replies), `POST /forum/posts/{id}/replies` (writes require auth). `Community.tsx` rewritten off its mock data onto these; new `/community/posts/:postId` detail page and a "New Topic" dialog.
- **Admin/global analytics** — `GET /analytics/global` (admin-only), sharing the same aggregation helper as the personal `/analytics/summary` endpoint, extended with `total_users`/`total_datasets`. `Analytics.tsx` shows a "My Analytics" / "Platform-wide" tab switcher for admins only.
- **Dataset upload format validation** — extension allowlist (`.tsv`, `.csv`, `.txt`, `.json`, `.jsonl`, `.tmx`, `.xliff`, `.xlf`) enforced in `datasets.py` before the file ever reaches storage; frontend file input's `accept` attribute matches.
- 23 new backend tests across glossary, display-name, forum, global analytics, and dataset validation — full suite (121 tests) green throughout.
- Verified live against real Postgres with **zero optional credentials configured**: ran all 5 new migrations from a clean database (including the glossary seed data), bootstrap-admin registration, glossary CRUD, display-name update reflected in a forum post's `author_handle`, forum post+reply+detail+category-count round trip, global analytics, and the dataset extension allowlist correctly rejecting a `.exe` before touching S3.

### Batch 5 — Infra polish

- **Async `ml_client`**: `MLServiceClient` converted from synchronous `httpx.post`/`httpx.get` calls to `httpx.AsyncClient`; all four methods (`translate`, `translate_batch`, `get_languages`, `get_health`) are now `async def` and awaited from the route handlers. A slow or hanging ml-service call no longer blocks the event loop out from under every other concurrent request. `FakeMLClient` in `conftest.py` updated to match (async methods); the pre-existing `_BrokenMLClient` unavailability test needed no change since its synchronous `raise` happens before the `await` is ever reached.
- **Stripe hardening**: `StripeClient` gained `is_configured`/`webhook_is_configured` properties (mirroring `EmailClient`/`OAuthClient`'s existing pattern), checked in both `billing_client.py` itself (fails fast with a `BillingError` before ever attempting a real Stripe API call with empty credentials) and again explicitly in the `billing.py` routes for a clear 503 rather than an incidental one. Previously an unconfigured server would still attempt a live network call to Stripe with an empty key and surface whatever `stripe.error.AuthenticationError` came back — functionally a 503 either way, but now fast and explicit rather than dependent on a real network round trip.
- 8 new backend tests (unit tests directly against `StripeClient`, plus route-level 503 tests for both `checkout-session` and `webhook`) — full suite (127 tests) green throughout.
- **Frontend Pricing page** rewritten off its fully-static mock: fetches `GET /billing/plans` on load. The Free tier's CTA and Enterprise's "Contact Sales" never depended on Stripe and are wired to real navigation; the Pro tier's button calls the real checkout-session endpoint against the first configured price when Stripe is set up, and shows "Coming soon" (disabled, with an explanatory caption) when the price map is empty — never a dead or misleading button either way. When more than one price is configured, an additional "Available Subscription Plans" section lists each real `price_id`/quota pair with its own working Subscribe button, since the marketing tiers (Free/Pro/Enterprise) don't have a stable 1:1 mapping to arbitrary admin-configured Stripe prices.
- OAuth login wiring (Batch 2) re-verified as still correct and untouched — `/auth/oauth/providers` continues to drive disabled/labeled buttons on the login page.
- Verified live against real Postgres with **zero Stripe/ml-service configuration**: `POST /translate` against a real (absent) ml-service correctly round-tripped a fast, clean 503 through the new async client instead of hanging; `GET /billing/plans` returned `[]`; `POST /billing/checkout-session` 503'd immediately without an outbound Stripe call. Re-ran with `STRIPE_PRICE_QUOTA_MAP` set but `STRIPE_SECRET_KEY` still empty — plans listed correctly, checkout-session still 503'd cleanly and fast rather than attempting (and failing) a real Stripe call.
- ml-service itself untouched in this batch; its test suite was fully verified earlier in this backlog-clearance pass (19 tests, including the new `forced_terms` override tests from Batch 4's glossary work) and no ml-service files changed since.

### Batch 6 — Live-testing fallout: email case-sensitivity, footer links, blog CMS, admin panel

Found and fixed while walking through the running app end-to-end for the first time:

- **Email case-sensitivity bug** (found live, not by unit tests): register/login/forgot-password/OAuth-linking all did exact-match email lookups, so a login attempt with different casing than what was stored (e.g. a browser auto-capitalizing the first letter) failed as an indistinguishable "wrong password" 401. Fixed with a single `normalize_email()` helper (`app/security.py`) applied at every email entry point — lowercases and trims before storage or lookup. 4 new regression tests.
- **Footer 404s**: `Footer.tsx` linked to `/privacy`, `/terms`, `/cookies`, `/gdpr` — none of which are real routes (the actual pages are at `/privacy-policy`, `/terms-of-service`, `/cookie-policy`, `/gdpr-compliance`). Fixed all four. Also removed a `/documentation` link that pointed at a page that was never built and is redundant with the existing `/api-docs` link elsewhere in the footer.
- **Real blog CMS**: the old `/blog` page was 100% hardcoded marketing fiction (fictional authors, fake view counts, a non-functional newsletter form) with no way to actually create or publish anything. Replaced with: `BlogPost` model (migration `0012`, `draft`/`published` status, auto-generated unique slugs with collision suffixing), public routes (`GET /blog/posts`, `GET /blog/posts/{slug}` — published-only, 404 on drafts) and admin-only routes (`GET/POST/PATCH/DELETE /blog/admin/posts...`) in `blog.py`. Frontend: real `Blog.tsx` list + new `/blog/:slug` detail page, both rendering actual published posts (or an honest empty state).
- **Admin panel** (`/admin`, new route, admin-only): three tabs — **Users** (list all accounts, change role, activate/deactivate — a user cannot deactivate their own account), **Glossary** (a real UI over the Batch-4 CRUD API that previously only existed via Swagger), **Blog** (create/edit/publish/delete posts). New `admin.py` route file: `GET /admin/users`, `PATCH /admin/users/{id}`. `ProtectedRoute` gained an `adminOnly` prop; `NavBar` shows an "Admin" link only for admin-role users.
- 20 new backend tests (4 email-normalization, 8 blog, 8 admin-user-management) — full suite (146 tests) green throughout.
- Verified live against the real running stack (not just a throwaway container): rebuilt and restarted the actual docker-compose `backend` service twice — migration `0011 → 0012` applied cleanly against the live database; confirmed both the case-sensitivity fix and its absence beforehand via direct reproduction (capitalized email 401'd before the fix, 200'd after); exercised `/admin/users`, blog post creation+publishing, and the public blog list end-to-end against the live server, then confirmed the pre-existing glossary endpoint was unaffected.
- Caught mid-session that the docker-compose `backend` service has no source volume mount — code edits require an explicit `docker compose up --build backend` to take effect, they don't hot-reload like the separately-run frontend dev server does. Worth knowing for any future live debugging against this stack.

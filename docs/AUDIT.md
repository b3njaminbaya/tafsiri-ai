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

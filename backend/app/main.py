import logging

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from .core.config import settings
from .core.limiter import limiter

# Without this, app-level logger.info() calls (e.g. EmailClient logging the
# email it would have sent when SMTP isn't configured) are silently dropped —
# Python's root logger defaults to WARNING with no handler attached.
logging.basicConfig(level=logging.INFO)
from .api.v1.routes import analytics as analytics_routes
from .api.v1.routes import auth as auth_routes
from .api.v1.routes import billing as billing_routes
from .api.v1.routes import community as community_routes
from .api.v1.routes import datasets as datasets_routes
from .api.v1.routes import forum as forum_routes
from .api.v1.routes import glossary as glossary_routes
from .api.v1.routes import meta as meta_routes
from .api.v1.routes import privacy as privacy_routes
from .api.v1.routes import review as review_routes
from .api.v1.routes import translate as translate_routes

tags_metadata = [
    {
        "name": "auth",
        "description": "Register/Login with email/password. OAuth providers will be added later. Includes API key management.",
    },
    {
        "name": "translation",
        "description": "Text translation via ml-service, with history and feedback.",
    },
    {
        "name": "datasets",
        "description": "Upload and browse parallel-corpus datasets, stored in MinIO/S3.",
    },
    {
        "name": "review",
        "description": "Active-learning review queue for low-confidence translations (translator/admin roles).",
    },
    {
        "name": "community",
        "description": "Public community contribution stats and leaderboards.",
    },
    {
        "name": "analytics",
        "description": "Personal translation analytics for the current user.",
    },
    {
        "name": "billing",
        "description": "Stripe-backed subscription checkout and webhook handling.",
    },
    {
        "name": "privacy",
        "description": "GDPR data export/erasure requests and privacy/consent settings.",
    },
    {
        "name": "glossary",
        "description": "Admin-managed domain terminology forced into translation output.",
    },
    {
        "name": "forum",
        "description": "Community discussion posts and replies.",
    },
]

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    openapi_tags=tags_metadata,
    description="API for the NMT Agent for Low-Resource Languages.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Schema is managed by Alembic — run `alembic upgrade head` before starting the app
# (see backend/README.md). No create_all() here; migrations are the single source
# of truth for table structure.

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_routes.router)
api_router.include_router(translate_routes.router)
api_router.include_router(datasets_routes.router)
api_router.include_router(review_routes.router)
api_router.include_router(community_routes.router)
api_router.include_router(analytics_routes.router)
api_router.include_router(meta_routes.router)
api_router.include_router(billing_routes.router)
api_router.include_router(privacy_routes.router)
api_router.include_router(glossary_routes.router)
api_router.include_router(forum_routes.router)
app.include_router(api_router)

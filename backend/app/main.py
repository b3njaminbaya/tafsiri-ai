from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from .core.config import settings
from .core.limiter import limiter
from .api.v1.routes import auth as auth_routes
from .api.v1.routes import datasets as datasets_routes
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
app.include_router(api_router)

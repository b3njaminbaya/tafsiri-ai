from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)

    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    display_name = Column(String(50), nullable=True)
    # Nullable: OAuth-only accounts (Google/GitHub) never set a password.
    hashed_password = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    # Set together when an account was created (or linked) via OAuth; both
    # NULL for a plain email/password account. Multiple NULLs are fine under
    # a unique index on both Postgres and SQLite.
    oauth_provider = Column(String(32), nullable=True)
    oauth_subject = Column(String(255), nullable=True)

    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role", back_populates="users")

    api_keys = relationship("APIKey", back_populates="user")

class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    quota_used = Column(Integer, default=0)
    quota_limit = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="api_keys")

class Translation(Base):
    __tablename__ = "translations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    source_lang = Column(String(16), nullable=True)
    target_lang = Column(String(16), nullable=False)
    domain = Column(String(32), nullable=True)
    input_text = Column(Text, nullable=False)
    output_text = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    user = relationship("User")
    feedback_entries = relationship(
        "Feedback", back_populates="translation", cascade="all, delete-orphan"
    )

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    translation_id = Column(Integer, ForeignKey("translations.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    user = relationship("User")
    translation = relationship("Translation", back_populates="feedback_entries")

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source_lang = Column(String(16), nullable=True)
    target_lang = Column(String(16), nullable=True)
    domain = Column(String(32), nullable=True)
    storage_key = Column(String(512), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    uploaded_by = relationship("User")

class Correction(Base):
    """A reviewer-submitted correction for a low-confidence translation —
    the active-learning review queue's output. Reviewing is restricted to
    the translator/admin roles (see require_any_role in deps.py).
    """
    __tablename__ = "corrections"
    id = Column(Integer, primary_key=True, index=True)
    translation_id = Column(Integer, ForeignKey("translations.id"), nullable=False, index=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    corrected_text = Column(Text, nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    translation = relationship("Translation")
    reviewer = relationship("User")

class AuthToken(Base):
    """Single-use tokens for password reset and email verification. One
    table, distinguished by `purpose`, rather than two near-identical tables.
    """
    __tablename__ = "auth_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    purpose = Column(String(32), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    user = relationship("User")

class PrivacySettings(Base):
    """One row per user — the real backing store for what PrivacyDashboard.tsx
    used to only hold in component state (lost on refresh).
    """
    __tablename__ = "privacy_settings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    analytics = Column(Boolean, default=True, nullable=False)
    marketing = Column(Boolean, default=False, nullable=False)
    functional = Column(Boolean, default=True, nullable=False)
    email_marketing = Column(Boolean, default=False, nullable=False)
    sms_marketing = Column(Boolean, default=False, nullable=False)
    push_notifications = Column(Boolean, default=True, nullable=False)
    data_collection = Column(Boolean, default=True, nullable=False)
    location_tracking = Column(Boolean, default=False, nullable=False)
    third_party_sharing = Column(Boolean, default=False, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False)

    user = relationship("User")

class GdprRequest(Base):
    """A logged data-rights request. access/portability are fulfilled
    immediately via GET /privacy/export; the rest (rectification, restrict,
    object) need a human and stay 'pending' — there's no admin review UI for
    those yet, a real gap noted in docs/AUDIT.md.
    """
    __tablename__ = "gdpr_requests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    request_type = Column(String(32), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(16), default="pending", nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User")

FORUM_CATEGORIES = (
    "general",
    "technical",
    "feature_requests",
    "model_training",
    "dataset_sharing",
)

class ForumPost(Base):
    __tablename__ = "forum_posts"
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category = Column(String(32), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    author = relationship("User")
    replies = relationship(
        "ForumReply", back_populates="post", cascade="all, delete-orphan", order_by="ForumReply.id"
    )

class ForumReply(Base):
    __tablename__ = "forum_replies"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("forum_posts.id"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    author = relationship("User")
    post = relationship("ForumPost", back_populates="replies")

class GlossaryTerm(Base):
    """Admin-managed domain terminology. The backend owns this data and
    resolves matches itself (source_term appears as a whole word in the
    input), passing the resolved target terms to ml-service's `forced_terms`
    override — ml-service still does the actual constrained decoding, it
    just no longer owns the glossary data. Replaces the small hardcoded
    dict ml-service shipped with in Phase 2.
    """
    __tablename__ = "glossary_terms"
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(32), nullable=False, index=True)
    source_lang = Column(String(16), nullable=False)
    target_lang = Column(String(16), nullable=False)
    source_term = Column(String(255), nullable=False)
    target_term = Column(String(255), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    created_by = relationship("User")

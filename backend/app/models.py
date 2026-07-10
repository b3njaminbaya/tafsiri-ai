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
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)

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
    created_at = Column(DateTime, default=_utcnow)

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
    created_at = Column(DateTime, default=_utcnow, nullable=False)

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
    created_at = Column(DateTime, default=_utcnow, nullable=False)

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
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    uploaded_by = relationship("User")

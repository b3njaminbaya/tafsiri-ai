from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class RoleRead(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime
    role: Optional[RoleRead]

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None

class APIKeyRead(BaseModel):
    id: int
    key: str
    is_active: bool
    quota_used: int
    quota_limit: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class APIKeyCreateResponse(BaseModel):
    message: str = "API key created"
    api_key: APIKeyRead

class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    source_lang: Optional[str] = Field(None, max_length=16)
    target_lang: str = Field(..., max_length=16)
    domain: Optional[str] = Field(None, max_length=32)

class TranslateResponse(BaseModel):
    translation: str
    source_lang: Optional[str] = None
    target_lang: str
    domain: Optional[str] = None
    confidence: float

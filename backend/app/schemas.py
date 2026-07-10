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
    id: int
    translation: str
    source_lang: Optional[str] = None
    target_lang: str
    domain: Optional[str] = None
    confidence: float
    applied_glossary_terms: List[str] = []

class TranslationRead(BaseModel):
    id: int
    source_lang: Optional[str]
    target_lang: str
    domain: Optional[str]
    input_text: str
    output_text: str
    confidence: float
    created_at: datetime

    class Config:
        from_attributes = True

class FeedbackCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=2000)

class FeedbackRead(BaseModel):
    id: int
    translation_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class DatasetRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    source_lang: Optional[str]
    target_lang: Optional[str]
    domain: Optional[str]
    size_bytes: int
    uploaded_by_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DatasetDownloadResponse(BaseModel):
    url: str
    expires_in_seconds: int

class CorrectionCreate(BaseModel):
    corrected_text: str = Field(..., min_length=1, max_length=5000)
    note: Optional[str] = Field(None, max_length=2000)

class CorrectionRead(BaseModel):
    id: int
    translation_id: int
    reviewer_id: int
    corrected_text: str
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ContributorCount(BaseModel):
    handle: str
    count: int

class CommunityStats(BaseModel):
    total_datasets: int
    total_translations: int
    total_corrections: int
    total_contributors: int
    top_dataset_contributors: List[ContributorCount]
    top_reviewers: List[ContributorCount]

class DailyCount(BaseModel):
    date: str
    count: int

class LanguagePairCount(BaseModel):
    source_lang: Optional[str]
    target_lang: str
    count: int

class RatingBreakdown(BaseModel):
    rating: int
    count: int

class AnalyticsSummary(BaseModel):
    total_translations: int
    average_confidence: float
    translations_by_day: List[DailyCount]
    top_language_pairs: List[LanguagePairCount]
    feedback_breakdown: List[RatingBreakdown]

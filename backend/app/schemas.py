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
    password: str = Field(..., min_length=8, max_length=128)

class UserRead(BaseModel):
    id: int
    email: EmailStr
    display_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    role: Optional[RoleRead]

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=50)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)

class VerifyEmailRequest(BaseModel):
    token: str

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
    cached: bool = False

class BatchTranslateRequest(BaseModel):
    items: List[TranslateRequest] = Field(..., min_length=1, max_length=50)

class BatchTranslateResponse(BaseModel):
    results: List[TranslateResponse]

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

class GlobalAnalyticsSummary(AnalyticsSummary):
    total_users: int
    total_datasets: int

class PlanRead(BaseModel):
    price_id: str
    quota_limit: int

class CheckoutSessionRequest(BaseModel):
    price_id: str

class CheckoutSessionResponse(BaseModel):
    checkout_url: str

class PrivacySettingsRead(BaseModel):
    analytics: bool
    marketing: bool
    functional: bool
    email_marketing: bool
    sms_marketing: bool
    push_notifications: bool
    data_collection: bool
    location_tracking: bool
    third_party_sharing: bool

    class Config:
        from_attributes = True

class PrivacySettingsUpdate(BaseModel):
    analytics: Optional[bool] = None
    marketing: Optional[bool] = None
    functional: Optional[bool] = None
    email_marketing: Optional[bool] = None
    sms_marketing: Optional[bool] = None
    push_notifications: Optional[bool] = None
    data_collection: Optional[bool] = None
    location_tracking: Optional[bool] = None
    third_party_sharing: Optional[bool] = None

GDPR_REQUEST_TYPES = ("access", "rectification", "erasure", "restrict", "portability", "object")

class GdprRequestCreate(BaseModel):
    request_type: str = Field(..., pattern="^(" + "|".join(GDPR_REQUEST_TYPES) + ")$")
    description: Optional[str] = Field(None, max_length=2000)

class GdprRequestRead(BaseModel):
    id: int
    request_type: str
    description: Optional[str]
    status: str
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True

class DataExport(BaseModel):
    user: UserRead
    translations: List[TranslationRead]
    feedback_given: List[FeedbackRead]
    corrections_given: List[CorrectionRead]
    datasets_uploaded: List[DatasetRead]
    api_keys: List[APIKeyRead]

FORUM_CATEGORIES = ("general", "technical", "feature_requests", "model_training", "dataset_sharing")

class ForumPostCreate(BaseModel):
    category: str = Field(..., pattern="^(" + "|".join(FORUM_CATEGORIES) + ")$")
    title: str = Field(..., min_length=1, max_length=255)
    body: str = Field(..., min_length=1, max_length=10000)

class ForumReplyCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=10000)

class ForumReplyRead(BaseModel):
    id: int
    post_id: int
    author_handle: str
    body: str
    created_at: datetime

    class Config:
        from_attributes = True

class ForumPostRead(BaseModel):
    id: int
    category: str
    title: str
    author_handle: str
    reply_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class ForumPostDetail(BaseModel):
    id: int
    category: str
    title: str
    body: str
    author_handle: str
    created_at: datetime
    replies: List[ForumReplyRead]

    class Config:
        from_attributes = True

class ForumCategoryCount(BaseModel):
    category: str
    post_count: int

class GlossaryTermCreate(BaseModel):
    domain: str = Field(..., max_length=32)
    source_lang: str = Field(..., max_length=16)
    target_lang: str = Field(..., max_length=16)
    source_term: str = Field(..., min_length=1, max_length=255)
    target_term: str = Field(..., min_length=1, max_length=255)

class GlossaryTermRead(BaseModel):
    id: int
    domain: str
    source_lang: str
    target_lang: str
    source_term: str
    target_term: str
    created_by_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

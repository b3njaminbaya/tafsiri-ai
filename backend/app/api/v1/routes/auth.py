from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from secrets import token_urlsafe

from .... import schemas
from ....models import User, Role, APIKey
from ....security import get_password_hash, verify_password, create_access_token
from ....deps import get_db, get_current_active_user, require_role
from ....core.limiter import limiter

router = APIRouter(prefix="/auth", tags=["auth"])

# Default roles (admin/translator/user) are seeded by the initial Alembic
# migration (20260710_0001_initial_schema) — not created at request time.

@router.post("/register", response_model=schemas.UserRead, summary="Register with email/password")
@limiter.limit("10/minute")
def register(request: Request, user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    default_role = db.query(Role).filter(Role.name == "user").first()
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=default_role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=schemas.Token, summary="Obtain JWT access token")
@limiter.limit("5/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    token = create_access_token(subject=str(user.id))
    return schemas.Token(access_token=token)

@router.get("/me", response_model=schemas.UserRead, summary="Get current user")
def me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.post("/api-keys", response_model=schemas.APIKeyCreateResponse, summary="Create an API key")
def create_api_key(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    key_value = token_urlsafe(32)
    api_key = APIKey(key=key_value, user_id=current_user.id, is_active=True)
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return schemas.APIKeyCreateResponse(api_key=api_key)

@router.get("/api-keys", response_model=list[schemas.APIKeyRead], summary="List my API keys")
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()
    return keys

@router.post("/api-keys/{key_id}/revoke", summary="Revoke an API key")
def revoke_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    key = db.query(APIKey).filter(APIKey.id == key_id, APIKey.user_id == current_user.id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    key.is_active = False
    db.commit()
    return {"message": "API key revoked"}

@router.post("/promote/{user_id}", summary="Promote a user to translator", dependencies=[Depends(require_role("admin"))])
def promote_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    translator_role = db.query(Role).filter(Role.name == "translator").first()
    user.role = translator_role
    db.commit()
    return {"message": "User promoted"}

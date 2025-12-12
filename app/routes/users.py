from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_current_active_user,
    get_password_hash,
    verify_password,
)
from ..core.config import get_settings
from ..database import get_db
from ..models import Match, Session, Strategy, User
from ..schemas import (
    DashboardPayload,
    MatchResponse,
    StrategyResponse,
    SessionResponse,
    TokenRefresh,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    existing = (
        db.query(User)
        .filter((User.username == data.username) | (User.email == data.email))
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse.from_orm(user)


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    expires_at = datetime.utcnow() + timedelta(
        minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
        user_id=user.id,
        username=user.username,
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(current_user: User = Depends(get_current_active_user)) -> dict:
    return {"detail": f"User {current_user.username} logged out"}


@router.post("/token/refresh", response_model=TokenResponse)
def refresh_token(payload: TokenRefresh, db: Session = Depends(get_db)) -> TokenResponse:
    decoded = decode_refresh_token(payload.refresh_token)
    username = decoded.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    expires_at = datetime.utcnow() + timedelta(
        minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
        user_id=user.id,
        username=user.username,
    )


@router.get("/dashboard", response_model=DashboardPayload)
def dashboard_data(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> DashboardPayload:
    matches = (
        db.query(Match)
        .filter(Match.user_id == current_user.id)
        .order_by(Match.created_at.desc())
        .all()
    )
    strategies = (
        db.query(Strategy)
        .filter(Strategy.user_id == current_user.id)
        .order_by(Strategy.created_at.desc())
        .all()
    )
    sessions = (
        db.query(Session)
        .filter(Session.user_id == current_user.id)
        .order_by(Session.created_at.desc())
        .all()
    )
    match_payload = [MatchResponse.from_orm(match) for match in matches]
    strategy_payload = [StrategyResponse.from_orm(strategy) for strategy in strategies]
    session_payload = [SessionResponse.from_orm(session) for session in sessions]
    return DashboardPayload(
        user=UserResponse.from_orm(current_user),
        matches=match_payload,
        strategies=strategy_payload,
        sessions=session_payload,
    )

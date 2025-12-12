from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field("bearer")
    expires_at: datetime
    user_id: int
    username: str


class TokenRefresh(BaseModel):
    refresh_token: str


class MatchBase(BaseModel):
    map: str = Field(..., min_length=1, max_length=100)
    agent: str = Field(..., min_length=1, max_length=50)
    score: int = Field(..., ge=0, le=10)
    notes: Optional[str] = Field(None, max_length=500)


class MatchCreate(MatchBase):
    pass


class MatchResponse(MatchBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StrategyBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=128)
    description: Optional[str] = Field(None, max_length=1000)


class StrategyCreate(StrategyBase):
    pass


class StrategyResponse(StrategyBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SessionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=128)
    focus_area: str = Field(..., min_length=1, max_length=128)
    duration_minutes: int = Field(..., ge=0, le=600)
    notes: Optional[str] = Field(None, max_length=1000)


class SessionCreate(SessionBase):
    pass


class SessionResponse(SessionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DashboardPayload(BaseModel):
    user: UserResponse
    matches: List[MatchResponse]
    strategies: List[StrategyResponse]
    sessions: List[SessionResponse]

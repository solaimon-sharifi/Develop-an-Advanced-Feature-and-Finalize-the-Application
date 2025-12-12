from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session as DbSession

from ..auth import get_current_active_user
from ..database import get_db
from ..models import Session as ValorantSession
from ..schemas import SessionCreate, SessionResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: SessionCreate,
    db: DbSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> SessionResponse:
    session = ValorantSession(
        title=payload.title,
        focus_area=payload.focus_area,
        duration_minutes=payload.duration_minutes,
        notes=payload.notes,
        user_id=current_user.id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/", response_model=List[SessionResponse])
def list_sessions(
    db: DbSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> List[SessionResponse]:
    return (
        db.query(ValorantSession)
        .filter(ValorantSession.user_id == current_user.id)
        .order_by(ValorantSession.created_at.desc())
        .all()
    )

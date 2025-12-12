from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from ..auth import get_current_active_user
from ..database import get_db
from ..models import Match
from ..schemas import MatchCreate, MatchResponse

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def create_match(
    payload: MatchCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> MatchResponse:
    match = Match(
        map=payload.map,
        agent=payload.agent,
        score=payload.score,
        notes=payload.notes,
        user_id=current_user.id,
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


@router.get("/", response_model=List[MatchResponse])
def list_matches(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> List[MatchResponse]:
    return (
        db.query(Match)
        .filter(Match.user_id == current_user.id)
        .order_by(Match.created_at.desc())
        .all()
    )
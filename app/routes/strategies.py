from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from ..auth import get_current_active_user
from ..database import get_db
from ..models import Strategy
from ..schemas import StrategyCreate, StrategyResponse

router = APIRouter(prefix="/strategies", tags=["strategies"])


@router.post("/", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
def create_strategy(
    payload: StrategyCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> StrategyResponse:
    strategy = Strategy(
        title=payload.title,
        description=payload.description,
        user_id=current_user.id,
    )
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    return strategy


@router.get("/", response_model=List[StrategyResponse])
def list_strategies(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> List[StrategyResponse]:
    return (
        db.query(Strategy)
        .filter(Strategy.user_id == current_user.id)
        .order_by(Strategy.created_at.desc())
        .all()
    )


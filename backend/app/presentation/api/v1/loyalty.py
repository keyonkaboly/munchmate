from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.database import get_db
from app.application.services.loyalty_service import get_loyalty_summary, apply_reward_to_order
from app.presentation.schemas.loyalty_schemas import LoyaltySummaryResponse, LoyaltyApplyRequest, LoyaltyApplyResponse


router = APIRouter(prefix="/loyalty", tags=["loyalty"])


@router.get("/{customer_id}", response_model=LoyaltySummaryResponse)
def get_loyalty(customer_id: int, db: Session = Depends(get_db)):
    summary = get_loyalty_summary(db, customer_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Customer not found")
    return summary


@router.post("/apply", response_model=LoyaltyApplyResponse)
def apply_loyalty_reward(data: LoyaltyApplyRequest, db: Session = Depends(get_db)):
    result = apply_reward_to_order(db, data.customer_id, data.order_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return result

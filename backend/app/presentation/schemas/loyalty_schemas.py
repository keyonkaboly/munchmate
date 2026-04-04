from pydantic import BaseModel

class LoyaltySummaryResponse(BaseModel):
    points: int
    reward_percent: int

class LoyaltyApplyRequest(BaseModel):
    customer_id: int
    combined_order_id: str

class LoyaltyApplyResponse(BaseModel):
    applied: bool
    reason: str | None = None
    combined_order_id: str | None = None
    order_total: float | None = None
    discount_percent: int | None = None
    discount_amount: float | None = None
    discounted_total: float | None = None
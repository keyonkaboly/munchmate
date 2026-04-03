from sqlalchemy.orm import Session
from app.infrastructure.database.models import Customer, Order, Payment

MILESTONE_DOLLARS = 500.0
MILESTONE_REWARD_PERCENT = 50


def award_loyalty_for_order(db: Session, order_id: str) -> dict | None:
    existing = db.query(Payment).filter(Payment.order_id == order_id).first()
    if existing:
        return None

    orders = db.query(Order).filter(Order.combined_order_id == order_id).all()
    if not orders:
        return None

    customer_id = orders[0].customer_id
    if customer_id is None:
        return None

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return None

    order_total = round(sum(item.total_cost for item in orders if item.total_cost), 2)
    if order_total <= 0:
        return None

    points_awarded = int(order_total)

    previous_points = customer.loyalty_points
    customer.loyalty_points += points_awarded

    prev_milestones = int(previous_points // MILESTONE_DOLLARS)
    new_milestones = int(customer.loyalty_points // MILESTONE_DOLLARS)
    rewards_to_add = max(0, new_milestones - prev_milestones)
    customer.loyalty_rewards_available += rewards_to_add

    db.commit()
    db.refresh(customer)


def get_loyalty_summary(db: Session, customer_id: int) -> dict | None:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return None

    return {"points": customer.loyalty_points, "reward_percent": MILESTONE_REWARD_PERCENT}


def apply_reward_to_order(db: Session, customer_id: int, order_id: str) -> dict | None:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return None

    orders = db.query(Order).filter(Order.combined_order_id == order_id).all()
    if not orders:
        return {"applied": False, "reason": "order_not_found"}

    if orders[0].customer_id != customer_id:
        return {"applied": False, "reason": "order_not_owned_by_customer"}

    if customer.loyalty_rewards_available <= 0:
        return {"applied": False, "reason": "no_rewards_available"}

    order_total = round(sum(item.total_cost for item in orders if item.total_cost), 2)
    if order_total <= 0:
        return {"applied": False, "reason": "order_total_invalid"}

    raw_discount = round(order_total * (MILESTONE_REWARD_PERCENT / 100.0), 2)
    discount = raw_discount
    discounted_total = round(max(0.0, order_total - discount), 2)

    customer.loyalty_rewards_available -= 1
    db.commit()
    db.refresh(customer)

    return {"combined_order_id": order_id, "order_total": order_total, "discount_percent": MILESTONE_REWARD_PERCENT, "discount_amount": discount, "discounted_total": discounted_total}

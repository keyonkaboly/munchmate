from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.infrastructure.security.hashing import hash_password
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Customer
from app.presentation.schemas.user_schemas import UserCreate

router_auth = APIRouter(prefix="/auth", tags=["auth"])


@router_auth.post("/register")
def register(
    user: UserCreate,
    role: str,
    db: Session = Depends(get_db)
):
    if role not in ["customer", "restaurant_owner"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid role. Must be 'customer' or 'restaurant_owner'."
        )

    hashed_password = hash_password(user.password)

    new_user = Customer(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        user_type="restaurant_manager" if role == "restaurant_owner" else "customer"
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Email or username already exists"
        )

    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": role
    }
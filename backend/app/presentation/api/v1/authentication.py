from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.infrastructure.security.hashing import hash_password, verify_password
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Customer
from app.presentation.schemas.user_schemas import UserCreate, UserLogin

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

@router_auth.post("/login")
def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    user = db.query(Customer).filter(Customer.email == user_credentials.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.user_type
        }
    }
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.infrastructure.security.hashing import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Customer
from app.presentation.schemas.user_schemas import UserCreate, UserLogin, UserUpdate
from datetime import timedelta

from app.application.services.authentication_service import get_current_user

router_auth = APIRouter(prefix="/auth", tags=["auth"])


@router_auth.post("/register")
def register(
    user: UserCreate,
    role: str,
    db: Session = Depends(get_db)
):
    if role not in ["customer", "restaurant_manager"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid role. Must be 'customer' or 'restaurant_manager'."
        )

    hashed_password = hash_password(user.password)

    new_user = Customer(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        user_type = role
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
    response: Response,
    db: Session = Depends(get_db),
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

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )

    return {"message": "Login successful"}

@router_auth.get("/me")
def read_me(current_user: Customer = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username
    }

@router_auth.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}

@router_auth.patch("/me")
def update_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    #check username conflict
    if user_update.username and user_update.username != current_user.username:
        existing_username = db.query(Customer).filter(Customer.username == user_update.username).first()
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already exists")
        current_user.username = user_update.username

    #check email conflict
    if user_update.email and user_update.email != current_user.email:
        existing_email = db.query(Customer).filter(Customer.email == user_update.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
        current_user.email = user_update.email

    #update password
    if user_update.password:
        current_user.password_hash = hash_password(user_update.password)

    db.commit()
    db.refresh(current_user)

    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "user_type": current_user.user_type,
        "message": "Account updated successfully"
    }
from fastapi import APIRouter, Depends, HTTPException
from app.presentation.schemas.user_schemas import UserCreate, UserLogin, UserResponse, RestaurantManagerCreate, RestaurantManagerResponse
from app.infrastructure.database.models import Customer
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.infrastructure.database.database import get_db
from app.infrastructure.security.hashing import hash_password

router_user = APIRouter(prefix="/users", tags=["users"])

"""creating new user so new new data so using post & only returning userresponse, not the password"""
@router_user.post("/", response_model=UserResponse) 
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db) 
):
    
    new_user = Customer(
        email=user.email,
        username=user.username,
        password_hash=hash_password(user.password), 
    )
    
    db.add(new_user) 
    
    try:
        db.commit()
        db.refresh(new_user) 
    except IntegrityError: 
        db.rollback() 
        raise HTTPException(status_code=400, detail="Email or username already exists") 
    
    
    return new_user

"""Creating restaurant manager. Try to commit to db and refresh is fails bc. of duplicate user/email"""
@router_user.post("/restaurant-managers", response_model=RestaurantManagerResponse)
def create_restaurant_manager(user: RestaurantManagerCreate, db: Session = Depends(get_db)):
    new_restaurant_manager = Customer(email=user.email, username=user.username, password_hash=hash_password(user.password), user_type="restaurant_manager", restaurant_manager_restaurant_id=user.restaurant_manager_restaurant_id)

    db.add(new_restaurant_manager)

    try:
        db.commit()
        db.refresh(new_restaurant_manager)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email or username already exists")

    return new_restaurant_manager
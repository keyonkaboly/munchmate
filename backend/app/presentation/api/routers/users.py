from fastapi import APIRouter, Depends, HTTPException
from app.presentation.schemas.user_schemas import UserCreate, UserLogin, UserResponse
from app.infrastructure.database.models import Customer
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.infrastructure.database.database import get_db

router_user = APIRouter(prefix="/users", tags=["users"])

#creating new user so new new data so using post & only returning userresponse, not the password
@router_user.post("/", response_model=UserResponse) #userresponse is from schemas and renturns the set defined already
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db) #get_db creates a new database session & gives it to the route
    #sessiion creates a temproay databse connection for that request
):
    
    new_user = Customer(
        email=user.email,
        username=user.username,
        password_hash=user.password, #this temporary for now 
    )
    
    db.add(new_user) #adds the new user to the database session
    
    try:
        db.commit() #commits the changes to the database
        db.refresh(new_user) #refreshes the new user instance with the data from the database
    except IntegrityError: #raised when a database rule is violated
        db.rollback() #rolls back the changes to the database if there is an integrity error (e.g. duplicate email or username)
        raise HTTPException(status_code=400, detail="Email or username already exists") #400=bad request
    
    
    return new_user
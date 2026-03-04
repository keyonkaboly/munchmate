from fastapi import APIRouter, Depends
from app.presentation.api.user_schemas import UserCreate, UserLogin, UserResponse
from app.infrastructure.database.models import Customer
from sqlalchemy.orm import Session
from app.infrastructure.database.database import get_db

router = APIRouter(prefix="/users", tags=["users"])

#creating new user so new new data so using post & only returning userresponse, not the password
@router.post("/", response_model=UserResponse) #userresponse is from schemas and renturns the set defined already
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db) #get_db creates a new database session & gives it to the route
    #sessiion creates a temproay databse connection for that request
):
    
    new_user = Customer(
        email=user.email,
        username=user.username,
        password=user.password, #this temproy for now 
    )
    
    db.add(new_user) #adds the new user to the database session
    db.commit() #commits the changes to the database
    
    return new_user

    


    

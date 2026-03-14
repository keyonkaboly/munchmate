from fastapi import APIRouter, FastAPI, HTTPException, status, Depends
from app.infrastructure.security.hashing import hash_password, verify_password
from app.infrastructure.security.auth import create_access_token
from app.infrastructure.database.user_database import fake_user_db
from app.presentation.schemas.user_schemas import UserCreate, UserLogin, Token
from app.infrastructure.security.auth import get_current_user
from app.infrastructure.security.roles import required_role

router_auth = APIRouter(prefix="/auth", tags=["Authentication"])

@router_auth.post("/register")
def register(user: UserCreate):
    #checks if email is already taken
    
    role = getattr(user, "role", "user")
    
    if user.email in fake_user_db:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    fake_user_db[user.email]= {
        "email": user.email,
        "username": user.username,
        "hashed_password": hash_password(user.password),
        "role": role
    }
    
    return{"message": "user registered successfully", "role": role}
    
@router_auth.post("/login", response_model=Token)
def login(credentials: UserLogin):
    #check  if user exists
    user = fake_user_db.get(credentials.email)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="invalid email or password"
        )
    
    #verify password
    if not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="invalid email email or password"
        )
    
    token = create_access_token(data={"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}

# this is a protected route so it requires a valid JWT token
@router_auth.get("/me")
def get_profile(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return {"user": current_user}


@router_auth.get("/manager/dashboard")
def manager_dashboard(current_user: dict = Depends(required_role("manager"))):
    return {"message": f"Welcome {current_user['username']}, you are a manager"}
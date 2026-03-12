from fastapi import APIRouter
from backend.app.infrastructure.security.hashing import hash_password


router_auth = APIRouter()

@router_auth.post("/register")

def register(username: str, password: str):
    hashed_password = hash_password(password)
    
    #change this later on to database
    return{
        "username": username,
        "hashed_password": hashed_password
    }


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.authorization_service import create_customer, validate_customer

router = APIRouter(prefix="/authorization", tags=["authorization"])

@router.post("/register")
def register(username: str, email: str, password: str, db: Session = Depends(get_db)):
    customer = create_customer(db, username, email, password)
    return {"message": "Success, customer registered.", "customer_id": customer.id}


@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    customer = validate_customer(db, username, password)

    if not customer:
        raise HTTPException(status_code=401, detail="Invalid login info")
    return {"message": "Login successful. Customer:", "customer_id": customer.id}
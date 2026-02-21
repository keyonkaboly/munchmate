from sqlalchemy.orm import Session
from app.db.models import Customer
from app.helpers.security import hash_password, verify_password

def create_customer(db: Session, username: str, email: str, password: str):
    customer = Customer(username=username, email=email, password_hash=hash_password(password))

    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

def validate_customer(db: Session, username: str, password: str):

    customer = db.query(Customer).filter(Customer.username == username).first()

    if not customer:
        return None
    
    if not verify_password(password, Customer.password_hash):
        return None
    
    return customer
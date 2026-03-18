from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.infrastructure.security.hashing import SECRET_KEY, ALGORITHM
from app.infrastructure.database.models import Customer
from app.infrastructure.database.database import get_db
from app.infrastructure.security.hashing import SECRET_KEY, ALGORITHM
from app.infrastructure.database.models import Customer


def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(Customer).filter(Customer.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
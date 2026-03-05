from sqlalchemy import Column, Integer, String
from .database import Base

class Customer(Base):
    __tablename__ = "customers"

    # Passwords can be the same, but usernames and emails must be unique
    # id is a unique identifier for each row in the table
    # None of these items are allowed to be null.
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

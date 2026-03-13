from sqlalchemy import Column, Integer, String, Float, Boolean
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


# Restaurant table definition
class Restaurant(Base):
    __tablename__ = "restaurants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    description = Column(String, nullable=True)
    hours_of_operation = Column(String, nullable=True)
    is_halal = Column(Boolean, default=False)
    is_vegetarian = Column(Boolean, default=False)

class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    
    # Update: ensure that same name/restaurant id cannot happen. Removed primary key. Can't be left null
    name = Column(String, nullable=False)
    restaurant_id = Column(Integer, nullable=False)
    price = Column(Float, nullable=True)
    
    # This means each restaurant can have items with same name
    # but the combination of name+restaurant_id must be unique
    # Not sure if this is the best approach tbh, might want to reconsider using an id field instead

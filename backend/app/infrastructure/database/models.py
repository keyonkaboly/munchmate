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


# Restaurant table definition
class Restaurant(Base):
    __tablename__ = "restaurants"
    
    id = Column(Integer, primary_key=True, index=True)
    # probably should add name, location fields here at some point


class MenuItem(Base):
    __tablename__ = "menu_items"
    
    # Using composite primary key here - name + restaurant_id together
    name = Column(String, primary_key=True)
    restaurant_id = Column(Integer, primary_key=True)
    
    # This means each restaurant can have items with same name
    # but the combination of name+restaurant_id must be unique
    # Not sure if this is the best approach tbh, might want to reconsider using an id field instead

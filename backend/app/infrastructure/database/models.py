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


# Restaurant model - straightforward
class Restaurant(Base):
    __tablename__ = "restaurants"
    
    id = Column(Integer, primary_key=True, index=True)
    # TODO: might want to add more fields later like name, address, etc.


# Menu items for each restaurant
class MenuItem(Base):
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # item name like "Burger" or whatever
    restaurant_id = Column(Integer, nullable=False)
    
    # Note: Should probably add a ForeignKey here eventually to link to Restaurant
    # Something like: ForeignKey("restaurants.id") but keeping it simple for now

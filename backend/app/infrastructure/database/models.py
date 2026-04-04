from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from .database import Base

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    user_type = Column(String, nullable=False, default="customer")
    restaurant_manager_restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=True)
    loyalty_points = Column(Integer, nullable=False, default=0)
    loyalty_rewards_available = Column(Integer, nullable=False, default=0)

class Restaurant(Base):
    __tablename__ = "restaurants"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, nullable=True)
    food_item = Column(String, nullable=True)
    is_halal = Column(Boolean, default=False)
    is_vegetarian = Column(Boolean, default=False)
    cuisine_type = Column(String, nullable=True)

class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    food_item = Column(String, nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    price = Column(Float, nullable=True)
    is_halal = Column(Boolean, default=False)
    is_vegetarian = Column(Boolean, default=False)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, index = True)
    combined_order_id = Column(String, index=True, nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable = True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable = False)
    subtotal = Column(Float, nullable = False, default = 0.0)
    tax = Column(Float, nullable = False, default = 0.0)
    delivery_cost = Column(Float, nullable = False, default = 5.0)
    total_cost = Column(Float, nullable = False, default = 0.0)
    delivery_method = Column(String, nullable=True)
    delivery_distance = Column(Float, nullable=True)
    delivery_time = Column(String, nullable=True)
    delivery_time_actual = Column(Float, nullable=True)
    delivery_delay = Column(Float, nullable=True)
    route_taken = Column(String, nullable=True)
    route_type = Column(String, nullable=True)
    route_efficiency = Column(Float, nullable=True)
    food_item = Column(String, nullable=True)
    
    status = Column(String, nullable=False, default="Created")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False)
    order_id = Column(String, nullable=False)
    message = Column(String, nullable=False)
    notification_type = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)

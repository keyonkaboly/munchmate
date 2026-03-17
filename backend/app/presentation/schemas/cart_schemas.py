from pydantic import BaseModel
from typing import List

"""Used pydantic to make schema for cart and checkout requests and responses"""
class CartItemResponse(BaseModel):
    food_item: str
    restaurant_id: int
    price: float

class CartRequest(BaseModel):
    order_id: str

class CartResponse(BaseModel):
    order_id: str
    items: List[CartItemResponse]
    subtotal: float
    tax: float
    delivery_cost: float
    total_cost: float

class CheckoutRequest(BaseModel):
    order_id: str

class CheckoutResponse(BaseModel):
    order_id: str
    subtotal: float
    tax: float
    delivery_cost: float
    total_cost: float
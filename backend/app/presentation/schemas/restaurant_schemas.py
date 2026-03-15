from pydantic import BaseModel, Field
from typing import Optional

#this file is for restaurant schemas, which will be used for restaurant info 
class RestaurantUpdate(BaseModel):
    id: int
    location: Optional[str] = None
    food_item: Optional[str] = None

class RestaurantResponse(BaseModel):
    id: int
    location: Optional[str] = None
    food_item: Optional[str] = None
    is_halal: Optional[bool] = None
    is_vegetarian: Optional[bool] = None
    cuisine_type: Optional[str] = None
    model_config = {"from_attributes": True}

class MenuItemUpdate(BaseModel):
    description: Optional[str] = None
    category: Optional[str] = None
    is_available: Optional[bool] = None
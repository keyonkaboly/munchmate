from pydantic import BaseModel, Field
from typing import Optional

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

class MenuItemNameUpdate(BaseModel):
    food_item: str = Field(min_length=1)
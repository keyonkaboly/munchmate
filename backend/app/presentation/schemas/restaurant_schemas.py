from pydantic import BaseModel, Field
from typing import Optional

#this file is for restaurant schemas, which will be used for restaurant info 
class RestaurantBase(BaseModel):
    name: str = Field(min_length=1, max_length=100) #rest. name must be between 1 to 100 characters
    description: Optional[str] = Field(default=None, max_length=500) # its optional to write a description about the restaurant
    hours_of_operation : Optional[str] = Field(default=None, max_length=100) # its optional to put the hours of the restaurant
    
class RestaurantUpdate(RestaurantBase):
    pass
    
class RestaurantResponse(RestaurantBase):
    id: int

model_config = {"from_attributes":True} # lets you return db object directly from fastapi endpoint and it will be converted to the pydantic model automatically

class MenuItemUpdate(BaseModel):
    description: Optional[str] = None
    category: Optional[str] = None
    is_available: Optional[bool] = None
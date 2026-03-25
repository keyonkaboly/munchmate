from pydantic import BaseModel,EmailStr, Field, ConfigDict
from typing import Literal
    
class UserBase(BaseModel):
    username: str = Field(min_length=6, max_length=12)
    email: EmailStr
    
class UserCreate(UserBase):
    password: str = Field(min_length=6)
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class UserResponse(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class RestaurantManagerCreate(UserCreate):
    restaurant_manager_restaurant_id: int
    
class RestaurantManagerResponse(UserResponse):
    restaurant_manager_restaurant_id: int
    user_type: str

class Token(BaseModel):
    access_token: str
    token_type: str
    
    
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=6, max_length=12)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=6)
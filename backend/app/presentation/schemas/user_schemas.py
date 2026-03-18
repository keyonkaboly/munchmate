from pydantic import BaseModel,EmailStr, Field, ConfigDict
from typing import Literal
    
class UserBase(BaseModel):
    username: str = Field(min_length=6, max_length=12) #username must be between 6 to 12 characters
    email: EmailStr
    
class UserCreate(UserBase):
    password: str = Field(min_length=6)
    
class UserLogin(UserBase):
    username: str
    password: str
    
class UserResponse(UserBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
    
class RegisterRequest(BaseModel):
    username: str = Field(min_length=6, max_length=12)
    email: EmailStr
    password: str = Field(min_length=6)
    role: Literal["customer", "restaurant_owner"]

class RegisterResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

class RestaurantManagerCreate(UserCreate):
    restaurant_manager_restaurant_id: int


class RestaurantManagerResponse(UserResponse):
    restaurant_manager_restaurant_id: int
    user_type: str

#this access token used to authenticate the user
#this tells the server who is making the request
class Token(BaseModel):
    access_token: str
    token_type: str
    
class UserInDB(UserBase):
    hashed_password: str
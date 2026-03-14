from pydantic import BaseModel,EmailStr, Field, ConfigDict
from typing import Optional

#this file is for user schemas, which will be used for user registration and login
class UserBase(BaseModel):
    username: str = Field(min_length=6, max_length=12) #username must be between 6 to 12 characters
    email: EmailStr = Field(max_length=50)
    
class UserCreate(UserBase):
    password: str = Field(min_length=6)
    role: Optional[str] = "user"
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class UserResponse(UserBase):
    id: int
    username: str
    email: EmailStr

#this access token used to authenticate the user
#this tells the server who is making the request
class Token(BaseModel):
    access_token: str
    token_type: str
    
class UserInDB(UserBase):
    hashed_password: str
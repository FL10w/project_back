from pydantic import BaseModel, Field, validator, EmailStr
from typing import List, Optional, Dict
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    preferences: Optional[Dict] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=5)
    favorite_genres: Optional[List[str]] = None
    favorite_authors: Optional[List[str]] = None
    reading_goals: Optional[str] = None

class UserPreferences(BaseModel):
    favorite_genres: List[str] = Field(default_factory=list)
    reading_goals: Optional[str] = None
    favorite_authors: List[str] = Field(default_factory=list)

class UserRating(BaseModel):
    item_id: str
    item_type: str
    rating: int
    timestamp: datetime

    @validator('item_type')
    def validate_item_type(cls, v):
        if v not in ('book', 'movie'):
            raise ValueError("Item type must be 'book' or 'movie'")
        return v

    @validator('rating')
    def validate_rating(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v

class UserLogin(BaseModel):
    email: str
    password: str

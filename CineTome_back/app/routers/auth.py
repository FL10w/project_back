from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from pydantic import BaseModel

from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.services.auth import  login_user
from app.services.user_service import create_user

router = APIRouter(prefix="/auth", tags=["auth"])

class EmailPasswordRequestForm(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, user_data)

@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    return await login_user(db, user.email, user.password)
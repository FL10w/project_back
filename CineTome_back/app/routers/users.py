from fastapi import APIRouter, Depends, HTTPException, status, Form, Security, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from fastapi.security import  HTTPAuthorizationCredentials
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.auth import get_current_user
from app.services.user_service import get_user_by_email, get_user_by_id
from app.core.constants import get_available_genres, get_available_authors
from sqlalchemy.orm.attributes import flag_modified



router = APIRouter(prefix="/users", tags=["users"])

@router.get("/genres", response_model=List[str])
async def get_genres():
    """Получить список доступных жанров"""
    return get_available_genres()

@router.get("/authors", response_model=List[str])
async def get_authors():
    """Получить список доступных авторов"""
    return get_available_authors()


@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate = Body(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить данные текущего пользователя"""
    print(f"Received update data: {update_data.dict()}")
    update_dict = {}

    if update_data.username:
        existing_user = await db.execute(
            select(User).where(User.username == update_data.username)
        )
        existing_user = existing_user.scalar_one_or_none()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        update_dict["username"] = update_data.username

    if update_data.email:
        existing_user = await db.execute(
            select(User).where(User.email == update_data.email)
        )
        existing_user = existing_user.scalar_one_or_none()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already taken"
            )
        update_dict["email"] = update_data.email

    if update_data.password:
        from app.utils.security import get_password_hash
        update_dict["hashed_password"] = get_password_hash(update_data.password)


    preferences = current_user.preferences or {
        "favorite_genres": [],
        "reading_goals": None,
        "favorite_authors": []
    }
    print(f"Initial preferences: {preferences}")

    available_genres = get_available_genres()
    available_authors = get_available_authors()


    has_preference_changes = False
    if update_data.favorite_genres is not None:
        invalid_genres = [genre for genre in update_data.favorite_genres if genre not in available_genres]
        if invalid_genres:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid genres: {invalid_genres}. Available genres: {available_genres}"
            )
        preferences["favorite_genres"] = update_data.favorite_genres
        has_preference_changes = True

    if update_data.favorite_authors is not None:
        invalid_authors = [author for author in update_data.favorite_authors if author not in available_authors]
        if invalid_authors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid authors: {invalid_authors}. Available authors: {available_authors}"
            )
        preferences["favorite_authors"] = update_data.favorite_authors
        has_preference_changes = True

    if update_data.reading_goals is not None:
        preferences["reading_goals"] = update_data.reading_goals
        has_preference_changes = True


    if has_preference_changes:
        current_user.preferences = dict(preferences)
        flag_modified(current_user, "preferences")
        print(f"Updated preferences: {current_user.preferences}")

    for key, value in update_dict.items():
        setattr(current_user, key, value)

    await db.commit()
    await db.refresh(current_user)

    print(f"Final user data: {current_user.__dict__}")
    return current_user
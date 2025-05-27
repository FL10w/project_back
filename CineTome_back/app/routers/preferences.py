from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserPreferences, UserRating
from app.services.auth import get_current_user
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.post("/update")
async def update_preferences(
        prefs: UserPreferences,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    user.preferences = prefs.dict()
    await db.commit()
    return {"message": "Preferences updated"}


@router.post("/add-rating")
async def add_rating(
        rating: UserRating,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    if not user.ratings_history:
        user.ratings_history = []

    user.ratings_history.append(rating.dict())
    await db.commit()
    return {"message": "Rating added"}
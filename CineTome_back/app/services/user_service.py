from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from app.models.user import User
from app.schemas.user import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


async def create_user(db: AsyncSession, user: UserCreate):
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        preferences={
            "favorite_genres": [],
            "reading_goals": None,
            "favorite_authors": []
        }
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_email(db: AsyncSession, email: str):
    async with db.begin():
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, id: int):
    async with db.begin():
        result = await db.execute(select(User).filter(User.id == id))
        return result.scalar_one_or_none()

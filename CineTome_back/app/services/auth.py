from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core import settings
from app.models.user import User
from app.services.user_service import pwd_context, get_user_by_email, get_user_by_id
from app.schemas.token import Token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(seconds=int(settings.JWT_EXPIRE_TIME))
    to_encode = {"sub": str(user_id), "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def verify_token(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    print(">>> verify_token вызвана")
    print("Проверка токена началась...")
    if not token:
        print("Нет токена")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        print(f"Полученный токен: {token[:10]}...")
        print(f"SECRET_KEY: {settings.SECRET_KEY[:5]}...")
        print(f"ALGORITHM: {settings.ALGORITHM}")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(f"Payload: {payload}")
        user_id: str = payload.get("sub")
        if user_id is None:
            print("sub не найден в payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        print(f"user_id из токена: {user_id}")
    except jwt.ExpiredSignatureError:
        print("Токен истек")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.PyJWTError as e:
        print(f"JWT ошибка: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        print(f"Неожиданная ошибка: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

    try:
        user = await get_user_by_id(db, int(user_id))
        if user is None:
            print(f"Пользователь с ID {user_id} не найден в БД")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        print(f"Пользователь {user.username} найден")
    except Exception as e:
        print(f"Ошибка получения пользователя: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return user

async def login_user(db: AsyncSession, email: str, password: str) -> Token:
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    access_token = create_access_token(user.id)
    token_response = Token(access_token=access_token, token_type="bearer")
    print(f"Returning token: {token_response.dict()}")
    return token_response

async def get_current_user(user: User = Depends(verify_token)) -> User:
    return user
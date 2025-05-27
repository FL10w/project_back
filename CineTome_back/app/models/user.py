from sqlalchemy import Column, Integer, String, JSON, LargeBinary
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    profile_picture = Column(LargeBinary, nullable=True)
    preferences = Column(JSON, default={
        "favorite_genres": [],
        "reading_goals": None,
        "favorite_authors": []
    })
    ratings_history = Column(JSON, default=[])
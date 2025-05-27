from sqlalchemy import Column, Integer, String, Float, JSON
from app.database import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    kp_id = Column(Integer, unique=True, index=True)
    imdb_id = Column(String, nullable=True)
    title = Column(String, index=True)
    year = Column(Integer)
    poster = Column(String, nullable=True)
    genres = Column(JSON)
    countries = Column(JSON)
    kp_rating = Column(Float, nullable=True)
    imdb_rating = Column(Float, nullable=True)
    duration = Column(Integer, nullable=True)
    content_type = Column(String, default="movie")

class Series(Base):
    __tablename__ = "series"

    id = Column(Integer, primary_key=True, index=True)
    kp_id = Column(Integer, unique=True, index=True)
    imdb_id = Column(String, nullable=True)
    title = Column(String, index=True)
    year = Column(Integer)
    poster = Column(String, nullable=True)
    genres = Column(JSON)
    countries = Column(JSON)
    kp_rating = Column(Float, nullable=True)
    imdb_rating = Column(Float, nullable=True)
    duration = Column(Integer, nullable=True)
    content_type = Column(String, default="series")
    episode_count = Column(Integer, nullable=True)
    season_count = Column(Integer, nullable=True)
    seasons = Column(JSON, nullable=True)
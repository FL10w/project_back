from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    work_id = Column(String, unique=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    year = Column(Integer, nullable=True)
    description = Column(String, nullable=True)
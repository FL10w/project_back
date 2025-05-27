from dotenv import load_dotenv
import os

load_dotenv('.env')

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
JWT_EXPIRE_TIME = os.getenv("JWT_EXPIRE_TIME", "3600")
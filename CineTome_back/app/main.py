from fastapi import FastAPI, Request
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, books, movies, ai, preferences, users
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from fastapi.openapi.utils import get_openapi



app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Request URL: {request.url}")
    print(f"Request Headers: {dict(request.headers)}")  # Логируем все заголовки
    response = await call_next(request)
    return response

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="CineTome API",
        version="1.0.0",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(ai.router)
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(movies.router)
app.include_router(users.router)
app.include_router(preferences.router)
app.mount("/uploads", StaticFiles(directory=settings.UPLOADS_DIR), name="uploads")

@app.get("/")
def read_root():
    return {"message": "Welcome to Recommendation Service!"}
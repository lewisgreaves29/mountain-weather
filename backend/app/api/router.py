from fastapi import APIRouter
from backend.app.api.v1.weather import router as weather_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(weather_router)

from fastapi import APIRouter

from app.api.v1 import ip as ip_routes

api_router = APIRouter()
api_router.include_router(ip_routes.router, prefix="/ip", tags=["ip"])

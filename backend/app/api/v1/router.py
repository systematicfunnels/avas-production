from fastapi import APIRouter
from app.api.v1.endpoints import auth, inspections, assets, analytics

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(inspections.router)
api_router.include_router(assets.router)
api_router.include_router(analytics.router)

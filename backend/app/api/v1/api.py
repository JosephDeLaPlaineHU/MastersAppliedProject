from fastapi import APIRouter
from app.api.v1.endpoints import auth, vms, analytics, courses, resources, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(vms.router, prefix="/vms", tags=["vms"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(resources.router, prefix="/resources", tags=["resources"])
api_router.include_router(users.router, prefix="/users", tags=["users"])


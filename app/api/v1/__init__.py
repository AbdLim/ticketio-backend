from fastapi import APIRouter
from .auth import router as auth_router
from .events import router as event_router
from .tickets import router as ticket_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(event_router)
api_router.include_router(ticket_router)

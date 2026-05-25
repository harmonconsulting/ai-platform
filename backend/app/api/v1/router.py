from fastapi import APIRouter

from app.api.v1 import (
    auth,
    chat,
    health,
    upload,
    knowledge
)

router = APIRouter()

router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"]
)

router.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat"]
)

router.include_router(
    upload.router,
    prefix="/upload",
    tags=["upload"]
)

router.include_router(
    knowledge.router,
    prefix="/knowledge",
    tags=["knowledge"]
)

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    categories,
    tags,
    posts,
    materials,
    messages,
    groups,
    goals,
    tasks,
    meetings,
    learning,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(categories.router)
api_router.include_router(tags.router)
api_router.include_router(posts.router)
api_router.include_router(materials.router)
api_router.include_router(messages.router)
api_router.include_router(groups.router)
api_router.include_router(goals.router)
api_router.include_router(tasks.router)
api_router.include_router(meetings.router)
api_router.include_router(learning.router)

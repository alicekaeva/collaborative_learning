from fastapi import APIRouter

from app.modules.identity.router import auth_router, users_router
from app.modules.taxonomy.router import categories_router, tags_router
from app.modules.groups.router import router as groups_router
from app.modules.messaging.router import router as messages_router
from app.modules.content.router import (
    posts_router, materials_router, goals_router,
    tasks_router, meetings_router, learning_router,
)

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(categories_router)
api_router.include_router(tags_router)
api_router.include_router(groups_router)
api_router.include_router(messages_router)
api_router.include_router(posts_router)
api_router.include_router(materials_router)
api_router.include_router(goals_router)
api_router.include_router(tasks_router)
api_router.include_router(meetings_router)
api_router.include_router(learning_router)

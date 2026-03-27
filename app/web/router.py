from fastapi import APIRouter
from app.web.routes import auth, posts, groups, materials, messages, learning, users, tags, categories

web_router = APIRouter()
web_router.include_router(auth.router)
web_router.include_router(posts.router)
web_router.include_router(groups.router)
web_router.include_router(materials.router)
web_router.include_router(messages.router)
web_router.include_router(learning.router)
web_router.include_router(users.router)
web_router.include_router(tags.router)
web_router.include_router(categories.router)

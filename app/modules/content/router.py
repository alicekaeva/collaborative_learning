from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel

from app.api.deps import DBDep, CurrentUser, require_roles
from app.modules.identity.models.user import User
from app.core.config import settings
from app.core.exceptions import NotFoundError, ForbiddenError, BadRequestError
from app.modules.content.crud import post as post_crud, material as material_crud
from app.modules.content.crud import goal as goal_crud, task as task_crud, meeting as meeting_crud
from app.modules.groups import repository as group_repo
from app.modules.content.schemas.post import PostCreate, PostUpdate, PostRead
from app.modules.content.schemas.material import MaterialRead, MaterialUpdate
from app.modules.content.schemas.goal import GoalCreate, GoalUpdate, GoalRead
from app.modules.content.schemas.task import TaskCreate, TaskUpdate, TaskRead
from app.modules.content.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingRead
from app.modules.groups.schemas.group import GroupRead
from app.modules.messaging.schemas.message import MessageRead, SendGroupMessageRequest
from app.schemas.common import Message
from app.services.cache import get_cached, set_cached
from app.services.storage import save_material, delete_file

posts_router = APIRouter(prefix="/posts", tags=["posts"])
materials_router = APIRouter(prefix="/materials", tags=["materials"])
goals_router = APIRouter(prefix="/goals", tags=["goals"])
tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])
meetings_router = APIRouter(prefix="/meetings", tags=["meetings"])
learning_router = APIRouter(prefix="/learning", tags=["learning"])


# ------------------------------------------------------------------ Posts

@posts_router.get("/", response_model=List[PostRead])
async def list_posts(
    db: DBDep,
    tag_id: Optional[int] = None,
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
):
    if tag_id:
        return await post_crud.get_by_tag(db, tag_id, skip=skip, limit=limit)
    if category_id:
        return await post_crud.get_by_category(db, category_id, skip=skip, limit=limit)
    return await post_crud.get_all(db, skip=skip, limit=limit)


@posts_router.get("/recommended", response_model=List[PostRead])
async def recommended_posts(db: DBDep, current_user: CurrentUser):
    cache_key = f"posts:recommended:{current_user.id}"
    cached = await get_cached(cache_key)
    if cached:
        return [PostRead.model_validate(item) for item in cached]
    tag_ids = [t.id for t in current_user.tags]
    posts = await post_crud.get_recommended(db, tag_ids)
    result = [PostRead.model_validate(p) for p in posts]
    await set_cached(cache_key, [r.model_dump(mode="json") for r in result])
    return result


@posts_router.get("/favorites", response_model=List[PostRead])
async def favorite_posts(db: DBDep, current_user: CurrentUser):
    return await post_crud.get_favorites(db, current_user.id)


@posts_router.get("/user/{user_id}", response_model=List[PostRead])
async def user_posts(user_id: int, db: DBDep):
    return await post_crud.get_by_author(db, user_id)


@posts_router.post("/", response_model=PostRead, status_code=201)
async def create_post(data: PostCreate, db: DBDep, current_user: CurrentUser):
    return await post_crud.create(db, data, current_user.id)


@posts_router.get("/{post_id}", response_model=PostRead)
async def get_post(post_id: int, db: DBDep):
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        raise NotFoundError("Пост не найден")
    return post


@posts_router.patch("/{post_id}", response_model=PostRead)
async def update_post(post_id: int, data: PostUpdate, db: DBDep, current_user: CurrentUser):
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        raise NotFoundError("Пост не найден")
    if post.author_id != current_user.id and "ROLE_ADMIN" not in current_user.roles:
        raise ForbiddenError("Нет доступа для редактирования этого поста")
    return await post_crud.update_post(db, post, data)


@posts_router.delete("/{post_id}", status_code=204)
async def delete_post(post_id: int, db: DBDep, current_user: CurrentUser):
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        raise NotFoundError("Пост не найден")
    if post.author_id != current_user.id and "ROLE_ADMIN" not in current_user.roles:
        raise ForbiddenError("Нет доступа для удаления этого поста")
    await post_crud.delete(db, post)


@posts_router.post("/{post_id}/favorite", response_model=Message)
async def add_to_favorites(post_id: int, db: DBDep, current_user: CurrentUser):
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        raise NotFoundError("Пост не найден")
    await post_crud.add_to_favorites(db, post, current_user)
    return Message(detail="Пост добавлен в избранное")


@posts_router.delete("/{post_id}/favorite", response_model=Message)
async def remove_from_favorites(post_id: int, db: DBDep, current_user: CurrentUser):
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        raise NotFoundError("Пост не найден")
    await post_crud.remove_from_favorites(db, post, current_user)
    return Message(detail="Пост удалён из избранного")


# ------------------------------------------------------------------ Materials

@materials_router.get("/", response_model=List[MaterialRead])
async def list_materials(db: DBDep, current_user: CurrentUser, skip: int = 0, limit: int = 50):
    return await material_crud.get_public(db, skip=skip, limit=limit)


@materials_router.post("/", response_model=MaterialRead, status_code=201)
async def upload_material(
    db: DBDep,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    name: str = Form(...),
    is_private: bool = Form(False),
    group_id: int = Form(None),
):
    file_link, mime_type = await save_material(file)
    return await material_crud.create(
        db,
        name=name,
        file_link=file_link,
        mime_type=mime_type,
        is_private=is_private,
        creator_user_id=current_user.id,
        creator_group_id=group_id,
    )


@materials_router.get("/{material_id}", response_model=MaterialRead)
async def get_material(material_id: int, db: DBDep, current_user: CurrentUser):
    material = await material_crud.get_by_id(db, material_id)
    if not material:
        raise NotFoundError("Материал не найден")
    if material.is_private and material.creator_user_id != current_user.id:
        raise ForbiddenError("Это приватный материал")
    return material


@materials_router.get("/{material_id}/download")
async def download_material(material_id: int, db: DBDep, current_user: CurrentUser):
    material = await material_crud.get_by_id(db, material_id)
    if not material:
        raise NotFoundError("Материал не найден")
    if material.is_private and material.creator_user_id != current_user.id:
        raise ForbiddenError("Это приватный материал")
    filename = Path(material.file_link).name
    upload_dir = Path(settings.UPLOAD_DIR).resolve()
    file_path = (upload_dir / filename).resolve()
    if not str(file_path).startswith(str(upload_dir)):
        raise BadRequestError("Недопустимый путь к файлу")
    if not file_path.exists():
        raise NotFoundError("Файл не найден на диске")
    return FileResponse(str(file_path), media_type=material.mime_type, filename=material.name)


@materials_router.patch("/{material_id}", response_model=MaterialRead)
async def update_material(material_id: int, data: MaterialUpdate, db: DBDep, current_user: CurrentUser):
    material = await material_crud.get_by_id(db, material_id)
    if not material:
        raise NotFoundError("Материал не найден")
    if material.creator_user_id != current_user.id and "ROLE_ADMIN" not in current_user.roles:
        raise ForbiddenError("Нет доступа")
    return await material_crud.update_material(db, material, data)


@materials_router.delete("/{material_id}", status_code=204)
async def delete_material(material_id: int, db: DBDep, current_user: CurrentUser):
    material = await material_crud.get_by_id(db, material_id)
    if not material:
        raise NotFoundError("Материал не найден")
    if material.creator_user_id != current_user.id and "ROLE_ADMIN" not in current_user.roles:
        raise ForbiddenError("Нет доступа")
    await delete_file(material.file_link)
    await material_crud.delete(db, material)


# ------------------------------------------------------------------ Goals

@goals_router.get("/group/{group_id}", response_model=List[GoalRead])
async def list_goals(group_id: int, db: DBDep, current_user: CurrentUser):
    return await goal_crud.get_by_group(db, group_id)


@goals_router.post("/", response_model=GoalRead, status_code=201)
async def create_goal(
    data: GoalCreate,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    group = await group_repo.get_by_id(db, data.group_id)
    if not group:
        raise NotFoundError("Группа не найдена")
    return await goal_crud.create(db, data)


@goals_router.get("/{goal_id}", response_model=GoalRead)
async def get_goal(goal_id: int, db: DBDep, current_user: CurrentUser):
    goal = await goal_crud.get_by_id(db, goal_id)
    if not goal:
        raise NotFoundError("Цель не найдена")
    return goal


@goals_router.patch("/{goal_id}", response_model=GoalRead)
async def update_goal(
    goal_id: int,
    data: GoalUpdate,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    goal = await goal_crud.get_by_id(db, goal_id)
    if not goal:
        raise NotFoundError("Цель не найдена")
    return await goal_crud.update_goal(db, goal, data)


@goals_router.post("/{goal_id}/complete", response_model=GoalRead)
async def complete_goal(
    goal_id: int,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    goal = await goal_crud.get_by_id(db, goal_id)
    if not goal:
        raise NotFoundError("Цель не найдена")
    return await goal_crud.set_completed(db, goal, True)


@goals_router.post("/{goal_id}/uncomplete", response_model=GoalRead)
async def uncomplete_goal(
    goal_id: int,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    goal = await goal_crud.get_by_id(db, goal_id)
    if not goal:
        raise NotFoundError("Цель не найдена")
    return await goal_crud.set_completed(db, goal, False)


@goals_router.delete("/{goal_id}", status_code=204)
async def delete_goal(
    goal_id: int,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    goal = await goal_crud.get_by_id(db, goal_id)
    if not goal:
        raise NotFoundError("Цель не найдена")
    await goal_crud.delete(db, goal)


# ------------------------------------------------------------------ Tasks

@tasks_router.get("/group/{group_id}", response_model=List[TaskRead])
async def list_tasks(group_id: int, db: DBDep, current_user: CurrentUser):
    return await task_crud.get_by_group(db, group_id)


@tasks_router.post("/", response_model=TaskRead, status_code=201)
async def create_task(
    data: TaskCreate,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    group = await group_repo.get_by_id(db, data.group_id)
    if not group:
        raise NotFoundError("Группа не найдена")
    return await task_crud.create(db, data)


@tasks_router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: int, db: DBDep, current_user: CurrentUser):
    task = await task_crud.get_by_id(db, task_id)
    if not task:
        raise NotFoundError("Задание не найдено")
    return task


@tasks_router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    task = await task_crud.get_by_id(db, task_id)
    if not task:
        raise NotFoundError("Задание не найдено")
    return await task_crud.update_task(db, task, data)


@tasks_router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    task = await task_crud.get_by_id(db, task_id)
    if not task:
        raise NotFoundError("Задание не найдено")
    await task_crud.delete(db, task)


# ------------------------------------------------------------------ Meetings

@meetings_router.get("/group/{group_id}", response_model=List[MeetingRead])
async def list_meetings(group_id: int, db: DBDep, current_user: CurrentUser):
    return await meeting_crud.get_by_group(db, group_id)


@meetings_router.post("/", response_model=MeetingRead, status_code=201)
async def create_meeting(
    data: MeetingCreate,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    group = await group_repo.get_by_id(db, data.group_id)
    if not group:
        raise NotFoundError("Группа не найдена")
    return await meeting_crud.create(db, data)


@meetings_router.get("/{meeting_id}", response_model=MeetingRead)
async def get_meeting(meeting_id: int, db: DBDep, current_user: CurrentUser):
    meeting = await meeting_crud.get_by_id(db, meeting_id)
    if not meeting:
        raise NotFoundError("Встреча не найдена")
    return meeting


@meetings_router.patch("/{meeting_id}", response_model=MeetingRead)
async def update_meeting(
    meeting_id: int,
    data: MeetingUpdate,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    meeting = await meeting_crud.get_by_id(db, meeting_id)
    if not meeting:
        raise NotFoundError("Встреча не найдена")
    return await meeting_crud.update_meeting(db, meeting, data)


@meetings_router.delete("/{meeting_id}", status_code=204)
async def delete_meeting(
    meeting_id: int,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    meeting = await meeting_crud.get_by_id(db, meeting_id)
    if not meeting:
        raise NotFoundError("Встреча не найдена")
    await meeting_crud.delete(db, meeting)


# ------------------------------------------------------------------ Learning (aggregate view)

class LearningGroupDetail(BaseModel):
    group: GroupRead
    messages: List[MessageRead] = []
    goals: List[GoalRead] = []
    tasks: List[TaskRead] = []
    meetings: List[MeetingRead] = []
    materials: List[MaterialRead] = []


@learning_router.get("/groups", response_model=List[GroupRead])
async def my_learning_groups(db: DBDep, current_user: CurrentUser):
    return await group_repo.get_user_groups(db, current_user)


@learning_router.get("/groups/{group_id}", response_model=LearningGroupDetail)
async def learning_group_detail(group_id: int, db: DBDep, current_user: CurrentUser):
    from app.modules.messaging import repository as msg_repo

    group = await group_repo.get_by_id(db, group_id)
    if not group:
        raise NotFoundError("Группа не найдена")

    role = await group_repo.get_user_role_in_group(db, group, current_user)
    if not role:
        raise ForbiddenError("Вы не состоите в этой группе")

    messages = await msg_repo.get_group_chat(db, group_id)
    goals = await goal_crud.get_by_group(db, group_id)
    tasks = await task_crud.get_by_group(db, group_id)
    meetings = await meeting_crud.get_by_group(db, group_id)
    materials = await material_crud.get_by_group(db, group_id)

    return LearningGroupDetail(
        group=GroupRead.model_validate(group),
        messages=[MessageRead.model_validate(m) for m in messages],
        goals=[GoalRead.model_validate(g) for g in goals],
        tasks=[TaskRead.model_validate(t) for t in tasks],
        meetings=[MeetingRead.model_validate(m) for m in meetings],
        materials=[MaterialRead.model_validate(m) for m in materials],
    )


@learning_router.post("/groups/{group_id}/chat", response_model=MessageRead, status_code=201)
async def send_chat_message(
    group_id: int,
    data: SendGroupMessageRequest,
    db: DBDep,
    current_user: CurrentUser,
):
    from app.modules.messaging import repository as msg_repo

    group = await group_repo.get_by_id(db, group_id)
    if not group:
        raise NotFoundError("Группа не найдена")

    role = await group_repo.get_user_role_in_group(db, group, current_user)
    if not role:
        raise ForbiddenError("Вы не состоите в этой группе")

    return await msg_repo.send_group(db, data.content, current_user.id, group_id)

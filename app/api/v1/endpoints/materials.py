from typing import List
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse
from pathlib import Path

from app.api.deps import DBDep, CurrentUser
from app.core.config import settings
from app.core.exceptions import NotFoundError, ForbiddenError
from app.crud import material as material_crud
from app.schemas.material import MaterialRead, MaterialUpdate
from app.schemas.common import Message
from app.services.storage import save_material, delete_file

router = APIRouter(prefix="/materials", tags=["materials"])


@router.get("/", response_model=List[MaterialRead])
async def list_materials(db: DBDep, current_user: CurrentUser, skip: int = 0, limit: int = 50):
    return await material_crud.get_public(db, skip=skip, limit=limit)


@router.post("/", response_model=MaterialRead, status_code=201)
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


@router.get("/{material_id}", response_model=MaterialRead)
async def get_material(material_id: int, db: DBDep, current_user: CurrentUser):
    material = await material_crud.get_by_id(db, material_id)
    if not material:
        raise NotFoundError("Материал не найден")
    if material.is_private and material.creator_user_id != current_user.id:
        raise ForbiddenError("Это приватный материал")
    return material


@router.get("/{material_id}/download")
async def download_material(material_id: int, db: DBDep, current_user: CurrentUser):
    material = await material_crud.get_by_id(db, material_id)
    if not material:
        raise NotFoundError("Материал не найден")
    if material.is_private and material.creator_user_id != current_user.id:
        raise ForbiddenError("Это приватный материал")
    filename = Path(material.file_link).name
    file_path = Path(settings.UPLOAD_DIR) / filename
    if not file_path.exists():
        raise NotFoundError("Файл не найден на диске")
    return FileResponse(str(file_path), media_type=material.mime_type, filename=material.name)


@router.patch("/{material_id}", response_model=MaterialRead)
async def update_material(material_id: int, data: MaterialUpdate, db: DBDep, current_user: CurrentUser):
    material = await material_crud.get_by_id(db, material_id)
    if not material:
        raise NotFoundError("Материал не найден")
    if material.creator_user_id != current_user.id and "ROLE_ADMIN" not in current_user.roles:
        raise ForbiddenError("Нет доступа")
    return await material_crud.update_material(db, material, data)


@router.delete("/{material_id}", response_model=Message)
async def delete_material(material_id: int, db: DBDep, current_user: CurrentUser):
    material = await material_crud.get_by_id(db, material_id)
    if not material:
        raise NotFoundError("Материал не найден")
    if material.creator_user_id != current_user.id and "ROLE_ADMIN" not in current_user.roles:
        raise ForbiddenError("Нет доступа")
    await delete_file(material.file_link)
    await material_crud.delete(db, material)
    return Message(detail="Материал удалён")

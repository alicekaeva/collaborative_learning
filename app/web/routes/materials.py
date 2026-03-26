import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Request, Form, File, UploadFile
from fastapi.responses import RedirectResponse, HTMLResponse

from app.api.deps import DBDep
from app.core.config import settings
from app.crud import material as material_crud
from app.schemas.material import MaterialUpdate
from app.web.deps import WebUser
from app.web.utils import templates, redirect

router = APIRouter(tags=["web:materials"])


def _get_flash(request: Request) -> str | None:
    return request.cookies.get("flash_message")


def _clear_flash(response) -> None:
    response.delete_cookie("flash_message")


@router.get("/materials", response_class=HTMLResponse)
async def material_list(request: Request, db: DBDep, current_user: WebUser):
    materials = await material_crud.get_public(db)
    flash = _get_flash(request)
    response = templates.TemplateResponse(
        "materials/list.html",
        {
            "request": request,
            "user": current_user,
            "materials": materials,
            "flash": flash,
        },
    )
    if flash:
        _clear_flash(response)
    return response


@router.get("/materials/new", response_class=HTMLResponse)
async def new_material_form(request: Request, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(
        "materials/new.html",
        {"request": request, "user": current_user},
    )


@router.post("/materials/new", response_class=HTMLResponse)
async def new_material_submit(
    request: Request,
    db: DBDep,
    current_user: WebUser,
    name: str = Form(...),
    is_private: bool = Form(default=False),
    file: UploadFile = File(...),
):
    if not current_user:
        return RedirectResponse("/login", status_code=303)

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix if file.filename else ""
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = upload_dir / unique_filename

    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        return templates.TemplateResponse(
            "materials/new.html",
            {
                "request": request,
                "user": current_user,
                "error": f"Файл превышает максимально допустимый размер {settings.MAX_FILE_SIZE_MB} МБ",
            },
            status_code=400,
        )

    with open(file_path, "wb") as f:
        f.write(content)

    mime_type = file.content_type or "application/octet-stream"
    file_link = f"/uploads/materials/{unique_filename}"

    await material_crud.create(
        db,
        name=name,
        file_link=file_link,
        mime_type=mime_type,
        is_private=is_private,
        creator_user_id=current_user.id,
    )
    return redirect("/materials", message="Материал успешно загружен")


@router.get("/materials/{material_id}", response_class=HTMLResponse)
async def material_detail(request: Request, material_id: int, db: DBDep, current_user: WebUser):
    material = await material_crud.get_by_id(db, material_id)
    if not material:
        return redirect("/materials", message="Материал не найден")
    if material.is_private:
        if not current_user:
            return RedirectResponse("/login", status_code=303)
        is_owner = material.creator_user_id == current_user.id
        is_admin = "ROLE_ADMIN" in current_user.roles
        if not is_owner and not is_admin:
            return redirect("/materials", message="Доступ запрещён")

    flash = _get_flash(request)
    response = templates.TemplateResponse(
        "materials/detail.html",
        {
            "request": request,
            "user": current_user,
            "material": material,
            "flash": flash,
        },
    )
    if flash:
        _clear_flash(response)
    return response


@router.get("/materials/{material_id}/edit", response_class=HTMLResponse)
async def edit_material_form(request: Request, material_id: int, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    material = await material_crud.get_by_id(db, material_id)
    if not material:
        return redirect("/materials", message="Материал не найден")
    is_owner = material.creator_user_id == current_user.id
    is_admin = "ROLE_ADMIN" in current_user.roles
    if not is_owner and not is_admin:
        return redirect("/materials", message="Недостаточно прав")
    return templates.TemplateResponse(
        "materials/edit.html",
        {"request": request, "user": current_user, "material": material},
    )


@router.post("/materials/{material_id}/edit", response_class=HTMLResponse)
async def edit_material_submit(
    request: Request,
    material_id: int,
    db: DBDep,
    current_user: WebUser,
    name: str = Form(...),
    is_private: bool = Form(default=False),
):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    material = await material_crud.get_by_id(db, material_id)
    if not material:
        return redirect("/materials", message="Материал не найден")
    is_owner = material.creator_user_id == current_user.id
    is_admin = "ROLE_ADMIN" in current_user.roles
    if not is_owner and not is_admin:
        return redirect("/materials", message="Недостаточно прав")
    data = MaterialUpdate(name=name, is_private=is_private)
    await material_crud.update_material(db, material, data)
    return redirect(f"/materials/{material_id}", message="Материал обновлён")


@router.post("/materials/{material_id}/delete", response_class=HTMLResponse)
async def delete_material(request: Request, material_id: int, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    material = await material_crud.get_by_id(db, material_id)
    if not material:
        return redirect("/materials", message="Материал не найден")
    is_owner = material.creator_user_id == current_user.id
    is_admin = "ROLE_ADMIN" in current_user.roles
    if not is_owner and not is_admin:
        return redirect("/materials", message="Недостаточно прав")

    # Delete physical file if it's stored locally
    file_link = material.file_link
    if file_link and file_link.startswith("/uploads/materials/"):
        filename = file_link.split("/uploads/materials/")[-1]
        file_path = Path(settings.UPLOAD_DIR) / filename
        if file_path.exists():
            try:
                os.remove(file_path)
            except OSError:
                pass

    await material_crud.delete(db, material)
    return redirect("/materials", message="Материал удалён")

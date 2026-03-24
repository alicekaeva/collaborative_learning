import os
import uuid
import aiofiles
from pathlib import Path
from slugify import slugify
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import BadRequestError

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "video/mp4",
    "video/webm",
    "audio/mpeg",
    "audio/wav",
    "text/plain",
    "application/zip",
    "application/x-zip-compressed",
}


async def save_material(file: UploadFile) -> tuple[str, str]:
    """Save uploaded file to disk. Returns (file_link, mime_type)."""
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise BadRequestError(f"Тип файла '{file.content_type}' не поддерживается")

    # Check size
    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise BadRequestError(f"Файл превышает максимально допустимый размер {settings.MAX_FILE_SIZE_MB}MB")

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    original_name = Path(file.filename or "file").stem
    ext = Path(file.filename or "file").suffix
    safe_name = f"{slugify(original_name)}-{uuid.uuid4().hex[:8]}{ext}"
    file_path = upload_dir / safe_name

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(contents)

    return f"/uploads/materials/{safe_name}", file.content_type


async def delete_file(file_link: str) -> None:
    """Delete a file from disk by its relative link."""
    filename = Path(file_link).name
    file_path = Path(settings.UPLOAD_DIR) / filename
    if file_path.exists():
        os.remove(file_path)

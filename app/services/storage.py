import asyncio
import uuid
import aiofiles
import filetype
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

# Byte sequences that indicate executable/scripting content regardless of declared MIME type
_DANGEROUS_SIGNATURES: list[bytes] = [
    b"<?php",
    b"<?\n",
    b"<?\r",
    b"#!/",
    b"\x7fELF",   # ELF executable (Linux)
    b"MZ",         # PE executable (Windows)
    b"<script",
]


def _is_dangerous_content(data: bytes) -> bool:
    """Return True if the file starts with a known dangerous byte sequence."""
    head = data[:512].lower()
    return any(head.startswith(sig.lower()) for sig in _DANGEROUS_SIGNATURES)


def _detect_mime(data: bytes) -> str | None:
    """Detect MIME type from file bytes using magic signatures (ignores HTTP header)."""
    kind = filetype.guess(data)
    if kind is not None:
        return kind.mime
    # filetype doesn't recognise plain-text or some Office XML; fall back to a
    # conservative check: if the bytes are valid UTF-8 and contain no NUL bytes
    # treat them as text/plain.
    try:
        data[:4096].decode("utf-8")
        if b"\x00" not in data[:4096]:
            return "text/plain"
    except (UnicodeDecodeError, ValueError):
        pass
    return None


async def save_material(file: UploadFile) -> tuple[str, str]:
    """Save uploaded file to disk. Returns (file_link, mime_type)."""
    contents = await file.read()

    if len(contents) > settings.MAX_FILE_SIZE:
        raise BadRequestError(f"Файл превышает максимально допустимый размер {settings.MAX_FILE_SIZE_MB}MB")

    # Detect MIME from actual bytes — never trust the Content-Type HTTP header
    detected_mime = _detect_mime(contents)
    if detected_mime not in ALLOWED_MIME_TYPES:
        raise BadRequestError(f"Тип файла не поддерживается (определён как '{detected_mime}')")

    if _is_dangerous_content(contents):
        raise BadRequestError("Содержимое файла не соответствует допустимому типу")

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    original_name = Path(file.filename or "file").stem
    ext = Path(file.filename or "file").suffix
    safe_name = f"{slugify(original_name)}-{uuid.uuid4().hex[:8]}{ext}"
    file_path = upload_dir / safe_name

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(contents)

    return f"/uploads/materials/{safe_name}", detected_mime


async def delete_file(file_link: str) -> None:
    """Delete a file from disk by its relative link."""
    filename = Path(file_link).name
    file_path = Path(settings.UPLOAD_DIR) / filename
    if file_path.exists():
        await asyncio.to_thread(file_path.unlink, True)

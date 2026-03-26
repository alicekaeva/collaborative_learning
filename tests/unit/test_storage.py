"""Юнит-тесты для app.services.storage — определение magic bytes и валидация MIME-типов."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import UploadFile

from app.core.exceptions import BadRequestError
from app.services.storage import _is_dangerous_content, save_material


# ---------------------------------------------------------------------------
# Вспомогательная фабрика загружаемых файлов
# ---------------------------------------------------------------------------

def _make_upload(content: bytes, content_type: str, filename: str = "file.pdf") -> MagicMock:
    upload = MagicMock(spec=UploadFile)
    upload.content_type = content_type
    upload.filename = filename
    upload.read = AsyncMock(return_value=content)
    return upload


# ---------------------------------------------------------------------------
# _is_dangerous_content — проверка magic bytes
# ---------------------------------------------------------------------------

class TestIsDangerousContent:
    def test_php_opening_tag_detected(self):
        assert _is_dangerous_content(b"<?php echo 'hi'; ?>") is True

    def test_php_short_tag_detected(self):
        assert _is_dangerous_content(b"<?\necho 'x';") is True

    def test_shell_shebang_detected(self):
        assert _is_dangerous_content(b"#!/bin/bash\nrm -rf /") is True

    def test_elf_binary_detected(self):
        assert _is_dangerous_content(b"\x7fELF\x02\x01\x01") is True

    def test_windows_pe_detected(self):
        assert _is_dangerous_content(b"MZ\x90\x00") is True

    def test_script_tag_detected(self):
        assert _is_dangerous_content(b"<script>alert(1)</script>") is True

    def test_pdf_magic_bytes_are_safe(self):
        assert _is_dangerous_content(b"%PDF-1.4\n...") is False

    def test_jpeg_magic_bytes_are_safe(self):
        assert _is_dangerous_content(b"\xff\xd8\xff\xe0" + b"\x00" * 100) is False

    def test_png_magic_bytes_are_safe(self):
        assert _is_dangerous_content(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100) is False

    def test_plain_text_is_safe(self):
        assert _is_dangerous_content(b"Hello, world!\nThis is a text file.") is False

    def test_empty_bytes_are_safe(self):
        assert _is_dangerous_content(b"") is False

    def test_detection_is_case_insensitive(self):
        """'<?PHP' в верхнем регистре тоже должен определяться как опасный."""
        assert _is_dangerous_content(b"<?PHP echo 1;") is True


# ---------------------------------------------------------------------------
# save_material — валидация MIME-типа и содержимого файла
# ---------------------------------------------------------------------------

class TestSaveMaterial:
    async def test_unsupported_mime_type_raises(self):
        upload = _make_upload(b"content", content_type="application/x-executable")
        with pytest.raises(BadRequestError, match="не поддерживается"):
            await save_material(upload)

    async def test_php_content_with_valid_mime_raises(self):
        """Клиент заявляет text/plain, но отправляет PHP — проверка magic bytes ловит."""
        upload = _make_upload(
            b"<?php system($_GET['cmd']); ?>",
            content_type="text/plain",
            filename="readme.txt",
        )
        with pytest.raises(BadRequestError, match="Содержимое файла"):
            await save_material(upload)

    async def test_elf_binary_disguised_as_pdf_raises(self):
        """Клиент лжёт о MIME — ELF-бинарник замаскирован под PDF."""
        upload = _make_upload(
            b"\x7fELF\x02\x01\x01" + b"\x00" * 100,
            content_type="application/pdf",
            filename="doc.pdf",
        )
        with pytest.raises(BadRequestError, match="Содержимое файла"):
            await save_material(upload)

    async def test_valid_pdf_saves_successfully(self, tmp_path):
        """Корректный PDF проходит валидацию и записывается на диск."""
        pdf_content = b"%PDF-1.4\n" + b"x" * 100
        upload = _make_upload(pdf_content, content_type="application/pdf", filename="doc.pdf")

        with patch("app.services.storage.settings") as mock_settings, \
             patch("app.services.storage.aiofiles.open") as mock_open:
            mock_settings.UPLOAD_DIR = str(tmp_path)
            mock_settings.MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 МБ
            mock_file = AsyncMock()
            mock_file.__aenter__ = AsyncMock(return_value=mock_file)
            mock_file.__aexit__ = AsyncMock(return_value=False)
            mock_open.return_value = mock_file

            file_link, mime_type = await save_material(upload)

        assert file_link.startswith("/uploads/materials/")
        assert mime_type == "application/pdf"

    async def test_oversized_file_raises(self, tmp_path):
        """Файл больше лимита отклоняется до записи на диск."""
        big_content = b"%PDF-1.4\n" + b"x" * (60 * 1024 * 1024)  # 60 МБ
        upload = _make_upload(big_content, content_type="application/pdf")

        with patch("app.services.storage.settings") as mock_settings:
            mock_settings.UPLOAD_DIR = str(tmp_path)
            mock_settings.MAX_FILE_SIZE = 50 * 1024 * 1024  # лимит 50 МБ
            mock_settings.MAX_FILE_SIZE_MB = 50

            with pytest.raises(BadRequestError, match="превышает максимально"):
                await save_material(upload)

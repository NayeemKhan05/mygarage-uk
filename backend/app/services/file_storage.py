from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


CHUNK_SIZE = 1024 * 1024


ALLOWED_RECEIPTS = {
    ".pdf": {
        "application/pdf",
    },
    ".jpg": {
        "image/jpeg",
    },
    ".jpeg": {
        "image/jpeg",
    },
    ".png": {
        "image/png",
    },
    ".webp": {
        "image/webp",
    },
}


class ReceiptUploadError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
    ) -> None:
        super().__init__(message)

        self.status_code = status_code


@dataclass
class StoredReceipt:
    original_filename: str
    stored_path: str
    content_type: str
    size_bytes: int


def _has_valid_signature(
    extension: str,
    content: bytes,
) -> bool:
    if extension == ".pdf":
        return content.startswith(
            b"%PDF"
        )

    if extension in {
        ".jpg",
        ".jpeg",
    }:
        return content.startswith(
            b"\xff\xd8\xff"
        )

    if extension == ".png":
        return content.startswith(
            b"\x89PNG\r\n\x1a\n"
        )

    if extension == ".webp":
        return (
            len(content) >= 12
            and content.startswith(
                b"RIFF"
            )
            and content[8:12]
            == b"WEBP"
        )

    return False


async def save_service_receipt(
    upload: UploadFile,
    user_id: int,
    vehicle_id: int,
    service_record_id: int,
) -> StoredReceipt:
    original_filename = (
        upload.filename
        or "receipt"
    )

    extension = Path(
        original_filename
    ).suffix.lower()

    if extension not in ALLOWED_RECEIPTS:
        raise ReceiptUploadError(
            (
                "Receipt must be a PDF, "
                "JPG, PNG or WebP file"
            ),
            status_code=415,
        )

    content_type = (
        upload.content_type
        or "application/octet-stream"
    ).lower()

    if (
        content_type
        not in ALLOWED_RECEIPTS[
            extension
        ]
    ):
        raise ReceiptUploadError(
            (
                "The receipt file type "
                "does not match its extension"
            ),
            status_code=415,
        )

    destination_directory = (
        settings.upload_dir
        / "service_receipts"
        / str(user_id)
        / str(vehicle_id)
        / str(service_record_id)
    )

    destination_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    stored_filename = (
        f"{uuid4().hex}{extension}"
    )

    destination = (
        destination_directory
        / stored_filename
    )

    size = 0
    first_chunk = True

    try:
        with destination.open(
            "wb"
        ) as file_handle:
            while True:
                chunk = await upload.read(
                    CHUNK_SIZE
                )

                if not chunk:
                    break

                if first_chunk:
                    if not _has_valid_signature(
                        extension,
                        chunk,
                    ):
                        raise ReceiptUploadError(
                            (
                                "The receipt file "
                                "contents are invalid"
                            ),
                            status_code=415,
                        )

                    first_chunk = False

                size += len(chunk)

                if (
                    size
                    > settings.max_receipt_size_bytes
                ):
                    raise ReceiptUploadError(
                        (
                            "Receipt exceeds the "
                            f"{settings.max_receipt_size_mb} MB "
                            "file size limit"
                        ),
                        status_code=413,
                    )

                file_handle.write(
                    chunk
                )

        if size == 0:
            raise ReceiptUploadError(
                "Receipt file is empty",
            )

    except Exception:
        destination.unlink(
            missing_ok=True
        )

        raise

    finally:
        await upload.close()

    relative_path = (
        destination.relative_to(
            settings.upload_dir
        )
        .as_posix()
    )

    return StoredReceipt(
        original_filename=original_filename,
        stored_path=relative_path,
        content_type=content_type,
        size_bytes=size,
    )


def resolve_receipt_path(
    stored_path: str,
) -> Path:
    root = settings.upload_dir.resolve()

    candidate = (
        root
        / stored_path
    ).resolve()

    if not candidate.is_relative_to(
        root
    ):
        raise ValueError(
            "Invalid stored receipt path"
        )

    return candidate


def delete_stored_receipt(
    stored_path: str,
) -> None:
    try:
        path = resolve_receipt_path(
            stored_path
        )
    except ValueError:
        return

    path.unlink(
        missing_ok=True
    )

    # Remove any now-empty receipt folders.
    current = path.parent
    root = settings.upload_dir.resolve()

    while (
        current != root
        and current.is_relative_to(
            root
        )
    ):
        try:
            current.rmdir()
        except OSError:
            break

        current = current.parent
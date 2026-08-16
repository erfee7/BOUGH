import logging
import uuid
import urllib.parse

from fastapi import APIRouter, File, HTTPException, Response, UploadFile

from app.db import attachments as db_attachments
from app.schemas.chat import AttachmentResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["attachments"])

# --- Validation constants (module-level, hand-editable) ---
MAX_ATTACHMENT_SIZE = 25 * 1024 * 1024  # 25 MB per file
MAX_FILENAME_LENGTH = 255
_READ_CHUNK_SIZE = 1024 * 1024  # 1 MB


def _detect_mime(data: bytes) -> str | None:
    """
    Identifies the file type by magic number. The detected type is the single
    source of truth — declared extensions and client Content-Types are ignored,
    so a renamed file is stored and transported under its real type.
    """
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    if data.startswith(b"%PDF-"):
        return "application/pdf"
    return None


def _sanitize_filename(name: str | None) -> str:
    """
    Normalizes a client-supplied filename for storage and header use:
    strip path components, drop non-printable and quote characters, cap length.
    Display-only — the backend never uses it as a path.
    """
    if not name:
        return "file"
    name = name.replace("\\", "/").split("/")[-1]
    name = "".join(ch for ch in name if ch.isprintable() and ch != '"')
    name = name.strip()[:MAX_FILENAME_LENGTH]
    return name or "file"


def _content_disposition(filename: str) -> str:
    """Builds a safe Content-Disposition header; uses RFC 5987 encoding for non-ASCII names."""
    try:
        filename.encode("latin-1")
        return f'inline; filename="{filename}"'
    except UnicodeEncodeError:
        return f"inline; filename*=UTF-8''{urllib.parse.quote(filename)}"


async def _read_with_cap(file: UploadFile) -> bytes:
    """
    Reads the upload body in chunks with a hard, server-measured size cap.
    Aborts as soon as the cap is exceeded — we never trust declared sizes.
    """
    chunks = []
    total = 0
    while True:
        chunk = await file.read(_READ_CHUNK_SIZE)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_ATTACHMENT_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds the maximum size of {MAX_ATTACHMENT_SIZE // (1024 * 1024)} MB.",
            )
        chunks.append(chunk)
    return b"".join(chunks)


@router.post("/attachments", response_model=AttachmentResponse)
async def upload_attachment(file: UploadFile = File(...)):
    """Receives a single file, validates it by magic number, and stores it as a standalone blob."""
    filename = _sanitize_filename(file.filename)
    data = await _read_with_cap(file)

    mime_type = _detect_mime(data)
    if mime_type is None:
        raise HTTPException(
            status_code=415,
            detail="Unsupported file type. Allowed types: PNG, JPEG, GIF, WEBP, PDF.",
        )

    # Lazy housekeeping, mirroring expired-session cleanup at login
    purged = await db_attachments.delete_orphaned_attachments()
    if purged:
        logger.info("Upload endpoint purged %d orphaned attachments.", purged)

    attachment_id = await db_attachments.create_attachment(
        filename=filename, mime_type=mime_type, data=data
    )

    # Read back server truth (metadata-only query; never drags the blob out of TOAST)
    records = await db_attachments.fetch_attachment_metadata(ids=[attachment_id])
    return AttachmentResponse.model_validate(records[0])


@router.get("/attachments/{attachment_id}")
async def download_attachment(attachment_id: uuid.UUID):
    """Serves raw attachment bytes for frontend rendering (<img>, <embed>)."""
    record = await db_attachments.fetch_attachment(attachment_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Plain Response, not StreamingResponse: asyncpg already materialized the blob
    return Response(
        content=record["data"],
        media_type=record["mime_type"],
        headers={
            "Content-Disposition": _content_disposition(record["filename"]),
            # Attachment bytes are immutable by design, so caching is safe; private = authenticated content
            "Cache-Control": "private, max-age=86400",
        },
    )
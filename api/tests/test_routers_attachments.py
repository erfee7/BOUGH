import uuid
import pytest
import httpx
from httpx import ASGITransport
from unittest.mock import patch, AsyncMock

from app.main import app
from app.security import get_current_user_id
from app.db import attachments as db_attachments
from app.routers import attachments as attachments_router

PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
JPEG_BYTES = b"\xff\xd8\xff\xe0" + b"\x00" * 100
PDF_BYTES = b"%PDF-1.4\n" + b"\x00" * 100


@pytest.mark.asyncio
async def test_upload_attachment_png(mock_pool):
    """Happy path: PNG upload returns server-measured metadata and stores the exact bytes."""
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/chat/attachments",
                files={"file": ("cat.png", PNG_BYTES, "image/png")},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["mime_type"] == "image/png"
            assert data["filename"] == "cat.png"
            assert data["size"] == len(PNG_BYTES)

            record = await db_attachments.fetch_attachment(uuid.UUID(data["id"]), conn=mock_pool.conn)
            assert record is not None
            assert record["data"] == PNG_BYTES


@pytest.mark.asyncio
async def test_upload_attachment_pdf(mock_pool):
    """Happy path: PDF upload."""
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/chat/attachments",
                files={"file": ("doc.pdf", PDF_BYTES, "application/pdf")},
            )

            assert response.status_code == 200
            assert response.json()["mime_type"] == "application/pdf"


@pytest.mark.asyncio
async def test_upload_detects_real_type_not_declaration(mock_pool):
    """A JPEG renamed to .png with a lying content-type is stored as image/jpeg."""
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/chat/attachments",
                files={"file": ("actually-jpeg.png", JPEG_BYTES, "application/octet-stream")},
            )

            assert response.status_code == 200
            assert response.json()["mime_type"] == "image/jpeg"


@pytest.mark.asyncio
async def test_upload_rejects_unknown_magic(mock_pool):
    """Plain text and PE executables are rejected with 415."""
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            for payload in (b"hello world, definitely not a file", b"MZ\x90\x00" + b"\x00" * 50):
                response = await client.post(
                    "/api/chat/attachments",
                    files={"file": ("innocent.png", payload, "image/png")},
                )
                assert response.status_code == 415


@pytest.mark.asyncio
async def test_upload_rejects_oversize():
    """Uploads over the size cap are rejected with 413 before anything is stored."""
    with patch('app.routers.attachments.db_attachments.create_attachment', new_callable=AsyncMock) as mock_create:
        with patch.object(attachments_router, "MAX_ATTACHMENT_SIZE", 8):
            async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/chat/attachments",
                    files={"file": ("big.png", PNG_BYTES, "image/png")},
                )

                assert response.status_code == 413
                mock_create.assert_not_called()  # Rejected before the write path is ever reached


@pytest.mark.asyncio
async def test_upload_sanitizes_filename(mock_pool):
    """Path components are stripped, quote characters dropped, length capped, empty names fall back."""
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Path traversal attempt -> basename only
            response = await client.post(
                "/api/chat/attachments",
                files={"file": ("../../etc/passwd.png", PNG_BYTES, "image/png")},
            )
            assert response.status_code == 200
            assert response.json()["filename"] == "passwd.png"

            # Whitespace-only -> fallback
            response = await client.post(
                "/api/chat/attachments",
                files={"file": ("   ", PNG_BYTES, "image/png")},
            )
            assert response.status_code == 200
            assert response.json()["filename"] == "file"

            # Overlength -> capped
            response = await client.post(
                "/api/chat/attachments",
                files={"file": ("a" * 300 + ".png", PNG_BYTES, "image/png")},
            )
            assert response.status_code == 200
            assert len(response.json()["filename"]) == 255


@pytest.mark.asyncio
async def test_download_attachment_roundtrip(mock_pool):
    """GET returns the exact bytes with detected Content-Type and inline disposition."""
    attachment_id = await db_attachments.create_attachment(
        filename="cat.png", mime_type="image/png", data=PNG_BYTES, conn=mock_pool.conn
    )

    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/chat/attachments/{attachment_id}")

            assert response.status_code == 200
            assert response.content == PNG_BYTES
            assert response.headers["content-type"] == "image/png"
            assert "inline" in response.headers["content-disposition"]
            assert "cat.png" in response.headers["content-disposition"]


@pytest.mark.asyncio
async def test_download_attachment_non_ascii_filename(mock_pool):
    """Non-ASCII filenames produce an RFC 5987 encoded Content-Disposition without crashing."""
    attachment_id = await db_attachments.create_attachment(
        filename="图片.png", mime_type="image/png", data=PNG_BYTES, conn=mock_pool.conn
    )

    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/chat/attachments/{attachment_id}")

            assert response.status_code == 200
            assert response.headers["content-disposition"].startswith("inline; filename*=UTF-8''")


@pytest.mark.asyncio
async def test_download_attachment_not_found(mock_pool):
    """Fetching a non-existent attachment returns 404."""
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/chat/attachments/{uuid.uuid4()}")
            assert response.status_code == 404


@pytest.mark.asyncio
async def test_upload_purges_orphans(mock_pool):
    """A backdated unreferenced blob is purged by the upload's lazy cleanup."""
    orphan_id = await db_attachments.create_attachment(
        filename="orphan.png", mime_type="image/png", data=b"ooo", conn=mock_pool.conn
    )
    await mock_pool.conn.execute(
        "UPDATE attachments SET created_at = NOW() - INTERVAL '25 hours' WHERE id = $1",
        orphan_id,
    )

    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/chat/attachments",
                files={"file": ("cat.png", PNG_BYTES, "image/png")},
            )
            assert response.status_code == 200

    assert await db_attachments.fetch_attachment(orphan_id, conn=mock_pool.conn) is None


@pytest.mark.asyncio
async def test_attachments_require_auth(mock_pool):
    """Without the auth bypass, both endpoints reject unauthenticated requests with 401."""
    app.dependency_overrides.pop(get_current_user_id, None)
    try:
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            post_response = await client.post(
                "/api/chat/attachments",
                files={"file": ("cat.png", PNG_BYTES, "image/png")},
            )
            get_response = await client.get(f"/api/chat/attachments/{uuid.uuid4()}")

            assert post_response.status_code == 401
            assert get_response.status_code == 401
    finally:
        app.dependency_overrides[get_current_user_id] = lambda: uuid.uuid4()
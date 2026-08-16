import uuid
import pytest
import asyncpg

from app.db.attachments import (
    create_attachment,
    fetch_attachment,
    fetch_attachment_metadata,
    fetch_attachment_data,
    delete_orphaned_attachments,
)

# Fake payloads — magic-number validation is router logic, the DB layer stores whatever it is given
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


@pytest.mark.asyncio
async def test_create_and_fetch_attachment(db_transaction: asyncpg.Connection):
    """Creating an attachment and fetching it back returns identical bytes and server-computed size."""
    attachment_id = await create_attachment(
        filename="cat.png",
        mime_type="image/png",
        data=PNG_BYTES,
        conn=db_transaction,
    )

    result = await fetch_attachment(attachment_id=attachment_id, conn=db_transaction)

    assert result is not None
    assert isinstance(result, dict)  # Enforces no Record type is returned
    assert result['id'] == attachment_id
    assert result['mime_type'] == "image/png"
    assert result['filename'] == "cat.png"
    assert result['size'] == len(PNG_BYTES)  # Size measured server-side from actual bytes
    assert result['data'] == PNG_BYTES


@pytest.mark.asyncio
async def test_fetch_missing_attachment(db_transaction: asyncpg.Connection):
    """Fetching a non-existent attachment returns None."""
    result = await fetch_attachment(attachment_id=uuid.uuid4(), conn=db_transaction)
    assert result is None


@pytest.mark.asyncio
async def test_fetch_attachment_metadata_batch(db_transaction: asyncpg.Connection):
    """Batch metadata fetch returns only existing IDs, and never the blob column."""
    real_1 = await create_attachment(filename="a.png", mime_type="image/png", data=b"aaa", conn=db_transaction)
    real_2 = await create_attachment(filename="b.pdf", mime_type="application/pdf", data=b"bbb", conn=db_transaction)
    bogus = uuid.uuid4()

    results = await fetch_attachment_metadata(ids=[real_1, real_2, bogus], conn=db_transaction)

    assert isinstance(results, list)
    assert all(isinstance(item, dict) for item in results)  # Enforces no Record type is returned
    assert len(results) == 2
    assert all('data' not in item for item in results)  # Metadata only, no blobs
    found_ids = {item['id'] for item in results}
    assert real_1 in found_ids and real_2 in found_ids
    assert bogus not in found_ids


@pytest.mark.asyncio
async def test_fetch_attachment_data_keyed_by_string(db_transaction: asyncpg.Connection):
    """Batch data fetch returns {str(id): bytes}, skipping missing IDs."""
    att_id = await create_attachment(filename="c.png", mime_type="image/png", data=b"ccc", conn=db_transaction)

    blob_map = await fetch_attachment_data(ids=[att_id, uuid.uuid4()], conn=db_transaction)

    for key, value in blob_map.items():
        assert isinstance(key, str)  # Matches the string ids used inside messages.attachments JSONB
        assert isinstance(value, bytes)
    assert blob_map == {str(att_id): b"ccc"}


@pytest.mark.asyncio
async def test_delete_orphaned_attachments(db_transaction: asyncpg.Connection):
    """Purges only old, unreferenced blobs; keeps referenced and fresh ones."""
    from app.db.conversations import create_conversation
    from app.db.messages import create_message

    conversation_id = await create_conversation(title="Test", conn=db_transaction)

    # (a) Old + unreferenced -> deleted
    orphan_id = await create_attachment(filename="orphan.png", mime_type="image/png", data=b"ooo", conn=db_transaction)
    # (b) Old + referenced by a message's attachments JSONB -> kept
    referenced_id = await create_attachment(filename="ref.png", mime_type="image/png", data=b"rrr", conn=db_transaction)
    # (c) Fresh + unreferenced -> kept (still inside the 24h window)
    fresh_id = await create_attachment(filename="fresh.png", mime_type="image/png", data=b"fff", conn=db_transaction)

    # Backdate the two old blobs past the 24h window
    await db_transaction.execute(
        "UPDATE attachments SET created_at = NOW() - INTERVAL '25 hours' WHERE id = ANY($1)",
        [orphan_id, referenced_id],
    )

    # A message referencing the second blob
    await create_message(
        conversation_id=conversation_id,
        role="user",
        content="Look at this",
        attachments=[{"id": str(referenced_id), "mime_type": "image/png", "filename": "ref.png", "size": 3}],
        conn=db_transaction,
    )

    purged = await delete_orphaned_attachments(conn=db_transaction)

    assert purged == 1
    assert await fetch_attachment(attachment_id=orphan_id, conn=db_transaction) is None
    assert await fetch_attachment(attachment_id=referenced_id, conn=db_transaction) is not None
    assert await fetch_attachment(attachment_id=fresh_id, conn=db_transaction) is not None
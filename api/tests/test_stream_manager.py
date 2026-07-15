import asyncio
import uuid
import pytest
from unittest.mock import patch, AsyncMock

from app.core import stream_manager
from app.core.stream_manager import start_stream, get_stream, _active_streams

# --- Mock Data
MOCK_METADATA = {"prompt_tokens": 10, "completion_tokens": 3, "total_tokens": 13}
MOCK_ERROR_DATA = {"message": "API Failed", "type": "APIError"}

# --- Mock Provider Helper ---
async def mock_generate_stream_success(history):
    """Simulates a provider that yields tokens, pauses, yields more, then finishes."""
    yield {"type": "token", "content": "A"}
    yield {"type": "token", "content": "B"}
    
    # Pause to allow the test to connect a listener mid-stream
    await asyncio.sleep(0.1)
    
    yield {"type": "token", "content": "C"}
    yield {"type": "done", "metadata": MOCK_METADATA}

async def mock_generate_stream_error(history):
    """Simulates a provider that fails mid-stream."""
    yield {"type": "token", "content": "Partial"}
    await asyncio.sleep(0.05)
    yield {"type": "error", "error_data": MOCK_ERROR_DATA}

# --- Tests ---

@pytest.mark.asyncio
async def test_start_stream_initializes_state():
    """Tests that start_stream creates an active state and updates DB status."""
    message_id = uuid.uuid4()
    
    with patch('app.core.stream_manager.db_messages.update_message', new_callable = AsyncMock) as mock_update:
        with patch('app.core.stream_manager.generate_stream', new = mock_generate_stream_success):
            start_stream(message_id, [{"role": "user", "content": "Hi"}])
            
            # Give the background task a microsecond to start
            await asyncio.sleep(0.01)
            
            # Assert state is registered
            assert message_id in _active_streams
            
            # Assert DB status updated to streaming
            mock_update.assert_any_call(message_id, status = 'streaming')
            
            # Wait for background task to finish
            await asyncio.sleep(0.5)
            
            # Assert state is cleaned up
            assert message_id not in _active_streams

@pytest.mark.asyncio
async def test_get_stream_catch_up_and_live():
    """Tests the atomic block: catch-up content followed by live tokens safely."""
    message_id = uuid.uuid4()
    
    with patch('app.core.stream_manager.db_messages.update_message', new_callable = AsyncMock):
        with patch('app.core.stream_manager.generate_stream', new = mock_generate_stream_success):
            start_stream(message_id, [{"role": "user", "content": "Hi"}])
            
            # Wait for tokens "A" and "B" to be processed, and hit the sleep(0.1)
            await asyncio.sleep(0.05)
            
            # Now we connect our listener. "AB" is accumulated. "C" is pending.
            events = []
            async for event in get_stream(message_id):
                events.append(event)
                
            # Assert we got the catch-up "AB", the live "C", and the done event
            assert len(events) == 3
            assert events[0] == {"type": "catch_up", "content": "AB"}
            assert events[1] == {"type": "token", "content": "C"}
            assert events[2] == {"type": "done", "metadata": MOCK_METADATA}

@pytest.mark.asyncio
async def test_run_generation_success_db_update():
    """Tests that the worker saves the final accumulated string and metadata to DB."""
    message_id = uuid.uuid4()
    
    with patch('app.core.stream_manager.db_messages.update_message', new_callable = AsyncMock) as mock_update:
        with patch('app.core.stream_manager.generate_stream', new = mock_generate_stream_success):
            start_stream(message_id, [{"role": "user", "content": "Hi"}])
            await asyncio.sleep(0.5) # Wait for completion
            
            # Assert the final DB update contained the accumulated string and metadata
            mock_update.assert_any_call(
                message_id, 
                status = 'complete', 
                content = 'ABC', 
                metadata = MOCK_METADATA
            )

@pytest.mark.asyncio
async def test_run_generation_error_db_update():
    """Tests that the worker saves partial content and error data to DB on failure."""
    message_id = uuid.uuid4()
    
    with patch('app.core.stream_manager.db_messages.update_message', new_callable = AsyncMock) as mock_update:
        with patch('app.core.stream_manager.generate_stream', new = mock_generate_stream_error):
            start_stream(message_id, [{"role": "user", "content": "Hi"}])
            await asyncio.sleep(0.2) # Wait for completion
            
            mock_update.assert_any_call(
                message_id, 
                status = 'error', 
                content = 'Partial', 
                error_data = MOCK_ERROR_DATA
            )

async def collect_events(stream_gen):
    """Helper to consume an async generator into a list."""
    events = []
    async for event in stream_gen:
        events.append(event)
    return events

@pytest.mark.asyncio
async def test_multiple_clients_receive_stream():
    """Tests that multiple concurrent listeners (e.g., multiple tabs) all get catch-up and live tokens."""
    message_id = uuid.uuid4()
    
    with patch('app.core.stream_manager.db_messages.update_message', new_callable = AsyncMock):
        with patch('app.core.stream_manager.generate_stream', new = mock_generate_stream_success):
            start_stream(message_id, [{"role": "user", "content": "Hi"}])
            
            # Wait for "Hello" to be accumulated
            await asyncio.sleep(0.03)
            
            # Connect two clients at the same time
            gen1 = get_stream(message_id)
            gen2 = get_stream(message_id)

            # Connect a third client after some time
            await asyncio.sleep(0.03)
            gen3 = get_stream(message_id)
            
            events1, events2, events3 = await asyncio.gather(
                collect_events(gen1),
                collect_events(gen2),
                collect_events(gen3)
            )
            
            # Assert both clients got the exact same stream
            assert len(events1) == 3
            assert len(events2) == 3
            assert len(events3) == 3

            assert events1[0] == {"type": "catch_up", "content": "AB"}
            assert events2[0] == {"type": "catch_up", "content": "AB"}
            assert events3[0] == {"type": "catch_up", "content": "AB"}
    
            assert events1[1] == {"type": "token", "content": "C"}
            assert events2[1] == {"type": "token", "content": "C"}
            assert events3[1] == {"type": "token", "content": "C"}

            assert events1[2] == {"type": "done", "metadata": MOCK_METADATA}
            assert events2[2] == {"type": "done", "metadata": MOCK_METADATA}
            assert events3[2] == {"type": "done", "metadata": MOCK_METADATA}


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
async def mock_generate_stream_success(history, model = None, parameters = None):
    """Simulates a provider that yields tokens, pauses, yields more, then finishes."""
    yield {"type": "reasoning", "content": "A"}
    yield {"type": "token", "content": "1"}
    
    # Pause to allow the test to connect a listener mid-stream
    await asyncio.sleep(0.1)
    
    yield {"type": "reasoning", "content": "B"}
    yield {"type": "token", "content": "2"}
    yield {"type": "done", "metadata": MOCK_METADATA}

async def mock_generate_stream_error(history, model = None, parameters = None):
    """Simulates a provider that fails mid-stream."""
    yield {"type": "reasoning", "content": "Part"}
    yield {"type": "token", "content": "Partial"}
    await asyncio.sleep(0.05)
    yield {"type": "error", "error_data": MOCK_ERROR_DATA}

async def mock_generate_stream_cancellable(history, model = None, parameters = None):
    """Simulates a provider that yields a token, pauses, yields another, then finishes."""
    yield {"type": "token", "content": "1"}
    await asyncio.sleep(0.2)  # Long pause to allow cancellation mid-stream
    yield {"type": "token", "content": "2"}  # This token should be dropped due to cancellation
    yield {"type": "done", "metadata": {}}

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
            
            # Wait for reasoning "A" and token "1" to be processed, and hit the sleep(0.1)
            await asyncio.sleep(0.05)
            
            # Now we connect our listener. "1" is accumulated content, "A" is accumulated reasoning.
            events = []
            async for event in get_stream(message_id):
                events.append(event)
                
            # Assert we got the catch-up, the live reasoning "B", the live token "2", and the done event
            assert len(events) == 4
            assert events[0] == {"type": "catch_up", "content": "1", "reasoning": "A"}
            assert events[1] == {"type": "reasoning", "content": "B"}
            assert events[2] == {"type": "token", "content": "2"}
            assert events[3] == {"type": "done", "metadata": MOCK_METADATA}

@pytest.mark.asyncio
async def test_start_stream_passes_model_and_parameters_to_provider():
    """Tests that model and parameters from start_stream reach the provider's generate_stream."""
    message_id = uuid.uuid4()
    captured_args = {}
    
    async def capturing_mock(history, model = None, parameters = None):
        captured_args['model'] = model
        captured_args['parameters'] = parameters
        yield {"type": "done", "metadata": {}}
    
    with patch('app.core.stream_manager.db_messages.update_message', new_callable = AsyncMock):
        with patch('app.core.stream_manager.generate_stream', new = capturing_mock):
            start_stream(
                message_id, 
                [{"role": "user", "content": "Hi"}], 
                model = "test-model", 
                parameters = {"temperature": 0.5}
            )
            
            # Wait for the background task to run
            await asyncio.sleep(0.1)
            
            assert captured_args['model'] == "test-model"
            assert captured_args['parameters'] == {"temperature": 0.5}

@pytest.mark.asyncio
async def test_run_generation_success_db_update():
    """Tests that the worker saves the final accumulated string, reasoning, and metadata to DB."""
    message_id = uuid.uuid4()
    
    with patch('app.core.stream_manager.db_messages.update_message', new_callable = AsyncMock) as mock_update:
        with patch('app.core.stream_manager.generate_stream', new = mock_generate_stream_success):
            start_stream(message_id, [{"role": "user", "content": "Hi"}])
            await asyncio.sleep(0.5) # Wait for completion
            
            # Assert the final DB update contained the accumulated string and metadata
            mock_update.assert_any_call(
                message_id, 
                status = 'complete', 
                content = '12', 
                reasoning = 'AB',
                metadata = MOCK_METADATA
            )

@pytest.mark.asyncio
async def test_run_generation_error_db_update():
    """Tests that the worker saves partial content, reasoning, and error data to DB on failure."""
    message_id = uuid.uuid4()
    
    with patch('app.core.stream_manager.db_messages.update_message', new_callable = AsyncMock) as mock_update:
        with patch('app.core.stream_manager.generate_stream', new = mock_generate_stream_error):
            start_stream(message_id, [{"role": "user", "content": "Hi"}])
            await asyncio.sleep(0.2)
            
            mock_update.assert_any_call(
                message_id, 
                status = 'error', 
                content = 'Partial', 
                reasoning = 'Part',
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
            
            # Wait for "1" and "A" to be accumulated
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
            assert len(events1) == 4
            assert len(events2) == 4
            assert len(events3) == 4

            assert events1[0] == {"type": "catch_up", "content": "1", "reasoning": "A"}
            assert events2[0] == {"type": "catch_up", "content": "1", "reasoning": "A"}
            assert events3[0] == {"type": "catch_up", "content": "1", "reasoning": "A"}
    
            assert events1[1] == {"type": "reasoning", "content": "B"}
            assert events2[1] == {"type": "reasoning", "content": "B"}
            assert events3[1] == {"type": "reasoning", "content": "B"}

            assert events1[2] == {"type": "token", "content": "2"}
            assert events2[2] == {"type": "token", "content": "2"}
            assert events3[2] == {"type": "token", "content": "2"}

            assert events1[3] == {"type": "done", "metadata": MOCK_METADATA}
            assert events2[3] == {"type": "done", "metadata": MOCK_METADATA}
            assert events3[3] == {"type": "done", "metadata": MOCK_METADATA}

@pytest.mark.asyncio
async def test_cancel_stream_saves_partial():
    """Tests that cancelling mid-stream saves accumulated content as 'canceled' and drops subsequent tokens."""
    message_id = uuid.uuid4()
    
    with patch('app.core.stream_manager.db_messages.update_message', new_callable=AsyncMock) as mock_update:
        with patch('app.core.stream_manager.generate_stream', new=mock_generate_stream_cancellable):
            start_stream(message_id, [{"role": "user", "content": "Hi"}])
            
            # Wait for "1" to be processed, and hit the sleep(0.2)
            await asyncio.sleep(0.05)
            
            # Request cancellation
            assert stream_manager.cancel_stream(message_id) is True
            
            # Wait for the background task to handle the cancellation and finish
            await asyncio.sleep(0.3)
            
            # Assert the final DB update saved the partial content ("1") as 'canceled'
            mock_update.assert_any_call(
                message_id, 
                status='canceled', 
                content='1', 
                reasoning=''
            )
            
            # Ensure state is cleaned up
            assert message_id not in _active_streams
import pytest
import os
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_ai_client():
    """Fixture providing a mocked OpenAI client."""
    with patch('ai.ai_client') as mock_client:
        mock_client.beta.assistants.create.return_value = MagicMock(id='assistant-123')
        mock_client.beta.assistants.update.return_value = None
        mock_client.beta.threads.create.return_value = MagicMock(id='thread-456')
        mock_client.beta.threads.messages.create.return_value = None
        mock_client.beta.threads.runs.create_and_poll.return_value = MagicMock(
            status='completed', id='run-789'
        )
        mock_client.files.create.return_value = MagicMock(id='file-123')
        mock_client.files.content.return_value = MagicMock()
        mock_client.files.content.return_value.read.return_value = b'test content'
        yield mock_client

@pytest.fixture(autouse=True)
def clean_env():
    """Automatically clean environment variables before each test."""
    # Store original env vars
    original_env = dict(os.environ)
    yield
    # Restore original env vars
    os.environ.clear()
    os.environ.update(original_env)
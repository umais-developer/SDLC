import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_vault():
    return MagicMock()

@pytest.fixture
def mock_graph():
    return MagicMock()

@pytest.fixture
def sample_pdf():
    return b"%PDF-1.4 test content"

import pytest
import json
import os
from pathlib import Path
from .session import Session, APIResponse

# Get the directory of the current file
CURRENT_DIR = Path(__file__).parent

def get_available_test_data(endpoint: str) -> list[str]:
    """Get a list of available test data files for an endpoint."""
    test_data_dir = CURRENT_DIR / "test_data" / endpoint
    return [f.stem for f in test_data_dir.glob("*.json")]

def load_directus_raw_response(endpoint, name):
    """Load directus raw JSON data from a file."""
    file_path = CURRENT_DIR / "test_data" / endpoint / f"{name}.json"
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        pytest.fail(f"Test data file not found: {file_path}")

class MockSession(Session):
    def __init__(self, url: str, token: str):
        super().__init__(url, token)

    def get(self, endpoint: str) -> APIResponse:
        parts = endpoint.split('/')
        prefix = parts[0]  # e.g., 'collections' or 'fields'
        name = parts[1]    # e.g., 'test_collection'
        data = load_directus_raw_response(prefix, name)

        return APIResponse(
            ok=True,
            error_message="",
            duration=1,  # mock duration
            data=data
        )

    def delete(self, endpoint: str, data: dict) -> APIResponse:
        return APIResponse(
            ok=True,
            error_message="",
            duration=1,  # mock duration
            data=None
        )

@pytest.fixture
def mock_session():
    return MockSession("http://example.com", "mock_token")

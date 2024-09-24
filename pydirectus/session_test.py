from pydirectus.session import Session, APIResponse
from pytest import raises
import pytest
import httpx
from unittest.mock import Mock

@pytest.fixture
def api_instance():
    return Session('http://example.com', '123')

def test_make_response_success(api_instance):
    url = "https://api.example.com/data"
    duration = 100
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": [{"id": 1, "name": "Test"}]}
    result = api_instance._make_response(url, duration, mock_response)

    assert isinstance(result, APIResponse)
    assert result.ok is True
    assert result.error_message == ""
    assert result.duration == duration
    assert result.data == [{"id": 1, "name": "Test"}]

def test_make_response_error(api_instance):
    url = "https://api.example.com/data"
    duration = 100
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    result = api_instance._make_response(url, duration, mock_response)

    assert isinstance(result, APIResponse)
    assert result.ok is False
    assert result.error_message == "Not Found"
    assert result.duration == duration
    assert result.data == {}

def test_make_response_ok_no_data(api_instance):
    "this happen when we use delete"
    url = "https://api.example.com/data"
    duration = 100
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 204
    mock_response.content = None
    mock_response.json.return_value = None
    result = api_instance._make_response(url, duration, mock_response)
    assert isinstance(result, APIResponse)
    assert result.ok is True
    assert result.error_message == ""
    assert result.duration == duration
    assert result.data == {}



def test_invalid_token():
    with raises(ValueError):
        Session("http://example.com", "")

def test_invalid_url():
    with raises(ValueError):
        Session("", "123")

def test_ping():
    s = Session("http://localhost", "123")
    assert not s.ping()

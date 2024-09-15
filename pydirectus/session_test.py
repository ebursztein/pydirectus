from pydirectus.session import Session
from pytest import raises

def test_invalid_token():
    with raises(ValueError):
        Session("http://example.com", "")

def test_invalid_url():
    with raises(ValueError):
        Session("", "123")

def test_ping():
    s = Session("http://localhost", "123")
    assert not s.ping()

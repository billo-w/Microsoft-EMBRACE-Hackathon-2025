import pytest
import json
from unittest.mock import patch
from app import app as flask_app

@pytest.fixture
def app():
    flask_app.config.update({"TESTING": True})
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_route(client):
    """Test the index route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data 

@patch('app.requests.post')
def test_process_route_summarize(mock_post, client):
    """Test the /process route with summarization."""
    mock_response = mock_post.return_value
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Mocked summary."}}]
    }

    test_data = {"text": "This is test text.", "summarize": True}
    response = client.post('/process', json=test_data)
    response_data = json.loads(response.data)

    assert response.status_code == 200
    assert response_data['original_text'] == "This is test text."
    assert response_data['summary'] == "Mocked summary."
    mock_post.assert_called_once()

def test_process_route_no_summarize(client):
    """Test the /process route without summarization."""
    test_data = {"text": "Sample text.", "summarize": False}
    response = client.post('/process', json=test_data)
    response_data = json.loads(response.data)

    assert response.status_code == 200
    assert response_data['original_text'] == "Sample text."
    assert response_data['processed_text'] == "Sample text." # Check processed text
    assert response_data['summary'] is None

def test_process_route_too_long(client):
     """Test input length validation."""
     long_text = "a" * 10001 # Exceeds MAX_INPUT_LENGTH
     test_data = {"text": long_text, "summarize": False}
     response = client.post('/process', json=test_data)
     response_data = json.loads(response.data)

     assert response.status_code == 413
     assert "error" in response_data
     assert "Input text too long" in response_data["error"]

# Add more tests for edge cases, error handling, etc.

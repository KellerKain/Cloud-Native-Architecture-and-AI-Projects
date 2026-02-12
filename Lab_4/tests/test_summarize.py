import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestSummarizeEndpoint:
    """Test suite for the POST /summarize endpoint."""

    def test_summarize_valid_request_with_truncation(self):
        """Test valid request that results in truncation."""
        response = client.post(
            "/summarize",
            json={
                "text": "The quick brown fox jumps over the lazy dog and continues running through the forest today",
                "max_length": 5
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == "The quick brown fox jumps"
        assert data["model"] == "placeholder"
        assert data["truncated"] is True

    def test_summarize_valid_request_without_truncation(self):
        """Test valid request that does not result in truncation."""
        response = client.post(
            "/summarize",
            json={
                "text": "The quick brown fox jumps",
                "max_length": 10
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == "The quick brown fox jumps"
        assert data["model"] == "placeholder"
        assert data["truncated"] is False

    def test_summarize_default_max_length(self):
        """Test request without specifying max_length (should default to 100)."""
        text = " ".join(["word"] * 50)  # 50 words, less than default 100
        response = client.post(
            "/summarize",
            json={"text": text}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["truncated"] is False
        assert data["model"] == "placeholder"

    def test_summarize_default_max_length_exceeds_text(self):
        """Test that default max_length (100) can truncate long text."""
        text = " ".join(["word"] * 150)  # 150 words, exceeds default 100
        response = client.post(
            "/summarize",
            json={"text": text}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["truncated"] is True
        # Should have exactly 100 words
        assert len(data["summary"].split()) == 100

    def test_summarize_empty_text(self):
        """Test that empty text is rejected."""
        response = client.post(
            "/summarize",
            json={"text": ""}
        )
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_summarize_whitespace_only_text(self):
        """Test that whitespace-only text is rejected."""
        response = client.post(
            "/summarize",
            json={"text": "   \t\n  "}
        )
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_summarize_missing_text_field(self):
        """Test that missing text field is rejected."""
        response = client.post(
            "/summarize",
            json={"max_length": 10}
        )
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_summarize_invalid_max_length_zero(self):
        """Test that max_length of 0 is rejected (must be >= 1)."""
        response = client.post(
            "/summarize",
            json={
                "text": "The quick brown fox",
                "max_length": 0
            }
        )
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_summarize_invalid_max_length_negative(self):
        """Test that negative max_length is rejected."""
        response = client.post(
            "/summarize",
            json={
                "text": "The quick brown fox",
                "max_length": -5
            }
        )
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_summarize_single_word_text(self):
        """Test text with a single word."""
        response = client.post(
            "/summarize",
            json={
                "text": "Hello",
                "max_length": 10
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == "Hello"
        assert data["truncated"] is False

    def test_summarize_text_with_special_characters(self):
        """Test text containing special characters and punctuation."""
        response = client.post(
            "/summarize",
            json={
                "text": "Hello, world! How are you? I'm doing great! This is a test.",
                "max_length": 5
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["summary"].split()) == 5
        assert data["truncated"] is True

    def test_summarize_text_with_extra_whitespace(self):
        """Test that extra whitespace is properly handled."""
        response = client.post(
            "/summarize",
            json={
                "text": "The   quick    brown     fox",  # Extra spaces
                "max_length": 3
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Should split on whitespace and get first 3 words
        assert data["summary"] == "The quick brown"
        assert data["truncated"] is True

    def test_summarize_response_schema(self):
        """Test that response matches the expected schema."""
        response = client.post(
            "/summarize",
            json={"text": "Test text for schema validation"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check all required fields are present
        assert "summary" in data
        assert "model" in data
        assert "truncated" in data
        
        # Check field types
        assert isinstance(data["summary"], str)
        assert isinstance(data["model"], str)
        assert isinstance(data["truncated"], bool)


class TestHealthEndpoint:
    """Test suite for the GET /health endpoint."""

    def test_health_check(self):
        """Test that health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["message"] == "Service is running"


class TestApiDocumentation:
    """Test suite for OpenAPI documentation endpoints."""

    def test_openapi_schema_available(self):
        """Test that OpenAPI schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "openapi" in response.json()

    def test_swagger_ui_available(self):
        """Test that Swagger UI is available."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

"""
Unit tests for AI service.
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from ai_service import AIService


class TestAIService:
    """Tests for the AIService class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_api_key = "test-key-123"

    def test_init_no_api_key(self):
        """Test initialization without API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Gemini API key not provided"):
                AIService()

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        service = AIService(api_key=self.test_api_key)
        assert service.api_key == self.test_api_key

    @patch("src.ai_service.genai.GenerativeModel")
    def test_summarize_article(self, mock_model):
        """Test article summarization."""
        mock_response = Mock()
        mock_response.text = "This is a summary of the article."
        mock_model.return_value.generate_content.return_value = mock_response

        service = AIService(api_key=self.test_api_key)
        summary = service.summarize_article("Long article text", "Test Title")

        assert summary == "This is a summary of the article."
        assert len(summary.split()) <= 300

    @patch("src.ai_service.genai.GenerativeModel")
    def test_summarize_article_truncates(self, mock_model):
        """Test summary truncation if over 300 words."""
        long_summary = " ".join(["word"] * 350)
        mock_response = Mock()
        mock_response.text = long_summary
        mock_model.return_value.generate_content.return_value = mock_response

        # Clear cache to avoid hitting cached result from previous test
        AIService._load_cache = lambda self: {}

        service = AIService(api_key=self.test_api_key)
        service.cache = {}
        summary = service.summarize_article("Long article text", "Test Title")

        assert len(summary.split()) == 300

    @patch("src.ai_service.genai.GenerativeModel")
    def test_analyze_sentiment_positive(self, mock_model):
        """Test sentiment analysis returning positive."""
        mock_response = Mock()
        mock_response.text = "positive"
        mock_model.return_value.generate_content.return_value = mock_response

        service = AIService(api_key=self.test_api_key)
        sentiment = service.analyze_sentiment("Article text", "Summary")

        assert sentiment == "positive"

    @patch("src.ai_service.genai.GenerativeModel")
    def test_analyze_sentiment_negative(self, mock_model):
        """Test sentiment analysis returning negative."""
        mock_response = Mock()
        mock_response.text = "negative"
        mock_model.return_value.generate_content.return_value = mock_response

        service = AIService(api_key=self.test_api_key)
        service.cache = {}
        sentiment = service.analyze_sentiment("Article text", "Summary")

        assert sentiment == "negative"

    @patch("src.ai_service.genai.GenerativeModel")
    def test_analyze_sentiment_neutral(self, mock_model):
        """Test sentiment analysis returning neutral."""
        mock_response = Mock()
        mock_response.text = "neutral"
        mock_model.return_value.generate_content.return_value = mock_response

        service = AIService(api_key=self.test_api_key)
        service.cache = {}
        sentiment = service.analyze_sentiment("Article text", "Summary")

        assert sentiment == "neutral"

    @patch("src.ai_service.genai.GenerativeModel")
    def test_analyze_sentiment_invalid_fallback(self, mock_model):
        """Test sentiment analysis with invalid response falls back to neutral."""
        mock_response = Mock()
        mock_response.text = "unknown"
        mock_model.return_value.generate_content.return_value = mock_response

        service = AIService(api_key=self.test_api_key)
        service.cache = {}
        sentiment = service.analyze_sentiment("Article text", "Summary")

        assert sentiment == "neutral"

    @patch("src.ai_service.genai.GenerativeModel")
    def test_classify_industry_finance(self, mock_model):
        """Test industry classification."""
        mock_response = Mock()
        mock_response.text = "Finance"
        mock_model.return_value.generate_content.return_value = mock_response

        service = AIService(api_key=self.test_api_key)
        industry = service.classify_industry("Article about banking")

        assert industry == "Finance"

    @patch("src.ai_service.genai.GenerativeModel")
    def test_classify_industry_invalid_fallback(self, mock_model):
        """Test industry classification with invalid response falls back to Other."""
        mock_response = Mock()
        mock_response.text = "Unknown Industry"
        mock_model.return_value.generate_content.return_value = mock_response

        service = AIService(api_key=self.test_api_key)
        industry = service.classify_industry("Article text")

        assert industry == "Other"

    @patch("src.ai_service.genai.GenerativeModel")
    def test_classify_event_type_political(self, mock_model):
        """Test event type classification."""
        mock_response = Mock()
        mock_response.text = "Political Events"
        mock_model.return_value.generate_content.return_value = mock_response

        service = AIService(api_key=self.test_api_key)
        event_type = service.classify_event_type("Article about election")

        assert event_type == "Political Events"

    @patch("src.ai_service.genai.GenerativeModel")
    def test_classify_event_type_invalid_fallback(self, mock_model):
        """Test event type classification with invalid response falls back to Other."""
        mock_response = Mock()
        mock_response.text = "Unknown Event"
        mock_model.return_value.generate_content.return_value = mock_response

        service = AIService(api_key=self.test_api_key)
        event_type = service.classify_event_type("Article text")

        assert event_type == "Other"

    def test_process_article(self):
        """Test full article processing."""
        service = AIService(api_key=self.test_api_key)

        # Mock the methods directly on the instance
        service.summarize_article = lambda text, title: "Test summary"
        service.analyze_sentiment = lambda text, summary: "positive"
        service.classify_industry = lambda text: "Finance"
        service.classify_event_type = lambda text: "Political Events"

        article = {
            "title": "Test Article",
            "full_text": "Test text",
            "source": "Test Source",
            "date": "2024-01-15",
            "url": "http://test.com",
        }

        result = service.process_article(article)

        assert result["summary"] == "Test summary"
        assert result["sentiment"] == "positive"
        assert result["industry"] == "Finance"
        assert result["event_type"] == "Political Events"
        assert "processed_at" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

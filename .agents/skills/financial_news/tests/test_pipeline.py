"""
Unit tests for data pipeline.
"""

import pytest
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pipeline import DataPipeline


class TestDataPipeline:
    """Tests for the DataPipeline class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_data_dir = Path("test_data")
        self.test_data_dir.mkdir(exist_ok=True)
        self.pipeline = DataPipeline(data_dir=str(self.test_data_dir), retention_days=7)

    def teardown_method(self):
        """Clean up test data."""
        for f in self.test_data_dir.glob("*.json"):
            f.unlink()
        self.test_data_dir.rmdir()

    def test_get_today_filename(self):
        """Test today's filename generation."""
        today = datetime.now().strftime("%Y-%m-%d")
        filename = self.pipeline.get_today_filename()
        assert filename == f"{today}.json"

    def test_load_existing_data_empty(self):
        """Test loading data when no files exist."""
        data = self.pipeline.load_existing_data()
        assert len(data) == 7
        assert all(articles == [] for articles in data.values())

    def test_load_existing_data_with_files(self):
        """Test loading data when files exist."""
        today = datetime.now().strftime("%Y-%m-%d")
        test_data = [{"title": "Test"}]

        filepath = self.test_data_dir / f"{today}.json"
        with open(filepath, "w") as f:
            json.dump(test_data, f)

        data = self.pipeline.load_existing_data()
        assert data[today] == test_data

    def test_save_daily_data(self):
        """Test saving daily data."""
        articles = [{"title": "Test Article", "summary": "Test"}]
        today = datetime.now().strftime("%Y-%m-%d")

        self.pipeline.save_daily_data(articles, today)

        filepath = self.test_data_dir / f"{today}.json"
        assert filepath.exists()

        with open(filepath, "r") as f:
            loaded = json.load(f)
        assert loaded == articles

    def test_validate_article_schema_valid(self):
        """Test schema validation with valid article."""
        article = {
            "title": "Test",
            "summary": "Summary",
            "source": "Source",
            "date": "2024-01-15",
            "url": "http://test.com",
            "sentiment": "positive",
            "industry": "Finance",
            "event_type": "Political Events",
        }
        assert self.pipeline.validate_article_schema(article) is True

    def test_validate_article_schema_missing_field(self):
        """Test schema validation with missing field."""
        article = {
            "title": "Test",
            "summary": "Summary",
            "source": "Source",
            "date": "2024-01-15",
            "url": "http://test.com",
            # Missing: sentiment, industry, event_type
        }
        assert self.pipeline.validate_article_schema(article) is False

    def test_prune_old_data(self):
        """Test pruning data older than retention period."""
        old_date = datetime.now() - timedelta(days=10)
        old_file = self.test_data_dir / f"{old_date.strftime('%Y-%m-%d')}.json"

        with open(old_file, "w") as f:
            json.dump([], f)

        self.pipeline.prune_old_data()
        assert not old_file.exists()

    def test_prune_keeps_recent_data(self):
        """Test that recent data is not pruned."""
        recent_date = datetime.now() - timedelta(days=3)
        recent_file = self.test_data_dir / f"{recent_date.strftime('%Y-%m-%d')}.json"

        with open(recent_file, "w") as f:
            json.dump([], f)

        self.pipeline.prune_old_data()
        assert recent_file.exists()

    @patch("src.pipeline.NewsScraper")
    @patch("src.pipeline.AIService")
    def test_run_pipeline(self, mock_ai, mock_scraper):
        """Test full pipeline execution."""
        # Mock scraper
        mock_scraper.return_value.scrape_all.return_value = [
            {
                "title": "Test",
                "full_text": "Text",
                "source": "Src",
                "date": "2024",
                "url": "http://test",
            }
        ]

        # Mock AI service
        mock_ai_instance = Mock()
        mock_ai_instance.process_article.return_value = {
            "title": "Test",
            "summary": "Summary",
            "source": "Src",
            "date": "2024",
            "url": "http://test",
            "sentiment": "positive",
            "industry": "Finance",
            "event_type": "Political Events",
        }
        mock_ai.return_value = mock_ai_instance

        # Set API key
        os.environ["GEMINI_API_KEY"] = "test-key"

        self.pipeline.run_pipeline()

        # Verify data file was created
        today = datetime.now().strftime("%Y-%m-%d")
        filepath = self.test_data_dir / f"{today}.json"
        assert filepath.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Unit tests for news scraper.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from scraper import NewsScraper


class TestNewsScraper:
    """Tests for the NewsScraper class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.scraper = NewsScraper(rate_limit_delay=0)

    def test_init(self):
        """Test scraper initialization."""
        scraper = NewsScraper()
        assert scraper.rate_limit_delay == 2.0
        assert scraper.scraped_urls == set()

    def test_is_duplicate_new_url(self):
        """Test duplicate detection for new URL."""
        self.scraper.scraped_urls = {"http://example.com"}
        assert self.scraper._is_duplicate("http://other.com") is False

    def test_is_duplicate_existing_url(self):
        """Test duplicate detection for existing URL."""
        self.scraper.scraped_urls = {"http://example.com"}
        assert self.scraper._is_duplicate("http://example.com") is True

    @patch("src.scraper.feedparser.parse")
    def test_scrape_ft_articles_empty_feed(self, mock_parse):
        """Test scraping FT with empty feed."""
        mock_feed = Mock()
        mock_feed.entries = []
        mock_parse.return_value = mock_feed

        articles = self.scraper.scrape_ft_articles()
        assert articles == []

    @patch("src.scraper.requests.Session.get")
    @patch("src.scraper.feedparser.parse")
    def test_scrape_ft_article_success(self, mock_parse, mock_get):
        """Test successful FT article scraping."""
        # Mock RSS feed
        mock_entry = Mock()
        mock_entry.link = "http://ft.com/article1"
        mock_entry.title = "Test FT Article"
        mock_entry.published = "2024-01-15"
        mock_entry.summary = "Test summary"

        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed

        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = (
            '<html><h1 class="article-headline">Test FT Article</h1></html>'
        )
        mock_get.return_value = mock_response

        articles = self.scraper.scrape_ft_articles(max_articles=1)

        assert len(articles) == 1
        assert articles[0]["title"] == "Test FT Article"
        assert articles[0]["source"] == "Financial Times"

    @patch("src.scraper.requests.Session.get")
    @patch("src.scraper.feedparser.parse")
    def test_scrape_ft_article_paywall(self, mock_parse, mock_get):
        """Test FT article with paywall."""
        mock_entry = Mock()
        mock_entry.link = "http://ft.com/article1"
        mock_entry.title = "Test FT Article"

        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed

        # Mock paywall response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<div class="js-article-paywall">Paywall</div>'
        mock_get.return_value = mock_response

        articles = self.scraper.scrape_ft_articles(max_articles=1)

        assert len(articles) == 1
        assert articles[0]["is_paywalled"] is True

    @patch("src.scraper.feedparser.parse")
    def test_scrape_ap_news_empty_feed(self, mock_parse):
        """Test scraping AP News with empty feed."""
        mock_feed = Mock()
        mock_feed.entries = []
        mock_parse.return_value = mock_feed

        articles = self.scraper.scrape_ap_news_articles()
        assert articles == []

    @patch("src.scraper.requests.Session.get")
    @patch("src.scraper.feedparser.parse")
    def test_scrape_ap_article_success(self, mock_parse, mock_get):
        """Test successful AP News article scraping."""
        mock_entry = Mock()
        mock_entry.link = "http://apnews.com/article1"
        mock_entry.title = "Test AP Article"
        mock_entry.published = "2024-01-15"

        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<h1 class="Page-headline">Test AP Article</h1>'
        mock_get.return_value = mock_response

        articles = self.scraper.scrape_ap_news_articles(max_articles=1)

        assert len(articles) == 1
        assert articles[0]["source"] == "AP News"

    def test_scrape_all(self):
        """Test scraping from all sources."""
        # Override methods on instance
        self.scraper.scrape_ft_articles = lambda max_articles=10: [
            {"title": "FT Article", "url": "ft.com"}
        ]
        self.scraper.scrape_ap_news_articles = lambda max_articles=10: [
            {"title": "AP Article", "url": "ap.com"}
        ]

        articles = self.scraper.scrape_all()

        assert len(articles) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

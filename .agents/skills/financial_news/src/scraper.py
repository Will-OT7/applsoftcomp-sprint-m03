"""
Financial news scraper for Financial Times and AP News.
Extracts article title, full text, source, date, and URL.
Handles paywalls gracefully and deduplicates by URL.
"""

import time
from datetime import datetime, timedelta
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import feedparser


class NewsScraper:
    """Scraper for financial news from FT and AP News."""

    def __init__(self, rate_limit_delay: float = 2.0):
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        self.scraped_urls = set()

    def scrape_ft_articles(self, max_articles: int = 10) -> list[dict]:
        """Scrape free articles from Financial Times."""
        articles = []
        # FT RSS feed for finance section
        ft_feed_url = "https://www.ft.com/companies/finance?format=rss"

        try:
            feed = feedparser.parse(ft_feed_url)
            for entry in feed.entries[:max_articles]:
                article = self._extract_ft_article(entry)
                if article and not self._is_duplicate(article["url"]):
                    articles.append(article)
                    self.scraped_urls.add(article["url"])
                    time.sleep(self.rate_limit_delay)
        except Exception as e:
            print(f"Error scraping FT: {e}")

        return articles

    def scrape_ap_news_articles(self, max_articles: int = 10) -> list[dict]:
        """Scrape articles from AP News finance section."""
        articles = []
        # AP News RSS feed for business
        ap_feed_url = "https://feeds.apnews.com/apf-businessfinancial"

        try:
            feed = feedparser.parse(ap_feed_url)
            for entry in feed.entries[:max_articles]:
                article = self._extract_ap_article(entry)
                if article and not self._is_duplicate(article["url"]):
                    articles.append(article)
                    self.scraped_urls.add(article["url"])
                    time.sleep(self.rate_limit_delay)
        except Exception as e:
            print(f"Error scraping AP News: {e}")

        return articles

    def _extract_ft_article(self, entry) -> dict | None:
        """Extract article data from FT RSS entry."""
        try:
            url = entry.link
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                return self._create_ft_fallback(entry)

            soup = BeautifulSoup(response.text, "html.parser")

            # Check for paywall
            paywall = soup.find("div", class_="js-article-paywall")
            if paywall:
                return self._create_ft_fallback(entry, is_paywalled=True)

            title = soup.find("h1", class_="article-headline")
            title = title.get_text(strip=True) if title else entry.title

            # Try to get full text
            content_div = soup.find("div", class_="article-body")
            if content_div:
                paragraphs = content_div.find_all("p")
                full_text = " ".join([p.get_text(strip=True) for p in paragraphs])
            else:
                full_text = entry.summary if hasattr(entry, "summary") else entry.title

            # Extract date
            pub_date = (
                entry.published
                if hasattr(entry, "published")
                else datetime.now().isoformat()
            )

            return {
                "title": title,
                "full_text": full_text,
                "source": "Financial Times",
                "date": pub_date,
                "url": url,
                "is_paywalled": False,
            }
        except Exception as e:
            print(f"Error extracting FT article: {e}")
            return self._create_ft_fallback(entry)

    def _create_ft_fallback(self, entry, is_paywalled: bool = False) -> dict:
        """Create fallback article data from RSS entry."""
        return {
            "title": entry.title,
            "full_text": entry.summary if hasattr(entry, "summary") else entry.title,
            "source": "Financial Times",
            "date": entry.published
            if hasattr(entry, "published")
            else datetime.now().isoformat(),
            "url": entry.link,
            "is_paywalled": is_paywalled,
        }

    def _extract_ap_article(self, entry) -> dict | None:
        """Extract article data from AP News RSS entry."""
        try:
            url = entry.link
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                return self._create_ap_fallback(entry)

            soup = BeautifulSoup(response.text, "html.parser")

            title = soup.find("h1", class_="Page-headline")
            title = title.get_text(strip=True) if title else entry.title

            # Get full text
            content_div = soup.find("div", class_="RichTextStoryBody")
            if content_div:
                paragraphs = content_div.find_all("p")
                full_text = " ".join([p.get_text(strip=True) for p in paragraphs])
            else:
                full_text = entry.summary if hasattr(entry, "summary") else entry.title

            # Extract date
            pub_date = (
                entry.published
                if hasattr(entry, "published")
                else datetime.now().isoformat()
            )

            return {
                "title": title,
                "full_text": full_text,
                "source": "AP News",
                "date": pub_date,
                "url": url,
                "is_paywalled": False,
            }
        except Exception as e:
            print(f"Error extracting AP article: {e}")
            return self._create_ap_fallback(entry)

    def _create_ap_fallback(self, entry) -> dict:
        """Create fallback article data from RSS entry."""
        return {
            "title": entry.title,
            "full_text": entry.summary if hasattr(entry, "summary") else entry.title,
            "source": "AP News",
            "date": entry.published
            if hasattr(entry, "published")
            else datetime.now().isoformat(),
            "url": entry.link,
            "is_paywalled": False,
        }

    def _is_duplicate(self, url: str) -> bool:
        """Check if URL has already been scraped."""
        return url in self.scraped_urls

    def scrape_all(self, target_per_industry: int = 2) -> list[dict]:
        """Scrape from all sources."""
        all_articles = []

        # Scrape from both sources
        ft_articles = self.scrape_ft_articles(max_articles=target_per_industry * 5)
        ap_articles = self.scrape_ap_news_articles(max_articles=target_per_industry * 5)

        all_articles.extend(ft_articles)
        all_articles.extend(ap_articles)

        return all_articles


def main():
    """Main entry point for scraper."""
    scraper = NewsScraper()
    articles = scraper.scrape_all(target_per_industry=2)

    print(f"Scraped {len(articles)} articles")
    for article in articles:
        print(f"  - {article['title']} ({article['source']})")

    return articles


if __name__ == "__main__":
    main()

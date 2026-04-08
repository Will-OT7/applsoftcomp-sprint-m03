"""
Financial news scraper for Financial Times, AP News, and Reuters.
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
    """Scraper for financial news from multiple sources."""

    FT_FEEDS = [
        "https://www.ft.com/companies?format=rss",
        "https://www.ft.com/technology?format=rss",
        "https://www.ft.com/markets?format=rss",
    ]

    AP_FEEDS = [
        "https://apnews.com/rss/top-news",
        "https://apnews.com/rss/business-news",
    ]

    REUTERS_FEEDS = [
        "https://feeds.reuters.com/Reuters/businessNews",
        "https://feeds.reuters.com/reuters/businessNews",
    ]

    INVESTING_FEEDS = [
        "https://www.investing.com/rss/news.rss",
        "https://www.investing.com/rss/stock_market.rss",
    ]

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

        for idx, ft_feed_url in enumerate(self.FT_FEEDS):
            try:
                print(f"  Trying FT feed {idx + 1}/{len(self.FT_FEEDS)}: {ft_feed_url}")
                feed = feedparser.parse(ft_feed_url)

                if not feed.entries:
                    print(f"    Warning: FT feed returned 0 entries")
                    continue

                print(f"    Found {len(feed.entries)} entries in feed")

                for entry in feed.entries[:max_articles]:
                    try:
                        article = self._extract_ft_article(entry)
                        if article and not self._is_duplicate(article["url"]):
                            articles.append(article)
                            self.scraped_urls.add(article["url"])
                            time.sleep(self.rate_limit_delay)

                            if len(articles) >= max_articles:
                                print(
                                    f"    Collected {len(articles)} articles, stopping"
                                )
                                break
                    except Exception as e:
                        print(f"    Error extracting FT article: {e}")
                        continue

                if articles:
                    print(f"  Successfully scraped {len(articles)} articles from FT")
                    break

            except Exception as e:
                print(f"  Error accessing FT feed {ft_feed_url}: {e}")
                continue

        if not articles:
            print("  Warning: No FT articles scraped from any feed")

        return articles

    def scrape_ap_news_articles(self, max_articles: int = 10) -> list[dict]:
        """Scrape articles from AP News business section."""
        articles = []

        for idx, ap_feed_url in enumerate(self.AP_FEEDS):
            try:
                print(f"  Trying AP feed {idx + 1}/{len(self.AP_FEEDS)}: {ap_feed_url}")
                feed = feedparser.parse(ap_feed_url)

                if not feed.entries:
                    print(f"    Warning: AP feed returned 0 entries")
                    continue

                print(f"    Found {len(feed.entries)} entries in feed")

                for entry in feed.entries[:max_articles]:
                    try:
                        article = self._extract_ap_article(entry)
                        if article and not self._is_duplicate(article["url"]):
                            articles.append(article)
                            self.scraped_urls.add(article["url"])
                            time.sleep(self.rate_limit_delay)

                            if len(articles) >= max_articles:
                                print(
                                    f"    Collected {len(articles)} articles, stopping"
                                )
                                break
                    except Exception as e:
                        print(f"    Error extracting AP article: {e}")
                        continue

                if articles:
                    print(
                        f"  Successfully scraped {len(articles)} articles from AP News"
                    )
                    break

            except Exception as e:
                print(f"  Error accessing AP feed {ap_feed_url}: {e}")
                continue

        if not articles:
            print("  Warning: No AP News articles scraped from any feed")

        return articles

    def scrape_reuters_articles(self, max_articles: int = 10) -> list[dict]:
        """Scrape articles from Reuters business section."""
        articles = []

        for idx, reuters_feed_url in enumerate(self.REUTERS_FEEDS):
            try:
                print(
                    f"  Trying Reuters feed {idx + 1}/{len(self.REUTERS_FEEDS)}: {reuters_feed_url}"
                )
                feed = feedparser.parse(reuters_feed_url)

                if not feed.entries:
                    print(f"    Warning: Reuters feed returned 0 entries")
                    continue

                print(f"    Found {len(feed.entries)} entries in feed")

                for entry in feed.entries[:max_articles]:
                    try:
                        article = self._extract_reuters_article(entry)
                        if article and not self._is_duplicate(article["url"]):
                            articles.append(article)
                            self.scraped_urls.add(article["url"])
                            time.sleep(self.rate_limit_delay)

                            if len(articles) >= max_articles:
                                print(
                                    f"    Collected {len(articles)} articles, stopping"
                                )
                                break
                    except Exception as e:
                        print(f"    Error extracting Reuters article: {e}")
                        continue

                if articles:
                    print(
                        f"  Successfully scraped {len(articles)} articles from Reuters"
                    )
                    break

            except Exception as e:
                print(f"  Error accessing Reuters feed {reuters_feed_url}: {e}")
                continue

        if not articles:
            print("  Warning: No Reuters articles scraped from any feed")

        return articles

    def scrape_investing_articles(self, max_articles: int = 10) -> list[dict]:
        """Scrape articles from Investing.com."""
        articles = []

        for idx, investing_feed_url in enumerate(self.INVESTING_FEEDS):
            try:
                print(
                    f"  Trying Investing.com feed {idx + 1}/{len(self.INVESTING_FEEDS)}: {investing_feed_url}"
                )
                feed = feedparser.parse(investing_feed_url)

                if not feed.entries:
                    print(f"    Warning: Investing.com feed returned 0 entries")
                    continue

                print(f"    Found {len(feed.entries)} entries in feed")

                for entry in feed.entries[:max_articles]:
                    try:
                        article = self._extract_investing_article(entry)
                        if article and not self._is_duplicate(article["url"]):
                            articles.append(article)
                            self.scraped_urls.add(article["url"])
                            time.sleep(self.rate_limit_delay)

                            if len(articles) >= max_articles:
                                print(
                                    f"    Collected {len(articles)} articles, stopping"
                                )
                                break
                    except Exception as e:
                        print(f"    Error extracting Investing.com article: {e}")
                        continue

                if articles:
                    print(
                        f"  Successfully scraped {len(articles)} articles from Investing.com"
                    )
                    break

            except Exception as e:
                print(f"  Error accessing Investing.com feed {investing_feed_url}: {e}")
                continue

        if not articles:
            print("  Warning: No Investing.com articles scraped from any feed")

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

    def _extract_reuters_article(self, entry) -> dict | None:
        """Extract article data from Reuters RSS entry."""
        try:
            url = entry.link
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                print(
                    f"    Reuters article failed with status {response.status_code}: {url}"
                )
                return self._create_reuters_fallback(entry)

            soup = BeautifulSoup(response.text, "html.parser")

            title = soup.find("h1", class_="article-headline")
            title = title.get_text(strip=True) if title else entry.title

            content_div = soup.find("div", class_="article-body")
            if content_div:
                paragraphs = content_div.find_all("p")
                full_text = " ".join([p.get_text(strip=True) for p in paragraphs])
            else:
                full_text = entry.summary if hasattr(entry, "summary") else entry.title

            pub_date = (
                entry.published
                if hasattr(entry, "published")
                else datetime.now().isoformat()
            )

            return {
                "title": title,
                "full_text": full_text,
                "source": "Reuters",
                "date": pub_date,
                "url": url,
                "is_paywalled": False,
            }
        except Exception as e:
            print(f"    Error extracting Reuters article: {e}")
            return self._create_reuters_fallback(entry)

    def _create_reuters_fallback(self, entry) -> dict:
        """Create fallback article data from RSS entry."""
        return {
            "title": entry.title,
            "full_text": entry.summary if hasattr(entry, "summary") else entry.title,
            "source": "Reuters",
            "date": entry.published
            if hasattr(entry, "published")
            else datetime.now().isoformat(),
            "url": entry.link,
            "is_paywalled": False,
        }

    def _extract_investing_article(self, entry) -> dict | None:
        """Extract article data from Investing.com RSS entry."""
        try:
            url = entry.link
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                print(
                    f"    Investing.com article failed with status {response.status_code}: {url}"
                )
                return self._create_investing_fallback(entry)

            soup = BeautifulSoup(response.text, "html.parser")

            title = soup.find("h1")
            title = title.get_text(strip=True) if title else entry.title

            content_div = soup.find("div", class_="contentSection") or soup.find(
                "article"
            )
            if content_div:
                paragraphs = content_div.find_all("p")
                full_text = " ".join([p.get_text(strip=True) for p in paragraphs])
            else:
                full_text = entry.summary if hasattr(entry, "summary") else entry.title

            pub_date = (
                entry.published
                if hasattr(entry, "published")
                else datetime.now().isoformat()
            )

            return {
                "title": title,
                "full_text": full_text,
                "source": "Investing.com",
                "date": pub_date,
                "url": url,
                "is_paywalled": False,
            }
        except Exception as e:
            print(f"    Error extracting Investing.com article: {e}")
            return self._create_investing_fallback(entry)

    def _create_investing_fallback(self, entry) -> dict:
        """Create fallback article data from RSS entry."""
        return {
            "title": entry.title,
            "full_text": entry.summary if hasattr(entry, "summary") else entry.title,
            "source": "Investing.com",
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
        """Scrape from all sources with fallback."""
        all_articles = []

        print("Scraping Financial Times...")
        ft_articles = self.scrape_ft_articles(max_articles=target_per_industry * 5)
        print(f"  Total FT articles: {len(ft_articles)}")

        print("Scraping AP News...")
        ap_articles = self.scrape_ap_news_articles(max_articles=target_per_industry * 5)
        print(f"  Total AP articles: {len(ap_articles)}")

        print("Scraping Reuters...")
        reuters_articles = self.scrape_reuters_articles(
            max_articles=target_per_industry * 5
        )
        print(f"  Total Reuters articles: {len(reuters_articles)}")

        print("Scraping Investing.com...")
        investing_articles = self.scrape_investing_articles(
            max_articles=target_per_industry * 5
        )
        print(f"  Total Investing.com articles: {len(investing_articles)}")

        all_articles.extend(ft_articles)
        all_articles.extend(ap_articles)
        all_articles.extend(reuters_articles)
        all_articles.extend(investing_articles)

        print(f"Total articles scraped: {len(all_articles)}")

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

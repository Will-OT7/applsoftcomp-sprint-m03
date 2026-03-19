"""
Data pipeline for financial news.
Manages 7-day rolling window, JSON storage, and data aggregation.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from src.scraper import NewsScraper
from src.ai_service import AIService


class DataPipeline:
    """Pipeline for processing and storing financial news data."""

    def __init__(self, data_dir: str = "data", retention_days: int = 7):
        self.data_dir = Path(data_dir)
        self.retention_days = retention_days
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def get_today_filename(self) -> str:
        """Generate filename for today's data."""
        return f"{datetime.now().strftime('%Y-%m-%d')}.json"

    def load_existing_data(self) -> dict[str, list]:
        """Load existing data files within retention window."""
        data = {}
        today = datetime.now()

        for i in range(self.retention_days):
            date = today - timedelta(days=i)
            filename = f"{date.strftime('%Y-%m-%d')}.json"
            filepath = self.data_dir / filename

            if filepath.exists():
                with open(filepath, "r") as f:
                    data[date.strftime("%Y-%m-%d")] = json.load(f)
            else:
                data[date.strftime("%Y-%m-%d")] = []

        return data

    def prune_old_data(self):
        """Remove data files older than retention period."""
        cutoff = datetime.now() - timedelta(days=self.retention_days)

        for filepath in self.data_dir.glob("*.json"):
            try:
                file_date = datetime.strptime(filepath.stem, "%Y-%m-%d")
                if file_date < cutoff:
                    filepath.unlink()
                    print(f"Pruned old data: {filepath.name}")
            except ValueError:
                pass  # Skip files with invalid date format

    def save_daily_data(self, articles: list[dict], date_str: str | None = None):
        """Save articles to daily JSON file."""
        date_str = date_str or datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str}.json"
        filepath = self.data_dir / filename

        with open(filepath, "w") as f:
            json.dump(articles, f, indent=2)

        print(f"Saved {len(articles)} articles to {filename}")

    def validate_article_schema(self, article: dict) -> bool:
        """Validate article has required fields."""
        required_fields = [
            "title",
            "summary",
            "source",
            "date",
            "url",
            "sentiment",
            "industry",
            "event_type",
        ]
        return all(field in article for field in required_fields)

    def run_pipeline(self):
        """Execute the full pipeline: scrape, process, save."""
        print("Starting data pipeline...")

        # Initialize services
        scraper = NewsScraper()
        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            print("Error: GEMINI_API_KEY not set")
            return

        ai_service = AIService(api_key=api_key)

        # Scrape articles
        print("Scraping articles...")
        raw_articles = scraper.scrape_all(target_per_industry=2)
        print(f"Scraped {len(raw_articles)} raw articles")

        # Process with AI
        print("Processing articles with AI...")
        processed_articles = []
        for article in raw_articles:
            try:
                processed = ai_service.process_article(article)
                if self.validate_article_schema(processed):
                    processed_articles.append(processed)
                else:
                    print(
                        f"  Skipped invalid article: {article.get('title', 'Unknown')}"
                    )
            except Exception as e:
                print(f"  Error processing article: {e}")

        # Save today's data
        today_str = datetime.now().strftime("%Y-%m-%d")
        self.save_daily_data(processed_articles, today_str)

        # Prune old data
        self.prune_old_data()

        # Generate aggregated data
        self.generate_aggregates()

        print("Pipeline complete!")

    def generate_aggregates(self):
        """Generate aggregated metrics for charts."""
        data = self.load_existing_data()

        # Aggregate by date, industry, sentiment
        aggregates = {"by_date": {}, "by_industry": {}, "sentiment_trends": {}}

        for date_str, articles in data.items():
            aggregates["by_date"][date_str] = len(articles)

            for article in articles:
                industry = article.get("industry", "Other")
                sentiment = article.get("sentiment", "neutral")

                if industry not in aggregates["by_industry"]:
                    aggregates["by_industry"][industry] = 0
                    aggregates["sentiment_trends"][industry] = {
                        "positive": 0,
                        "negative": 0,
                        "neutral": 0,
                    }

                aggregates["by_industry"][industry] += 1
                aggregates["sentiment_trends"][industry][sentiment] += 1

        # Save aggregates
        aggregates_path = self.data_dir / "aggregates.json"
        with open(aggregates_path, "w") as f:
            json.dump(aggregates, f, indent=2)

        print(f"Generated aggregates for {len(data)} days")


def main():
    """Main entry point for pipeline."""
    pipeline = DataPipeline()
    pipeline.run_pipeline()


if __name__ == "__main__":
    main()

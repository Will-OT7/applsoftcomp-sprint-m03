"""
AI summarization service using Google Gemini API.
Generates summaries (max 300 words), analyzes sentiment,
and classifies industry and event type.
"""

import os
import json
from pathlib import Path
from datetime import datetime
import google.generativeai as genai


class AIService:
    """AI service for article summarization and classification."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not provided")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.cache_file = Path("data/api_cache.json")
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        """Load API cache from file."""
        if self.cache_file.exists():
            with open(self.cache_file, "r") as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        """Save API cache to file."""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f, indent=2)

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key from text."""
        return f"{len(text)}:{text[:100]}"

    def summarize_article(self, article_text: str, title: str) -> str:
        """Generate summary with max 300 words, including quotes where applicable."""
        cache_key = self._get_cache_key(article_text)
        if cache_key in self.cache:
            return self.cache[cache_key]["summary"]

        prompt = f"""
Summarize the following news article in maximum 300 words. 
Include direct quotes from the article where relevant.
Be concise and focus on the key financial information.

Title: {title}

Article:
{article_text}

Summary:
"""

        try:
            response = self.model.generate_content(prompt)
            summary = response.text.strip()

            # Ensure summary is within 300 words
            words = summary.split()
            if len(words) > 300:
                summary = " ".join(words[:300])

            self.cache[cache_key] = {
                "summary": summary,
                "timestamp": datetime.now().isoformat(),
            }
            self._save_cache()

            return summary
        except Exception as e:
            print(f"Error summarizing article: {e}")
            return article_text[:500]  # Fallback to truncated text

    def analyze_sentiment(self, article_text: str, summary: str) -> str:
        """Analyze sentiment and return simple label: positive, negative, or neutral."""
        cache_key = f"sentiment:{len(article_text)}:{article_text[:50]}"
        if cache_key in self.cache:
            return self.cache[cache_key]["sentiment"]

        prompt = f"""
Analyze the sentiment of this financial news article.
Respond with ONLY one word: positive, negative, or neutral.

Summary: {summary}

Sentiment:
"""

        try:
            response = self.model.generate_content(prompt)
            sentiment = response.text.strip().lower()

            # Ensure valid sentiment label
            if sentiment not in ["positive", "negative", "neutral"]:
                sentiment = "neutral"

            self.cache[cache_key] = {
                "sentiment": sentiment,
                "timestamp": datetime.now().isoformat(),
            }
            self._save_cache()

            return sentiment
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return "neutral"

    def classify_industry(self, article_text: str) -> str:
        """Classify article into industry category."""
        industries = [
            "Technology",
            "Finance",
            "Healthcare",
            "Energy",
            "Retail",
            "Manufacturing",
            "Other",
        ]

        cache_key = f"industry:{len(article_text)}:{article_text[:50]}"
        if cache_key in self.cache:
            return self.cache[cache_key]["industry"]

        prompt = f"""
Classify this financial news article into one of these industries:
{", ".join(industries)}

Respond with ONLY the industry name.

Article summary: {article_text[:500]}

Industry:
"""

        try:
            response = self.model.generate_content(prompt)
            industry = response.text.strip().title()

            # Validate industry
            if industry not in industries:
                industry = "Other"

            self.cache[cache_key] = {
                "industry": industry,
                "timestamp": datetime.now().isoformat(),
            }
            self._save_cache()

            return industry
        except Exception as e:
            print(f"Error classifying industry: {e}")
            return "Other"

    def classify_event_type(self, article_text: str) -> str:
        """Classify event type: rate changes, political events, environmental events, or other."""
        event_types = [
            "Rate Changes",
            "Political Events",
            "Environmental Events",
            "Other",
        ]

        cache_key = f"event:{len(article_text)}:{article_text[:50]}"
        if cache_key in self.cache:
            return self.cache[cache_key]["event_type"]

        prompt = f"""
Classify this financial news article into one of these event types:
{", ".join(event_types)}

Respond with ONLY the event type name.

Article summary: {article_text[:500]}

Event Type:
"""

        try:
            response = self.model.generate_content(prompt)
            event_type = response.text.strip().title()

            # Validate event type
            if event_type not in event_types:
                event_type = "Other"

            self.cache[cache_key] = {
                "event_type": event_type,
                "timestamp": datetime.now().isoformat(),
            }
            self._save_cache()

            return event_type
        except Exception as e:
            print(f"Error classifying event type: {e}")
            return "Other"

    def process_article(self, article: dict) -> dict:
        """Process a single article through all AI services."""
        full_text = article.get("full_text", article.get("title", ""))
        title = article.get("title", "")

        print(f"  Processing: {title}")

        summary = self.summarize_article(full_text, title)
        sentiment = self.analyze_sentiment(full_text, summary)
        industry = self.classify_industry(full_text)
        event_type = self.classify_event_type(full_text)

        return {
            **article,
            "summary": summary,
            "sentiment": sentiment,
            "industry": industry,
            "event_type": event_type,
            "processed_at": datetime.now().isoformat(),
        }


def main():
    """Main entry point for AI service testing."""
    # Test with sample article
    test_article = {
        "title": "Test Article",
        "full_text": "This is a test article about financial markets.",
        "source": "Test Source",
        "date": datetime.now().isoformat(),
        "url": "https://example.com",
    }

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not set")
        return

    service = AIService(api_key=api_key)
    result = service.process_article(test_article)

    print(f"\nProcessed article:")
    print(f"  Summary: {result['summary'][:100]}...")
    print(f"  Sentiment: {result['sentiment']}")
    print(f"  Industry: {result['industry']}")
    print(f"  Event Type: {result['event_type']}")


if __name__ == "__main__":
    main()

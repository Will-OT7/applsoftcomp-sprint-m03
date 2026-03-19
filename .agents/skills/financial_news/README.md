# Financial News Assistant

A personalized AI assistant that summarizes 7 days of financial news from Financial Times and AP News, hosted as a static website on GitHub Pages.

## Overview

The system uses:
- **GitHub Actions** to scrape news daily at 5 AM UTC
- **Google Gemini API** for article summarization and sentiment analysis
- **Chart.js** for interactive visualizations
- **localStorage** for user preferences and feedback

## Features

- **Daily News Scraping**: Automatically scrapes Financial Times and AP News
- **AI Summarization**: 300-word max summaries with quotes
- **Sentiment Analysis**: Positive, negative, or neutral labels
- **Industry Classification**: Technology, Finance, Healthcare, Energy, Retail, Manufacturing, Other
- **Event Type Classification**: Rate Changes, Political Events, Environmental Events
- **Personalization**: User-selectable industries and event types
- **Feedback System**: Thumbs up/down for news ranking
- **7-Day Rolling Window**: Automatic data pruning
- **Interactive Charts**: Sentiment trends and news volume

## Architecture

```
.agents/skills/financial_news/
├── .github/workflows/
│   └── financial_news.yml    # Daily GitHub Action
├── src/
│   ├── scraper.py            # News scraper (FT + AP)
│   ├── ai_service.py         # Gemini API wrapper
│   └── pipeline.py           # Data pipeline
├── tests/
│   ├── test_scraper.py
│   ├── test_ai_service.py
│   └── test_pipeline.py
├── data/                     # Generated JSON data
├── index.html                # Dashboard page
├── app.js                    # Frontend logic
├── pyproject.toml            # Python dependencies
└── README.md                 # This file
```

## Setup

### Prerequisites

1. **Python 3.12+** with uv
2. **Google Gemini API Key**

### Installation

```bash
# Navigate to the skill directory
cd .agents/skills/financial_news

# Install dependencies
uv sync
```

### GitHub Secrets Configuration

1. Go to your repository Settings → Secrets and variables → Actions
2. Add a new secret named `gemini_key` with your Google Gemini API key

**⚠️ Security Warning**: If your API key has been exposed (e.g., in code, commits, or chat), immediately:
1. Delete the compromised key in Google Cloud Console
2. Generate a new API key
3. Update the GitHub secret

### Manual Testing

```bash
# Run tests
uv run pytest tests/ -v

# Run scraper (requires GEMINI_API_KEY)
GEMINI_API_KEY=your-key uv run python src/scraper.py

# Run full pipeline (requires GEMINI_API_KEY)
GEMINI_API_KEY=your-key uv run python src/pipeline.py
```

## GitHub Actions Workflow

The workflow runs daily at 5 AM UTC:

1. Checks out the repository
2. Installs Python dependencies with uv
3. Runs the news scraper
4. Processes articles with Gemini AI
5. Commits generated data to `/data` directory

### Manual Trigger

You can manually trigger the workflow:
- Go to Actions → Financial News Scraper → Run workflow

## Data Format

Each day's data is stored as `YYYY-MM-DD.json`:

```json
[
  {
    "title": "Article Title",
    "summary": "AI-generated summary (max 300 words)",
    "source": "Financial Times",
    "date": "2024-01-15T10:30:00Z",
    "url": "https://...",
    "sentiment": "positive",
    "industry": "Finance",
    "event_type": "Rate Changes",
    "is_paywalled": false
  }
]
```

## Frontend Usage

### Configuration

1. Click **Settings** (⚙️) button
2. Select preferred industries (minimum 1 required)
3. Select preferred event types
4. Click **Save**

### Feedback

- Click **👍** to upvote relevant articles
- Click **👎** to downvote irrelevant articles
- Feedback persists across sessions
- Future news is ranked based on feedback patterns

### Charts

- **Sentiment Trends**: Shows positive/negative/neutral distribution by industry
- **News Volume**: Shows article count by industry

## Troubleshooting

### No Data Showing

1. Check if GitHub Actions workflow has run successfully
2. Verify data files exist in `.agents/skills/financial_news/data/`
3. Check browser console for errors

### API Errors

1. Verify `gemini_key` secret is set correctly
2. Check API quota in Google Cloud Console
3. Review workflow logs for specific error messages

### Scraping Failures

1. Some articles may be paywalled (handled gracefully)
2. Rate limiting may cause delays
3. Check workflow logs for specific errors

## Development

### Adding New Sources

Edit `src/scraper.py` to add new RSS feeds or scrapers.

### Customizing AI Prompts

Edit `src/ai_service.py` to modify summarization or classification prompts.

### Extending Industries

Update the industry list in:
- `src/ai_service.py` (AI classification)
- `index.html` (config UI)
- `app.js` (filtering logic)

## License

MIT

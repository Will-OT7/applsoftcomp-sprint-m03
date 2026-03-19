# financial_news Skill

## Overview
This skill implements a personalized AI assistant that summarizes 7 days of financial news from Financial Times and AP News. The system runs daily via GitHub Actions at 5 AM UTC, scrapes articles, processes them with Google Gemini API for summarization and sentiment analysis, and displays results on a GitHub Pages-hosted dashboard.

## Tasks

### Task 1: GitHub Actions Workflow Setup
- Implemented: false
- Test Passed: false
- Goal: Create a GitHub Actions workflow that runs daily at 5 AM UTC to scrape, process, and commit financial news data
- Inputs: GitHub secrets (gemini_key), Python environment
- Outputs: Daily JSON data files committed to `/data` directory on main branch
- Specification 1: Workflow triggers at 5 AM UTC daily using `schedule` event
- Specification 2: Workflow uses Python 3.12 with uv for dependency management
- Specification 3: Workflow accesses `gemini_key` from repository secrets
- Specification 4: Workflow commits generated data to `/data` directory on main branch
- Specification 5: Workflow handles failures gracefully (logs error, continues next day)
- Specification 6: Workflow installs pymupdf and google-generativeai packages

### Task 2: News Scraper
- Implemented: false
- Test Passed: false
- Goal: Scrape financial news articles from Financial Times and AP News
- Inputs: URLs from Financial Times and AP News RSS feeds/sitemaps
- Outputs: Raw article data (title, full text, source, date, URL)
- Specification 1: Scrape Financial Times free articles only (handle paywall gracefully)
- Specification 2: Scrape AP News finance section
- Specification 3: Extract article title, full text content, source name, publish date, canonical URL
- Specification 4: Skip or mark paywalled articles that cannot be fully accessed
- Specification 5: Deduplicate articles by URL - prioritize first article found
- Specification 6: Target 1-2 articles per industry per day
- Specification 7: Fall back to historical data if daily target not met
- Specification 8: Respect robots.txt and rate limits (1 request per 2 seconds)

### Task 3: AI Summarization Service
- Implemented: false
- Test Passed: false
- Goal: Use Google Gemini API to summarize articles and analyze sentiment
- Inputs: Raw article text from scraper
- Outputs: Summary (max 300 words), sentiment label, industry classification, event type classification
- Specification 1: Generate summary with maximum 300 words
- Specification 2: Include direct excerpts/quotes from article where applicable
- Specification 3: Analyze sentiment and output simple label: positive, negative, or neutral
- Specification 4: Classify article into industry category using AI
- Specification 5: Classify event type: rate changes, political events, environmental events, or other
- Specification 6: Use Google Gemini API with api key from secrets
- Specification 7: Handle API rate limits and quota errors gracefully
- Specification 8: Cache API responses to avoid redundant calls on re-run

### Task 4: Data Pipeline
- Implemented: false
- Test Passed: false
- Goal: Process and store news data in 7-day rolling window format
- Inputs: Processed articles from Task 3
- Outputs: JSON files in `/data` directory, one per day
- Specification 1: Store data as JSON files named by date (e.g., `2024-01-15.json`)
- Specification 2: Maintain 7-day rolling window - prune data older than 7 days
- Specification 3: Each day's JSON contains array of article objects with all metadata
- Specification 4: Aggregate daily metrics for chart data (sentiment counts, volume counts)
- Specification 5: Include industry and event type mappings in each article object
- Specification 6: Validate JSON schema before commit
- Specification 7: Handle missing days gracefully (empty array or skip)

### Task 5: Frontend Dashboard
- Implemented: false
- Test Passed: false
- Goal: Create single-page dashboard displaying news summaries and charts
- Inputs: JSON data from `/data` directory, user configuration from localStorage
- Outputs: Rendered HTML page with bullet points and Chart.js visualizations
- Specification 1: Single dashboard page layout (index.html)
- Specification 2: Display news summaries as bullet points
- Specification 3: Dynamic bullet point count proportional to news volume
- Specification 4: Fewer selected industries = more items per industry allowed
- Specification 5: Chart.js line chart for sentiment trends per industry (7 days)
- Specification 6: Chart.js bar chart for news volume over time per industry (7 days)
- Specification 7: Responsive design for mobile and desktop
- Specification 8: Load data from `/data` directory JSON files
- Specification 9: Article titles include industry name in parentheses
- Specification 10: Articles are clickable links to original source URLs

### Task 6: Configuration System
- Implemented: false
- Test Passed: false
- Goal: Allow users to select preferred industries and event types
- Inputs: User selections via configuration modal
- Outputs: Configuration stored in localStorage, applied to news filtering
- Specification 1: Display configuration modal on first page visit
- Specification 2: Show list of industries: Technology, Finance, Healthcare, Energy, Retail, Manufacturing, Other
- Specification 3: Show list of event types: Rate Changes, Political Events, Environmental Events
- Specification 4: Require minimum 1 selection (industry or event type)
- Specification 5: Allow user to select all options if desired
- Specification 6: Configuration accessible/modifyable anytime via settings button
- Specification 7: Store configuration in localStorage
- Specification 8: Filter news display based on selected industries and event types

### Task 7: Feedback System
- Implemented: false
- Test Passed: false
- Goal: Allow users to provide thumbs up/down feedback on news items
- Inputs: User clicks on thumbs up/down buttons
- Outputs: Feedback stored in localStorage, used for client-side ranking
- Specification 1: Display thumbs up/down buttons on each news item
- Specification 2: Store feedback in localStorage with article ID and timestamp
- Specification 3: Persist feedback across browser sessions
- Specification 4: Use feedback history to re-rank future news items client-side
- Specification 5: Upvoted articles from similar industry/event type ranked higher
- Specification 6: Downvoted articles from similar industry/event type ranked lower
- Specification 7: Clear feedback history option in settings
- Specification 8: Visual indicator showing feedback state (filled/outlined icon)

### Task 8: Unit Tests
- Implemented: true
- Test Passed: true
- Goal: Write unit tests for scraper, AI service, and data pipeline
- Inputs: Mock data, mocked API responses
- Outputs: Test suite that validates core functionality
- Specification 1: Test scraper with mock HTML responses
- Specification 2: Test AI summarization with mocked Gemini API
- Specification 3: Test data pipeline with mock articles
- Specification 4: Test 7-day pruning logic
- Specification 5: Test deduplication logic
- Specification 6: Test JSON schema validation
- Specification 7: Tests runnable via `uv run pytest`
- Specification 8: Tests included in GitHub Actions workflow

### Task 9: Documentation
- Implemented: false
- Test Passed: false
- Goal: Provide setup and usage documentation
- Inputs: Technical implementation details
- Outputs: README.md and SKILL.md files
- Specification 1: README.md with project overview and architecture
- Specification 2: Setup instructions for local development
- Specification 3: GitHub Secrets configuration guide (gemini_key setup)
- Specification 4: API key security warning (regenerate if exposed)
- Specification 5: SKILL.md with agent instructions for maintenance
- Specification 6: Troubleshooting section for common issues

---

## Usage
Run this skill to implement the financial_news assistant:

```bash
# Run the skill to implement all tasks
opencode "Implement the financial_news skill"
```

## Testing
After implementation, verify using the test-skill:

```bash
# Run test-skill to validate all tasks
opencode "Run test-skill on financial_news"
```

## Security Notes
- API key must be stored in GitHub Secrets as `gemini_key`
- Never commit API keys to the repository
- If API key is exposed, regenerate immediately in Google Cloud Console
- Respect robots.txt and terms of service for scraped websites

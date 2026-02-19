# AI Job Source Agent

An automated pipeline that discovers company career pages and extracts open job position URLs from LinkedIn job search results. Given a LinkedIn job search URL, the agent scrapes company listings, finds each company's careers page using a 3-tier strategy, and extracts a direct link to an open position — outputting everything as structured JSON.

---

## How It Works

The pipeline follows five stages:

1. **LinkedIn Data Acquisition** — Fetches job listings from a LinkedIn search URL via the [Apify](https://apify.com) API, extracting company names and website URLs.
2. **Career Page Discovery (3-tier)** — For each company, finds the careers page:
   - **Tier 1** (free, ~80% success): Tests common URL paths (`/careers`, `/jobs`, etc.)
   - **Tier 2** (free, ~15% success): Scrapes the homepage with BeautifulSoup, scanning links and footer/nav for career keywords
   - **Tier 3** (paid, ~5% fallback): Asks Claude AI to infer the careers URL
3. **Position Extraction** — Uses Playwright (headless Chromium) to navigate the career page and extract the first job posting URL, handling JavaScript-rendered pages.
4. **Validation** — All URLs are structurally validated and checked for HTTP 200 responses.
5. **Output** — Results and execution statistics are saved to a timestamped JSON file.

---

## Project Structure

```
AI_JobSourceAgent/
├── pipeline.py           # Main entry point — orchestrates all components
├── config.py             # Configuration loaded from environment variables
├── models.py             # Data models: CompanyData, JobSourceResult, ExecutionStatistics
├── linkedin_fetcher.py   # LinkedIn data acquisition via Apify
├── career_finder.py      # 3-tier career page discovery strategy
├── position_extractor.py # Job posting URL extraction via Playwright
├── claude_fallback.py    # Claude AI fallback for Tier 3 discovery
├── url_validator.py      # URL normalization and HTTP validation
├── output_manager.py     # JSON output and statistics persistence
├── logger.py             # Centralized structured logger
└── requirements.txt      # Python dependencies
```

---

## Prerequisites

- **Python 3.9+**
- **Apify account** with an API token — used to scrape LinkedIn job listings
- **Anthropic API key** *(optional)* — only used as a last-resort fallback for ~5% of companies; the pipeline works without it

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd AI_JobSourceAgent
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright browsers

Playwright requires a one-time download of the Chromium browser binary:

```bash
playwright install chromium
```

> If you encounter system dependency errors on Linux, run:
> ```bash
> playwright install-deps chromium
> ```

### 5. Set environment variables

The agent requires API keys set as environment variables. **Do not hardcode keys in source files.**

```bash
export APIFY_TOKEN="your_apify_token_here"
export ANTHROPIC_API_KEY="your_anthropic_api_key_here"   # Optional
```

To make these persistent across terminal sessions, add them to your shell profile (`~/.zshrc`, `~/.bashrc`, etc.) or use a `.env` file with a tool like `direnv`.

#### Getting your Apify token

1. Sign up at [apify.com](https://apify.com)
2. Go to **Settings → Integrations** in the Apify console
3. Copy your **Personal API token**

The Apify actor used is `hMvNSpz3JnHgl5jkh` (LinkedIn Job Scraper). Ensure your Apify account has sufficient credits — estimated cost is ~$0.01 per listing, with a default budget cap of $25/month.

#### Getting your Anthropic API key (optional)

1. Sign up at [console.anthropic.com](https://console.anthropic.com)
2. Go to **API Keys** and create a new key
3. The agent caps Claude usage at 50 calls/month to stay within budget

### 6. Create the output directory

The pipeline writes results to `./output/` automatically, but you can create it manually:

```bash
mkdir -p output
```

---

## Usage

Run the pipeline from the project root with the virtual environment activated:

```bash
python pipeline.py --linkedin-url "<LinkedIn job search URL>" --max 50
```

### Arguments

| Argument | Required | Default | Description |
|---|---|---|---|
| `--linkedin-url` | Yes | — | A LinkedIn job search results URL |
| `--max` | No | `50` | Number of companies to process (range: 1–50) |

### Example

```bash
python pipeline.py \
  --linkedin-url "https://www.linkedin.com/jobs/search/?keywords=software+engineer&location=San+Francisco" \
  --max 30
```

### Output

On completion, two files are written to `./output/`:

- **`job_sources_YYYY-MM-DD.json`** — Results and statistics
- **`pipeline.log`** — Full execution log with timestamps

#### Output JSON schema

```json
{
  "results": [
    {
      "company_name": "Acme Corp",
      "career_page_url": "https://acmecorp.com/careers",
      "open_position_url": "https://acmecorp.com/careers/software-engineer-123",
      "timestamp": "2024-01-15T14:23:05.123456"
    }
  ],
  "statistics": {
    "total_processed": 30,
    "successful": 26,
    "failed": 4,
    "success_rate": "86.7%",
    "heuristic_success_rate": "83.3%",
    "tier1_success": 22,
    "tier2_success": 3,
    "tier3_success": 1,
    "claude_api_calls": 1,
    "linkedin_api_calls": 1,
    "total_processing_time": 187.4
  },
  "generated_at": "2024-01-15T14:25:12.000000"
}
```

---

## Configuration Reference

All runtime configuration is managed in `config.py` and loaded from environment variables. Key defaults:

| Setting | Default | Description |
|---|---|---|
| `APIFY_TOKEN` | *(required)* | Apify API token for LinkedIn scraping |
| `ANTHROPIC_API_KEY` | *(optional)* | Anthropic API key for Tier 3 fallback |
| `max_claude_calls` | `50` | Monthly cap on Claude API calls |
| `request_timeout` | `5s` | HTTP request timeout per URL check |
| `browser_timeout` | `15000ms` | Playwright page load timeout |
| `output_dir` | `./output` | Directory for JSON results and logs |

---

## Troubleshooting

**`Configuration validation failed (check APIFY_TOKEN)`**
The `APIFY_TOKEN` environment variable is missing or empty. Set it as described in Setup step 5.

**`No listings fetched from LinkedIn`**
The LinkedIn URL may be invalid, require authentication, or the Apify actor may have failed. Verify the URL works in a browser and that your Apify token is valid with sufficient credits.

**Playwright errors on first run**
Run `playwright install chromium` to download the required browser binary.

**Low success rate**
Some company websites block automated requests or use non-standard career page structures. The Tier 3 Claude fallback can improve coverage if an `ANTHROPIC_API_KEY` is provided.

---

## API Cost Estimates

| Component | Cost | Monthly Budget Cap |
|---|---|---|
| Apify (LinkedIn scraping) | ~$0.01/listing | ~$25 |
| Anthropic Claude (Tier 3 fallback) | ~$0.003/call | ~$20 (50 calls max) |
| Playwright + BeautifulSoup | Free | — |

For a typical run of 50 companies, the total cost is approximately **$0.50–$1.00**.

"""LinkedIn data acquisition module (SRS Section 6.1).

Per class diagram: LinkedInFetcher produces CompanyData (1..*).
Per SRS FR-1.1 through FR-1.4.
Dependencies: apify-client or requests.
API Budget: $20-25/month.
"""

from typing import Dict, List, Optional

from apify_client import ApifyClient

from config import Configuration
from logger import Logger
from models import CompanyData, ExecutionStatistics


class LinkedInFetcher:
    """Fetches job listings from LinkedIn via Apify API.

    Per class diagram:
      - Composition: owned by JobSourcePipeline (lifecycle bound)
      - Dependency: uses Configuration, logs to Logger
      - Association: produces CompanyData (1..*), updates ExecutionStatistics
    """

    def __init__(
        self,
        config: Configuration,
        logger: Logger,
        statistics: ExecutionStatistics,
    ) -> None:
        self.api_token: str = config.apify_token
        self.base_url: str = "https://api.apify.com/v2"
        self.max_items: int = 50  # FR-1.3 upper bound
        self.request_timeout: int = config.request_timeout
        self.api_calls_made: int = 0
        self.monthly_budget: float = 25.0  # NFR-2.1
        self._config = config
        self._logger = logger
        self._statistics = statistics

    def fetch_job_listings(
        self, linkedin_url: str, limit: int = 50
    ) -> List[Dict]:
        """FR-1.1: Fetch job listings from LinkedIn via third-party API.

        Args:
            linkedin_url: LinkedIn job search URL.
            limit: Max items to fetch (FR-1.3: 20-50).

        Returns:
            Raw API response items.
        """
        self._logger.info(f"Fetching up to {limit} listings from LinkedIn")
        try:
            raw = self._make_api_request(linkedin_url, {"maxItems": min(limit, self.max_items)})
            if not self.validate_api_response(raw):
                self._logger.error("Invalid API response from LinkedIn fetcher")
                return []
            self._track_api_cost(len(raw))
            self._statistics.linkedin_api_calls += 1
            return raw
        except Exception as e:
            self._logger.error("LinkedIn API failure", e)
            return []

    def extract_company_data(self, raw_response: List[Dict]) -> List[CompanyData]:
        """FR-1.2: Extract company name, company website URL.

        Per class diagram: produces CompanyData with multiplicity 1..*.
        """
        companies: List[CompanyData] = []
        for item in raw_response:
            company_name = item.get("companyName", "") or item.get("company", "")
            company_url = item.get("companyUrl", "") or item.get("companyLink", "")
            linkedin_job_url = item.get("jobUrl", "") or item.get("link", "")
            job_title = item.get("title", "") or item.get("jobTitle", "")

            if not company_name or not company_url:
                self._logger.warning(f"Skipping item with missing data: {item.get('title', 'unknown')}")
                continue

            # Normalize: extract root domain from LinkedIn company URL if needed
            if "linkedin.com" in company_url:
                website = item.get("companyWebsite", "") or item.get("website", "")
                if website:
                    company_url = website
                else:
                    self._logger.warning(f"No website URL for {company_name}, only LinkedIn profile")
                    continue

            company = CompanyData(
                company_name=company_name,
                company_url=company_url,
                linkedin_job_url=linkedin_job_url,
                job_title=job_title,
            )

            if company.validate_url():
                companies.append(company)
            else:
                self._logger.warning(f"Invalid URL for {company_name}: {company_url}")

        self._logger.info(f"Extracted {len(companies)} companies from API response")
        return companies

    def handle_rate_limit(self, response: Dict) -> bool:
        """FR-1.4: Handle API rate limits gracefully."""
        if isinstance(response, dict) and response.get("error", {}).get("type") == "rate-limit":
            self._logger.warning("LinkedIn API rate limit hit")
            return True
        return False

    def validate_api_response(self, response: object) -> bool:
        """Validate the API returned usable data."""
        if response is None:
            return False
        if isinstance(response, list):
            return len(response) > 0
        return False

    def _make_api_request(self, linkedin_url: str, params: Dict) -> List[Dict]:
        """Call Apify actor to scrape LinkedIn job listings."""
        client = ApifyClient(self.api_token)
        run_input = {
            "startUrls": [{"url": linkedin_url}],
            "maxItems": params.get("maxItems", self.max_items),
        }
        run = client.actor("hMvNSpz3JnHgl5jkh").call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        self.api_calls_made += 1
        return items

    def _track_api_cost(self, items_fetched: int) -> None:
        """Track estimated API cost against budget (NFR-2.1)."""
        estimated_cost = items_fetched * 0.01  # rough per-item estimate
        self._logger.info(f"Estimated API cost for {items_fetched} items: ${estimated_cost:.2f}")

"""Career page discovery module (SRS Section 6.2).

Per class diagram: CareerPageFinder with 3-tier strategy.
Per state machine diagram: Tier1 -> Tier2 -> Tier3 fallback chain.
Dependencies: requests, beautifulsoup4.
API Budget: $0 (Tiers 1 & 2 are free).
"""

from typing import List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from claude_fallback import ClaudeFallback
from config import Configuration
from logger import Logger
from models import ExecutionStatistics
from url_validator import URLValidator


class CareerPageFinder:
    """Discovers career pages using a 3-tier strategy.

    Per class diagram:
      - Composition: owned by JobSourcePipeline (lifecycle bound)
      - Dependency: uses Configuration, Logger, URLValidator
      - Association: fallback to ClaudeFallback (0..1), updates ExecutionStatistics

    Per state machine (Diagram 4):
      Tier 1 (80%): Direct path testing - FREE
      Tier 2 (15%): Homepage scraping with BeautifulSoup - FREE
      Tier 3 (5%):  Claude API fallback - PAID
    """

    def __init__(
        self,
        config: Configuration,
        logger: Logger,
        statistics: ExecutionStatistics,
        claude_fallback: Optional[ClaudeFallback] = None,
    ) -> None:
        self.common_paths: List[str] = list(config.career_paths)
        self.career_keywords: List[str] = list(config.career_keywords)
        self.request_timeout: int = config.request_timeout
        self.max_retries: int = 2
        self.tier1_success_count: int = 0
        self.tier2_success_count: int = 0
        self.tier3_success_count: int = 0
        self._logger = logger
        self._statistics = statistics
        self._claude_fallback = claude_fallback
        self._validator = URLValidator(timeout=config.request_timeout)
        self._headers = {"User-Agent": self._validator.user_agent}

    def find_career_page(self, company_url: str) -> Optional[str]:
        """Main entry: try Tier 1 -> Tier 2 -> Tier 3. Per sequence diagram.

        FR-2.5: Returns absolute URL only, or None.
        """
        company_url = self._validator.normalize(company_url)
        self._logger.info(f"Finding career page for {company_url}")

        # Tier 1: Direct paths (80% expected success)
        result = self.find_via_direct_paths(company_url)
        if result:
            self.tier1_success_count += 1
            self._statistics.increment_success(tier=1)
            self._logger.info(f"Tier 1 success: {result}")
            return result

        # Tier 2: Homepage scraping (15% expected success)
        result = self.scrape_homepage(company_url)
        if result:
            self.tier2_success_count += 1
            self._statistics.increment_success(tier=2)
            self._logger.info(f"Tier 2 success: {result}")
            return result

        # Tier 3: Claude API fallback (5% expected success)
        if self._claude_fallback:
            result = self._claude_fallback.find_career_page_ai(company_url)
            if result:
                self.tier3_success_count += 1
                self._statistics.increment_success(tier=3)
                self._logger.info(f"Tier 3 success: {result}")
                return result

        self._logger.warning(f"No career page found for {company_url}")
        return None

    def find_via_direct_paths(self, company_url: str) -> Optional[str]:
        """Tier 1 (FR-2.1): Test common career page paths.

        Per state machine: Testing -> Success (80%) or Failed (all paths exhausted).
        """
        for path in self.common_paths:
            test_url = company_url.rstrip("/") + path
            try:
                response = requests.head(
                    test_url,
                    timeout=self.request_timeout,
                    headers=self._headers,
                    allow_redirects=True,
                )
                if response.status_code == 200:
                    # Verify it's actually a career page, not a generic redirect
                    if self._is_valid_career_page(response.url, ""):
                        return response.url
            except requests.RequestException:
                continue
        return None

    def scrape_homepage(self, company_url: str) -> Optional[str]:
        """Tier 2 (FR-2.2): Scrape homepage for career links.

        Per state machine: Scraping -> ExtractingLinks -> MatchingKeywords.
        """
        try:
            response = requests.get(
                company_url,
                timeout=self.request_timeout,
                headers=self._headers,
                allow_redirects=True,
            )
            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            # Check footer/nav first (common location for career links)
            footer_result = self.check_footer_nav(soup)
            if footer_result:
                return self.make_absolute_url(company_url, footer_result)

            # Scan all links for career keywords (FR-2.3)
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                text = link.get_text(strip=True).lower()
                if self._matches_career_keyword(text, href):
                    absolute_url = self.make_absolute_url(company_url, href)
                    if self.validate_url(absolute_url):
                        return absolute_url

        except requests.RequestException as e:
            self._logger.error(f"Homepage scrape failed for {company_url}", e)

        return None

    def check_footer_nav(self, soup: BeautifulSoup) -> Optional[str]:
        """Check footer and nav elements for career links."""
        for container_tag in ["footer", "nav"]:
            for container in soup.find_all(container_tag):
                for link in container.find_all("a", href=True):
                    href = link.get("href", "")
                    text = link.get_text(strip=True).lower()
                    if self._matches_career_keyword(text, href):
                        return href
        return None

    def make_absolute_url(self, base_url: str, relative_url: str) -> str:
        """FR-2.5: Return absolute URLs only."""
        return urljoin(base_url, relative_url)

    def validate_url(self, url: str) -> bool:
        """Quick structural validation (no HTTP check)."""
        try:
            parsed = urlparse(url)
            return all([parsed.scheme, parsed.netloc])
        except Exception:
            return False

    def _matches_career_keyword(self, text: str, url: str) -> bool:
        """FR-2.3: Match against career keywords in link text or URL."""
        combined = (text + " " + url).lower()
        return any(keyword in combined for keyword in self.career_keywords)

    def _is_valid_career_page(self, url: str, content: str) -> bool:
        """Verify URL looks like a career page (not a generic redirect)."""
        url_lower = url.lower()
        return any(keyword in url_lower for keyword in self.career_keywords)

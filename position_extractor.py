"""Position extraction module (SRS Section 6.3).

Per class diagram: PositionExtractor with Playwright browser automation.
Per SRS FR-3.1 through FR-3.4.
Dependencies: playwright.
API Budget: $0.
"""

from typing import List, Optional
from urllib.parse import urljoin

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from config import Configuration
from logger import Logger
from url_validator import URLValidator


class PositionExtractor:
    """Extracts first job posting URL from career pages.

    Per class diagram:
      - Composition: owned by JobSourcePipeline (lifecycle bound)
      - Dependency: uses Configuration, Logger, URLValidator
      - Uses Playwright Browser interface (component diagram)

    Per SRS FR-3.1: Handle JavaScript rendering via Playwright.
    """

    # Common selectors for job listing links
    JOB_SELECTORS: List[str] = [
        'a[href*="job"]',
        'a[href*="position"]',
        'a[href*="opening"]',
        'a[href*="posting"]',
        'a[href*="apply"]',
        'a[href*="career"]',
        ".job-listing a",
        ".job-card a",
        ".careers-list a",
        ".opening a",
        '[class*="job"] a',
        '[class*="position"] a',
        '[class*="career"] a',
        '[data-job] a',
        'a[class*="job"]',
    ]

    def __init__(self, config: Configuration, logger: Logger) -> None:
        self.browser_timeout: int = config.browser_timeout  # FR-3.4: 15000ms
        self.page_load_timeout: int = config.browser_timeout
        self.job_selectors: List[str] = list(self.JOB_SELECTORS)
        self.headless: bool = True
        self.browser_context: Optional[BrowserContext] = None
        self._config = config
        self._logger = logger
        self._validator = URLValidator(timeout=config.request_timeout)
        self._browser: Optional[Browser] = None
        self._playwright = None

    def extract_first_position(self, career_page_url: str) -> Optional[str]:
        """FR-3.2: Extract first available job posting URL.

        Per sequence diagram: navigate_to_page -> find_job_links -> return first.
        FR-3.3: Return absolute URL only.
        FR-3.4: Timeout after 15 seconds.
        """
        self._logger.info(f"Extracting position from {career_page_url}")
        try:
            page = self.navigate_to_page(career_page_url)
            if page is None:
                return None

            job_links = self.find_job_links(page)
            page.close()

            if job_links:
                absolute_url = self.make_absolute_url(career_page_url, job_links[0])
                self._logger.info(f"Found position: {absolute_url}")
                return absolute_url

            self._logger.warning(f"No job links found on {career_page_url}")
            return None

        except Exception as e:
            self._logger.error(f"Position extraction failed for {career_page_url}", e)
            return None

    def navigate_to_page(self, url: str) -> Optional[Page]:
        """FR-3.1: Navigate to career page, handling JS rendering."""
        try:
            if self._browser is None:
                self._browser = self._initialize_browser()

            if self.browser_context is None:
                self.browser_context = self._browser.new_context(
                    user_agent=self._validator.user_agent
                )

            page = self.browser_context.new_page()
            page.goto(url, timeout=self.page_load_timeout, wait_until="domcontentloaded")
            self._wait_for_content(page)
            return page

        except Exception as e:
            self._logger.error(f"Navigation failed for {url}", e)
            return None

    def find_job_links(self, page: Page) -> List[str]:
        """Find job posting links on the page using selectors."""
        found_urls: List[str] = []

        for selector in self.job_selectors:
            try:
                elements = page.query_selector_all(selector)
                for element in elements:
                    url = self._extract_job_url(element)
                    if url and url not in found_urls:
                        found_urls.append(url)
                        if len(found_urls) >= 1:  # FR-3.2: first available
                            return found_urls
            except Exception:
                continue

        return found_urls

    def make_absolute_url(self, base_url: str, job_url: str) -> str:
        """FR-3.3: Return absolute URL only."""
        return urljoin(base_url, job_url)

    def _initialize_browser(self) -> Browser:
        """Launch Playwright Chromium browser (component diagram: Playwright Browser)."""
        self._playwright = sync_playwright().start()
        return self._playwright.chromium.launch(headless=self.headless)

    def _wait_for_content(self, page: Page) -> None:
        """Wait for dynamic content to load."""
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass  # Best-effort; page may already have content

    def _extract_job_url(self, element: object) -> Optional[str]:
        """Extract href from a link element."""
        try:
            href = element.get_attribute("href")
            if href and not href.startswith(("javascript:", "mailto:", "#")):
                return href
        except Exception:
            pass
        return None

    def close(self) -> None:
        """Cleanup browser resources."""
        if self.browser_context:
            self.browser_context.close()
            self.browser_context = None
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None

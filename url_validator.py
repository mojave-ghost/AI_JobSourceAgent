"""URL validation utility for AI Job Source Agent.

Per class diagram: used by CareerPageFinder and PositionExtractor via dependency.
Per SRS NFR-3.3: Validate URLs before returning (200 status check).
"""

from urllib.parse import urljoin, urlparse

import requests


class URLValidator:
    """Validates and normalizes URLs.

    Per class diagram: timeout, user_agent attributes.
    Dependencies: CareerPageFinder ..> URLValidator, PositionExtractor ..> URLValidator.
    """

    def __init__(self, timeout: int = 5) -> None:
        self.timeout: int = timeout
        self.user_agent: str = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

    def is_valid(self, url: str) -> bool:
        """Check that URL is well-formed and returns HTTP 200. Per NFR-3.3."""
        try:
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                return False
            status = self._check_status(url)
            return status == 200
        except Exception:
            return False

    def normalize(self, url: str) -> str:
        """Ensure URL has scheme and trailing slash normalization."""
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")

    def make_absolute(self, base: str, relative: str) -> str:
        """Convert relative URL to absolute. Per FR-2.5 and FR-3.3."""
        return urljoin(base, relative)

    def _check_status(self, url: str) -> int:
        """HTTP HEAD request to check URL status. Per NFR-1.3: 5s timeout."""
        try:
            response = requests.head(
                url,
                timeout=self.timeout,
                headers={"User-Agent": self.user_agent},
                allow_redirects=True,
            )
            return response.status_code
        except requests.RequestException:
            return 0

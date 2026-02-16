"""Claude AI fallback module (SRS Section 6.4).

Per class diagram: ClaudeFallback with monthly rate limiting.
Per state machine Tier 3: CheckingLimit -> CallingAPI -> ParsingResponse.
Dependencies: anthropic.
API Budget: $15-20/month, max 50 calls/month (NFR-2.2).
"""

from typing import Dict, Optional

import anthropic

from config import Configuration
from logger import Logger
from models import ExecutionStatistics


class ClaudeFallback:
    """AI-powered career page discovery as last resort.

    Per class diagram:
      - Composition: owned by JobSourcePipeline (lifecycle bound)
      - Dependency: uses Configuration, logs to Logger
      - Association: updates ExecutionStatistics
      - Used by CareerPageFinder via fallback dependency (0..1, 5% of cases)

    Per state machine (Diagram 4, Tier 3):
      CheckingLimit -> CallingAPI -> ParsingResponse -> Success/Failed
    """

    def __init__(
        self,
        config: Configuration,
        logger: Logger,
        statistics: ExecutionStatistics,
    ) -> None:
        self.api_key: str = config.anthropic_api_key
        self.model: str = "claude-sonnet-4-5-20250514"  # SRS: Sonnet 4.5
        self.max_tokens: int = 256
        self.calls_this_month: int = 0
        self.max_calls_per_month: int = config.max_claude_calls  # NFR-2.2: 50
        self.monthly_budget: float = 20.0
        self._logger = logger
        self._statistics = statistics
        self._client: Optional[anthropic.Anthropic] = None

    def find_career_page_ai(self, company_url: str) -> Optional[str]:
        """Tier 3: Use Claude to find career page URL.

        Per sequence diagram: check limit -> build prompt -> API call -> parse.
        """
        if not self.check_monthly_limit():
            self._logger.warning("Claude API monthly limit reached, skipping")
            return None

        if not self.api_key:
            self._logger.warning("No Anthropic API key configured, skipping Claude fallback")
            return None

        self._logger.info(f"Tier 3: Using Claude API for {company_url}")

        try:
            if self._client is None:
                self._client = anthropic.Anthropic(api_key=self.api_key)

            prompt = self._build_prompt(company_url)
            response = self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            self.increment_call_counter()
            return self._parse_claude_response(response)

        except Exception as e:
            self._logger.error(f"Claude API call failed for {company_url}", e)
            return None

    def check_monthly_limit(self) -> bool:
        """Per state machine: CheckingLimit -> CallingAPI or Failed."""
        return self.calls_this_month < self.max_calls_per_month

    def increment_call_counter(self) -> None:
        """Track calls against monthly limit and statistics."""
        self.calls_this_month += 1
        self._statistics.claude_api_calls += 1

    def _build_prompt(self, company_url: str) -> str:
        """Construct prompt for career page discovery."""
        return (
            f"What is the careers/jobs page URL for the company at {company_url}? "
            f"Return ONLY the full URL, nothing else. "
            f"If you don't know, return 'UNKNOWN'."
        )

    def _parse_claude_response(self, response: object) -> Optional[str]:
        """Extract URL from Claude response."""
        try:
            text = response.content[0].text.strip()
            if text.upper() == "UNKNOWN" or not text.startswith("http"):
                return None
            return text
        except (AttributeError, IndexError):
            return None

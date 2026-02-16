"""Configuration module for AI Job Source Agent (SRS Section 7)."""

import os
from typing import Any, List


class Configuration:
    """Centralized configuration loaded from environment variables and defaults.

    Per class diagram: owns career_paths, career_keywords, API keys, timeouts.
    Per SRS NFR-4.2: Environment variables for API keys.
    Per SRS NFR-4.3: Single configuration file for paths/patterns.
    """

    def __init__(self) -> None:
        # API keys (SRS Section 7 - env vars)
        self.apify_token: str = ""
        self.anthropic_api_key: str = ""

        # Career page patterns (SRS Section 7, FR-2.1, FR-2.3)
        self.career_paths: List[str] = [
            "/careers",
            "/jobs",
            "/about/careers",
            "/about/jobs",
            "/join-us",
            "/work-with-us",
            "/career",
            "/job-openings",
            "/open-positions",
            "/opportunities",
            "/en/careers",
            "/us/careers",
            "/company/careers",
        ]
        self.career_keywords: List[str] = [
            "careers",
            "jobs",
            "join us",
            "opportunities",
            "work with us",
            "open positions",
            "job openings",
            "we're hiring",
            "hiring",
            "come work",
            "employment",
        ]

        # Limits (SRS Section 7, NFR-2.2)
        self.max_claude_calls: int = 50
        self.request_timeout: int = 5       # NFR-1.3: 5s per HTTP request
        self.browser_timeout: int = 15000   # FR-3.4: 15s per page

        # Output (SRS Section 7)
        self.output_dir: str = "./output"

        self.load_from_env()

    def load_from_env(self) -> None:
        """Load API keys from environment variables (NFR-4.2)."""
        self.apify_token = os.environ.get("APIFY_TOKEN", "")
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    def validate(self) -> bool:
        """Validate that required configuration is present."""
        if not self.apify_token:
            return False
        return True

    def get(self, key: str) -> Any:
        """Generic getter for configuration values."""
        return getattr(self, key, None)

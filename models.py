"""Data models for AI Job Source Agent.

Per class diagram: CompanyData, JobSourceResult, ExecutionStatistics.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional
from urllib.parse import urlparse


@dataclass
class CompanyData:
    """Data extracted from LinkedIn API for a single company.

    Per class diagram: produced by LinkedInFetcher, processed by Pipeline.
    Multiplicity: 1..* produced, 20..50 processed per run (FR-1.3).
    """

    company_name: str
    company_url: str
    linkedin_job_url: str = ""
    job_title: str = ""

    def to_dict(self) -> Dict:
        return {
            "company_name": self.company_name,
            "company_url": self.company_url,
            "linkedin_job_url": self.linkedin_job_url,
            "job_title": self.job_title,
        }

    def validate_url(self) -> bool:
        try:
            result = urlparse(self.company_url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False


@dataclass
class JobSourceResult:
    """Result for a single company after full pipeline processing.

    Per class diagram: created by Pipeline, contained by OutputManager.
    Multiplicity: 0..* (0 if all fail, up to 50 if all succeed).
    Per SRS FR-4.1 schema: company_name, career_page_url, open_position_url, timestamp.
    """

    company_name: str
    career_page_url: str
    open_position_url: str
    timestamp: datetime = field(default_factory=datetime.now)
    source_tier: int = 0
    processing_time: float = 0.0

    def to_dict(self) -> Dict:
        """Per SRS FR-4.1 output schema."""
        return {
            "company_name": self.company_name,
            "career_page_url": self.career_page_url,
            "open_position_url": self.open_position_url,
            "timestamp": self.timestamp.isoformat(),
        }

    def validate(self) -> bool:
        return bool(self.company_name and self.career_page_url)

    def __repr__(self) -> str:
        return (
            f"JobSourceResult(company={self.company_name!r}, "
            f"career={self.career_page_url!r}, "
            f"position={self.open_position_url!r})"
        )


@dataclass
class ExecutionStatistics:
    """Tracks pipeline execution metrics.

    Per class diagram: owned by Pipeline and OutputManager.
    Per SRS FR-4.2: success rate, API calls used.
    """

    total_processed: int = 0
    successful: int = 0
    failed: int = 0
    tier1_success: int = 0
    tier2_success: int = 0
    tier3_success: int = 0
    claude_api_calls: int = 0
    linkedin_api_calls: int = 0
    total_processing_time: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def increment_success(self, tier: int) -> None:
        self.successful += 1
        self.total_processed += 1
        if tier == 1:
            self.tier1_success += 1
        elif tier == 2:
            self.tier2_success += 1
        elif tier == 3:
            self.tier3_success += 1

    def increment_failure(self) -> None:
        self.failed += 1
        self.total_processed += 1

    def calculate_success_rate(self) -> float:
        if self.total_processed == 0:
            return 0.0
        return (self.successful / self.total_processed) * 100

    def calculate_heuristic_success_rate(self) -> float:
        """Success rate for free tiers only (Tier 1 + 2). Per NFR-2.3: >80%."""
        heuristic_total = self.tier1_success + self.tier2_success
        if self.total_processed == 0:
            return 0.0
        return (heuristic_total / self.total_processed) * 100

    def to_dict(self) -> Dict:
        return {
            "total_processed": self.total_processed,
            "successful": self.successful,
            "failed": self.failed,
            "success_rate": f"{self.calculate_success_rate():.1f}%",
            "heuristic_success_rate": f"{self.calculate_heuristic_success_rate():.1f}%",
            "tier1_success": self.tier1_success,
            "tier2_success": self.tier2_success,
            "tier3_success": self.tier3_success,
            "claude_api_calls": self.claude_api_calls,
            "linkedin_api_calls": self.linkedin_api_calls,
            "total_processing_time": round(self.total_processing_time, 2),
        }

    def get_summary(self) -> str:
        return (
            f"Processed: {self.total_processed} | "
            f"Success: {self.successful} ({self.calculate_success_rate():.1f}%) | "
            f"Failed: {self.failed} | "
            f"Tier1: {self.tier1_success} | Tier2: {self.tier2_success} | "
            f"Tier3: {self.tier3_success} | "
            f"Claude calls: {self.claude_api_calls} | "
            f"Time: {self.total_processing_time:.1f}s"
        )

"""Pipeline orchestrator module (SRS Section 6.5).

Per class diagram: JobSourcePipeline owns all 8 components via composition.
Per sequence diagram (Diagram 3): coordinates full execution flow.
Per component diagram (Diagram 5): main entry point.

Input: LinkedIn URL, max_companies
Output: JSON file + console stats
Dependencies: All modules + json
"""

import argparse
import time
from datetime import datetime
from typing import Optional

from career_finder import CareerPageFinder
from claude_fallback import ClaudeFallback
from config import Configuration
from linkedin_fetcher import LinkedInFetcher
from logger import Logger
from models import CompanyData, ExecutionStatistics, JobSourceResult
from output_manager import OutputManager
from position_extractor import PositionExtractor


class JobSourcePipeline:
    """Main pipeline orchestrator — facade over all subsystems.

    Per class diagram (Diagram 1):
      Composition (owns, lifecycle bound):
        - config: Configuration (1)
        - linkedin_fetcher: LinkedInFetcher (1)
        - career_finder: CareerPageFinder (1)
        - claude_fallback: ClaudeFallback (1)
        - position_extractor: PositionExtractor (1)
        - output_manager: OutputManager (1)
        - statistics: ExecutionStatistics (1)
        - logger: Logger (1)

    Per relationship diagram (Diagram 2):
      - Processes 20..50 CompanyData (FR-1.3)
      - Creates 0..* JobSourceResult

    Design patterns (from UML docs):
      - Facade: single entry point for User
      - Strategy: CareerPageFinder uses tiered strategy
      - Singleton: shared Configuration and Logger
    """

    def __init__(self) -> None:
        # All attributes initialized in _initialize_components
        self.config: Optional[Configuration] = None
        self.linkedin_fetcher: Optional[LinkedInFetcher] = None
        self.career_finder: Optional[CareerPageFinder] = None
        self.claude_fallback: Optional[ClaudeFallback] = None
        self.position_extractor: Optional[PositionExtractor] = None
        self.output_manager: Optional[OutputManager] = None
        self.statistics: Optional[ExecutionStatistics] = None
        self.logger: Optional[Logger] = None
        self._initialize_components()

    def run(self, linkedin_url: str, max_companies: int = 50) -> None:
        """Main entry point — full pipeline execution.

        Per sequence diagram (Diagram 3):
          1. Validate inputs
          2. Record start time
          3. Fetch LinkedIn listings
          4. Extract company data
          5. Loop: process each company
          6. Save results to JSON
          7. Print summary

        Args:
            linkedin_url: LinkedIn job search URL (single URL per run).
            max_companies: FR-1.3: 20-50 companies per execution.
        """
        if not self._validate_inputs(linkedin_url, max_companies):
            return

        self.logger.info("Starting pipeline")
        self.statistics.start_time = datetime.now()

        # Step 1: LinkedIn Data Acquisition (per sequence diagram)
        raw_listings = self.linkedin_fetcher.fetch_job_listings(linkedin_url, limit=max_companies)
        if not raw_listings:
            self.logger.error("No listings fetched from LinkedIn, aborting")
            return

        companies = self.linkedin_fetcher.extract_company_data(raw_listings)
        if not companies:
            self.logger.error("No valid companies extracted, aborting")
            return

        # Enforce FR-1.3 bounds
        companies = companies[:max_companies]
        total = len(companies)
        self.logger.info(f"Processing {total} companies")

        # Step 2: Process each company (per sequence diagram loop)
        for i, company in enumerate(companies, 1):
            self._print_progress(i, total)
            result = self.process_single_company(company)
            if result:
                self.output_manager.add_result(result)

        # Step 3: Finalize (per sequence diagram)
        self.statistics.end_time = datetime.now()
        self.statistics.total_processing_time = (
            self.statistics.end_time - self.statistics.start_time
        ).total_seconds()

        # Save output (FR-4.1, FR-4.2, FR-4.3)
        filepath = self.output_manager.save_to_json()

        # Console summary
        self.logger.info("Pipeline completed")
        print(f"\n{'='*60}")
        print(self.statistics.get_summary())
        print(f"Output: {filepath}")
        print(f"{'='*60}")

        # Cleanup browser resources
        self.position_extractor.close()

        # Persist logs
        self.logger.save_logs()

    def process_single_company(self, company: CompanyData) -> Optional[JobSourceResult]:
        """Process one company through career discovery + position extraction.

        Per sequence diagram inner loop:
          1. find_career_page(company_url)
          2. If found: extract_first_position(career_url)
          3. If position found: create JobSourceResult
          4. On failure: increment_failure, log

        NFR-3.2: Continue execution on individual company failures.
        """
        start = time.time()
        self.logger.info(f"Processing: {company.company_name} ({company.company_url})")

        try:
            # Career page discovery (3-tier strategy)
            career_url = self.career_finder.find_career_page(company.company_url)

            if not career_url:
                self.statistics.increment_failure()
                self.logger.warning(f"No career page found for {company.company_name}")
                return None

            # Position extraction
            position_url = self.position_extractor.extract_first_position(career_url)

            if not position_url:
                self.statistics.increment_failure()
                self.logger.warning(f"No positions found for {company.company_name}")
                return None

            # Build result (FR-4.1 schema)
            processing_time = time.time() - start
            result = JobSourceResult(
                company_name=company.company_name,
                career_page_url=career_url,
                open_position_url=position_url,
                timestamp=datetime.now(),
                source_tier=self._determine_tier(),
                processing_time=processing_time,
            )

            self.logger.info(f"Success: {company.company_name}")
            return result

        except Exception as e:
            self.handle_error(e, company)
            return None

    def handle_error(self, error: Exception, company: CompanyData) -> None:
        """NFR-3.2: Log error, continue to next company."""
        self.statistics.increment_failure()
        self.logger.error(
            f"Error processing {company.company_name}: {company.company_url}",
            error,
        )

    def _initialize_components(self) -> None:
        """Create all owned components (composition relationships).

        Per relationship constraints:
          1. Configuration must be initialized before any component.
          2. Logger must be available before any logging occurs.
          3. Statistics shared across components.
        """
        # Infrastructure first (temporal constraint 1 & 2)
        self.config = Configuration()
        self.logger = Logger(log_file="output/pipeline.log")
        self.statistics = ExecutionStatistics()

        # Core components (all receive config, logger, statistics)
        self.claude_fallback = ClaudeFallback(
            config=self.config,
            logger=self.logger,
            statistics=self.statistics,
        )
        self.linkedin_fetcher = LinkedInFetcher(
            config=self.config,
            logger=self.logger,
            statistics=self.statistics,
        )
        self.career_finder = CareerPageFinder(
            config=self.config,
            logger=self.logger,
            statistics=self.statistics,
            claude_fallback=self.claude_fallback,
        )
        self.position_extractor = PositionExtractor(
            config=self.config,
            logger=self.logger,
        )
        self.output_manager = OutputManager(
            config=self.config,
            logger=self.logger,
            statistics=self.statistics,
        )

    def _validate_inputs(self, linkedin_url: str, max_companies: int) -> bool:
        """Validate pipeline inputs before execution."""
        if not linkedin_url:
            self.logger.error("LinkedIn URL is required")
            return False
        if not linkedin_url.startswith("http"):
            self.logger.error(f"Invalid LinkedIn URL: {linkedin_url}")
            return False
        if max_companies < 1 or max_companies > 50:
            self.logger.warning(f"max_companies {max_companies} out of range, clamping to 1-50")
            max_companies = max(1, min(50, max_companies))
        if not self.config.validate():
            self.logger.error("Configuration validation failed (check APIFY_TOKEN)")
            return False
        return True

    def _print_progress(self, current: int, total: int) -> None:
        """Display processing progress."""
        percent = (current / total) * 100
        print(f"  [{current}/{total}] ({percent:.0f}%)", end="\r")

    def _determine_tier(self) -> int:
        """Determine which tier succeeded based on latest statistics delta."""
        # The career_finder already incremented the correct tier in statistics;
        # infer from the most recently incremented counter.
        stats = self.statistics
        tier_counts = [
            (1, stats.tier1_success),
            (2, stats.tier2_success),
            (3, stats.tier3_success),
        ]
        return max(tier_counts, key=lambda x: x[1])[0]


# ─── CLI entry point (SRS Section 13) ───────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI Job Source Agent - Extract career pages from LinkedIn job listings"
    )
    parser.add_argument(
        "--linkedin-url",
        required=True,
        help="LinkedIn job search URL",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=50,
        help="Maximum companies to process (default: 50, range: 1-50)",
    )
    args = parser.parse_args()

    pipeline = JobSourcePipeline()
    pipeline.run(linkedin_url=args.linkedin_url, max_companies=args.max)


if __name__ == "__main__":
    main()

"""Output management module for AI Job Source Agent.

Per class diagram: OutputManager contains JobSourceResult (0..*) and ExecutionStatistics (1).
Per SRS FR-4.1 through FR-4.3.
"""

import json
import os
from datetime import datetime
from typing import Dict, List

from config import Configuration
from logger import Logger
from models import ExecutionStatistics, JobSourceResult


class OutputManager:
    """Manages result collection and JSON file output.

    Per class diagram:
      - Composition: owned by JobSourcePipeline (lifecycle bound)
      - Composition: contains JobSourceResult (0..*), ExecutionStatistics (1)
      - Dependency: uses Configuration, logs to Logger

    Per SRS:
      FR-4.1: JSON schema with company_name, career_page_url, open_position_url, timestamp.
      FR-4.2: Include execution statistics.
      FR-4.3: Filename format job_sources_YYYY-MM-DD.json.
    """

    def __init__(
        self,
        config: Configuration,
        logger: Logger,
        statistics: ExecutionStatistics,
    ) -> None:
        self.output_dir: str = config.output_dir
        self.filename_template: str = "job_sources_{date}.json"
        self.results: List[JobSourceResult] = []
        self.statistics: ExecutionStatistics = statistics
        self._logger = logger
        self._ensure_output_dir()

    def add_result(self, result: JobSourceResult) -> None:
        """Add a successful result to the collection."""
        self.results.append(result)

    def save_to_json(self, filename: str = "") -> str:
        """FR-4.1/FR-4.2: Save results + statistics to JSON file.

        Per sequence diagram: generate_filename -> _format_output -> save.
        Returns the filepath of the saved file.
        """
        if not filename:
            filename = self.generate_filename()

        filepath = os.path.join(self.output_dir, filename)
        output = self._format_output()

        with open(filepath, "w") as f:
            json.dump(output, f, indent=2, default=str)

        self._logger.info(f"Saved {len(self.results)} results to {filepath}")
        return filepath

    def generate_filename(self) -> str:
        """FR-4.3: Filename format job_sources_YYYY-MM-DD.json."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.filename_template.format(date=date_str)

    def _format_output(self) -> Dict:
        """Structure output with results array and statistics (FR-4.1 + FR-4.2)."""
        return {
            "results": [r.to_dict() for r in self.results],
            "statistics": self.statistics.to_dict(),
            "generated_at": datetime.now().isoformat(),
        }

    def _ensure_output_dir(self) -> None:
        """Create output directory if it doesn't exist."""
        os.makedirs(self.output_dir, exist_ok=True)

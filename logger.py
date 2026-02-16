"""Logger module for AI Job Source Agent.

Per class diagram: depended on by all components via dependency relationship.
Per SRS NFR-3.1: Log all errors with timestamps.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class Logger:
    """Centralized logger with file persistence.

    Per class diagram: log_file, log_level, logs attributes.
    Singleton pattern: shared instance across all components.
    """

    def __init__(self, log_file: str = "pipeline.log", log_level: str = "INFO") -> None:
        self.log_file: str = log_file
        self.log_level: str = log_level
        self.logs: List[Dict] = []

    def info(self, message: str) -> None:
        self._log("INFO", message)

    def error(self, message: str, exception: Optional[Exception] = None) -> None:
        entry_message = message
        if exception:
            entry_message = f"{message} | {type(exception).__name__}: {exception}"
        self._log("ERROR", entry_message)

    def warning(self, message: str) -> None:
        self._log("WARNING", message)

    def save_logs(self) -> None:
        """Persist logs to file."""
        os.makedirs(os.path.dirname(self.log_file) if os.path.dirname(self.log_file) else ".", exist_ok=True)
        with open(self.log_file, "w") as f:
            json.dump(self.logs, f, indent=2, default=str)

    def _log(self, level: str, message: str) -> None:
        """NFR-3.1: All entries include timestamp."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
        }
        self.logs.append(entry)
        # Also print to console for immediate feedback
        print(f"[{entry['timestamp']}] {level}: {message}")

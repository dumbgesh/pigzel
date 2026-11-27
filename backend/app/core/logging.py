"""Centralized logging configuration for Pigzel."""

import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    """Configure root application logging with a clean, consistent format."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
        force=True,
    )

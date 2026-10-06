# Kalakriti/Backend/app/utils/logger.py

import sys

from loguru import logger

# Remove default handler to prevent duplicate output
logger.remove()

SENSITIVE_KEYS = {"api_key", "token", "password", "secret", "authorization"}


def _redact(record: dict) -> None:
    """Mask sensitive values in log record extras before they reach the sink."""
    extra = record.get("extra", {})
    for key in extra:
        if any(s in key.lower() for s in SENSITIVE_KEYS):
            extra[key] = "***REDACTED***"


def setup_logger(environment: str = "development") -> None:
    """Configure Loguru sinks based on environment. Call once in main.py."""

    _redact_filter = lambda record: (_redact(record), True)[1]  # noqa: E731

    if environment == "production":
        # Structured JSON for log aggregation (Sentry, CloudWatch, etc.)
        logger.add(
            sys.stdout,
            format="{message}",
            serialize=True,
            filter=_redact_filter,
            level="INFO",
        )
        logger.add(
            "logs/kalakriti_{time:YYYY-MM-DD}.log",
            rotation="10 MB",
            retention="7 days",
            serialize=True,
            filter=_redact_filter,
            level="INFO",
        )
    else:
        # Human-readable colored output for local development
        logger.add(
            sys.stderr,
            format=(
                "<green>{time:HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            filter=_redact_filter,
            level="DEBUG",
            colorize=True,
        )

    logger.info("Logger initialized for environment: {}", environment)
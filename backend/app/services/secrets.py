import logging
import sys
from backend.app.config import Settings, get_settings

logger = logging.getLogger(__name__)


def validate_secrets() -> Settings:
    """Validates that all mandatory secrets injected by 1Password Connect exist

    and are non-empty. Exits immediately if any required secret is missing.
    """
    try:
        settings = get_settings()
    except Exception as exc:
        logger.critical("CRITICAL: Failed to load application settings from 1Password Connect: %s", exc)
        sys.exit(1)

    if not settings.auth_secret_token or not settings.auth_secret_token.strip():
        logger.critical("CRITICAL: AUTH_SECRET_TOKEN is unset or empty! No hardcoded fallbacks permitted.")
        sys.exit(1)

    logger.info("Successfully validated 1Password Connect secret injection.")
    return settings

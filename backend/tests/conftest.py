import os

import pytest

from backend.app.config import get_settings

# Inject mock secret for test runs so validation passes
os.environ["AUTH_SECRET_TOKEN"] = "test-token-xyz-12345"
os.environ["APP_ENV"] = "test"
os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["LOCATIONS_FILE"] = "config/locations.yaml"


@pytest.fixture(autouse=True)
def clean_settings():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()

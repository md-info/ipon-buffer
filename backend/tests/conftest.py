"""Shared synthetic setup."""

import pytest
from app.config import load_config
from app.sandbox.personas import golden_fixture


@pytest.fixture
def config():
    return load_config()


@pytest.fixture
def golden():
    return golden_fixture()

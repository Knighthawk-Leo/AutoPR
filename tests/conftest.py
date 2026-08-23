import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# main.py mounts ./static and configures ./templates by *relative* path at
# import time, so the working directory must be the project root before the
# import happens -- not later inside a fixture.
os.chdir(ROOT)

from main import app  # noqa: E402


@pytest.fixture(scope="session")
def css_text() -> str:
    return (ROOT / "static" / "style.css").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def template_text() -> str:
    return (ROOT / "templates" / "index.html").read_text(encoding="utf-8")


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client

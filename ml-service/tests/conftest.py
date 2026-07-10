import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# A tiny, publicly-hosted random-weight checkpoint sharing M2M100's exact
# architecture/tokenizer classes — verifies the real request/tokenize/
# generate/decode/confidence pipeline without downloading the ~1.6GB
# production checkpoint. Its actual translations are meaningless (random
# weights); only the plumbing is under test here.
os.environ.setdefault("MODEL_NAME", "valhalla/m2m100_tiny_random")

from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    return TestClient(app)

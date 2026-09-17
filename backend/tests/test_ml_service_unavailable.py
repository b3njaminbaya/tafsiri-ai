from app.main import app
from app.ml_client import MLServiceError, get_ml_client

from .conftest import _fake_ml
from .helpers import auth_headers, register_and_login


class _BrokenMLClient:
    def translate(self, *args, **kwargs):
        raise MLServiceError("ml-service unreachable: connection refused")


def test_translate_returns_503_when_ml_service_unreachable(client):
    token = register_and_login(client, "broken_ml_user@example.com")
    app.dependency_overrides[get_ml_client] = lambda: _BrokenMLClient()
    try:
        resp = client.post(
            "/api/v1/translate/",
            json={"text": "hi", "target_lang": "es"},
            headers=auth_headers(token),
        )
        assert resp.status_code == 503
    finally:
        # Restore the shared fake so later tests in the session aren't affected.
        app.dependency_overrides[get_ml_client] = lambda: _fake_ml


class _BadInputMLClient:
    """Simulates ml-service rejecting the request itself (e.g. an
    unsupported language or an ambiguous auto-detect) — a 4xx client-input
    problem, not an outage, and shouldn't be reported as one.
    """

    async def translate(self, *args, **kwargs):
        raise MLServiceError("Unsupported target language: xx", status_code=400)


def test_translate_passes_through_ml_service_4xx_instead_of_503(client):
    token = register_and_login(client, "badinput_ml_user@example.com")
    app.dependency_overrides[get_ml_client] = lambda: _BadInputMLClient()
    try:
        resp = client.post(
            "/api/v1/translate/",
            json={"text": "hi", "target_lang": "xx"},
            headers=auth_headers(token),
        )
        assert resp.status_code == 400
    finally:
        app.dependency_overrides[get_ml_client] = lambda: _fake_ml

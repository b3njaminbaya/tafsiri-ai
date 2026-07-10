from app.main import app
from app.ml_client import MLServiceError, get_ml_client

from .conftest import FakeMLClient
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
        # Restore the fake so later tests in the session aren't affected.
        app.dependency_overrides[get_ml_client] = lambda: FakeMLClient()

from app.models import Translation

from .conftest import run_db
from .helpers import auth_headers, register_and_login


def _create_translation(user_id: int, confidence: float, text="hello", output="hola") -> int:
    async def _impl(db):
        t = Translation(
            user_id=user_id,
            source_lang="en",
            target_lang="es",
            domain=None,
            input_text=text,
            output_text=output,
            confidence=confidence,
        )
        db.add(t)
        await db.commit()
        return t.id

    return run_db(_impl)


def _promote_to_translator(client, promote_actor_to_admin, email: str) -> tuple[str, int]:
    admin_token = promote_actor_to_admin(f"admin_for_{email}")
    translator_token = register_and_login(client, email)
    me = client.get("/api/v1/auth/me", headers=auth_headers(translator_token)).json()
    resp = client.patch(
        f"/api/v1/admin/users/{me['id']}",
        json={"role_name": "translator"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200
    return translator_token, me["id"]


def test_regular_user_cannot_access_review_queue(client):
    token = register_and_login(client, "regular_reviewer@example.com")
    resp = client.get("/api/v1/review/queue", headers=auth_headers(token))
    assert resp.status_code == 403


def test_translator_sees_only_low_confidence_uncorrected_translations(client, promote_actor_to_admin):
    translator_token, user_id = _promote_to_translator(client, promote_actor_to_admin, "reviewer@example.com")

    low_id = _create_translation(user_id, confidence=0.2)
    _create_translation(user_id, confidence=0.95)

    resp = client.get("/api/v1/review/queue", headers=auth_headers(translator_token))
    assert resp.status_code == 200
    body = resp.json()
    ids = [t["id"] for t in body]
    assert low_id in ids
    assert all(t["confidence"] < 0.6 for t in body)


def test_submit_correction_removes_translation_from_queue(client, promote_actor_to_admin):
    translator_token, user_id = _promote_to_translator(client, promote_actor_to_admin, "reviewer2@example.com")
    low_id = _create_translation(user_id, confidence=0.1)

    correct = client.post(
        f"/api/v1/review/{low_id}/correct",
        json={"corrected_text": "hola mundo", "note": "fixed greeting"},
        headers=auth_headers(translator_token),
    )
    assert correct.status_code == 200
    body = correct.json()
    assert body["corrected_text"] == "hola mundo"
    assert body["translation_id"] == low_id

    queue = client.get("/api/v1/review/queue", headers=auth_headers(translator_token))
    assert low_id not in [t["id"] for t in queue.json()]


def test_correction_requires_reviewer_role(client):
    token = register_and_login(client, "notreviewer@example.com")
    me = client.get("/api/v1/auth/me", headers=auth_headers(token)).json()
    low_id = _create_translation(me["id"], confidence=0.1)

    resp = client.post(
        f"/api/v1/review/{low_id}/correct",
        json={"corrected_text": "x"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 403


def test_correction_on_missing_translation_returns_404(client, promote_actor_to_admin):
    translator_token, _ = _promote_to_translator(client, promote_actor_to_admin, "reviewer3@example.com")
    resp = client.post(
        "/api/v1/review/999999/correct",
        json={"corrected_text": "x"},
        headers=auth_headers(translator_token),
    )
    assert resp.status_code == 404

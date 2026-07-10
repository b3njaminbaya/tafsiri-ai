def test_login_is_rate_limited_after_too_many_attempts(client):
    for _ in range(5):
        resp = client.post(
            "/api/v1/auth/login",
            data={"username": "nouser@example.com", "password": "wrong"},
        )
        assert resp.status_code == 401

    blocked = client.post(
        "/api/v1/auth/login",
        data={"username": "nouser@example.com", "password": "wrong"},
    )
    assert blocked.status_code == 429

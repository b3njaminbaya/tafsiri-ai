import io

from .helpers import auth_headers, register_and_login


def _upload_dataset(client, token, name="Corpus"):
    data = {"name": name, "source_lang": "en", "target_lang": "es"}
    files = {"file": ("c.tsv", io.BytesIO(b"a\tb\n"), "text/tab-separated-values")}
    return client.post("/api/v1/datasets/", data=data, files=files, headers=auth_headers(token))


def test_community_stats_is_public(client):
    resp = client.get("/api/v1/community/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert "total_datasets" in body
    assert "top_dataset_contributors" in body


def test_community_stats_reflects_real_activity(client):
    token = register_and_login(client, "contributor_alice@example.com")
    _upload_dataset(client, token, name="Alice's Corpus")
    _upload_dataset(client, token, name="Alice's Second Corpus")

    resp = client.get("/api/v1/community/stats")
    body = resp.json()
    assert body["total_datasets"] >= 2

    top = {c["handle"]: c["count"] for c in body["top_dataset_contributors"]}
    assert top.get("contributor_alice", 0) >= 2


def test_community_stats_handle_hides_email_domain(client):
    token = register_and_login(client, "private_person@some-provider.example")
    _upload_dataset(client, token, name="Private Corpus")

    resp = client.get("/api/v1/community/stats")
    body = resp.json()
    handles = [c["handle"] for c in body["top_dataset_contributors"]]
    assert "private_person" in handles
    assert not any("@" in h or "some-provider" in h for h in handles)

import io

from .helpers import auth_headers, register_and_login


def _upload(client, token, filename="corpus.tsv", content=b"hello\thola\n", **fields):
    data = {
        "name": "Test Corpus",
        "description": "A tiny test parallel corpus",
        "source_lang": "en",
        "target_lang": "es",
        "domain": "general",
        **fields,
    }
    files = {"file": (filename, io.BytesIO(content), "text/tab-separated-values")}
    return client.post(
        "/api/v1/datasets/",
        data=data,
        files=files,
        headers=auth_headers(token),
    )


def test_upload_and_list_dataset(client):
    token = register_and_login(client, "dataset_uploader@example.com")
    upload = _upload(client, token)
    assert upload.status_code == 200
    body = upload.json()
    assert body["name"] == "Test Corpus"
    assert body["size_bytes"] == len(b"hello\thola\n")

    listing = client.get("/api/v1/datasets/")
    assert listing.status_code == 200
    assert any(d["id"] == body["id"] for d in listing.json())


def test_upload_requires_auth(client):
    files = {"file": ("corpus.tsv", io.BytesIO(b"a\tb\n"), "text/tab-separated-values")}
    resp = client.post(
        "/api/v1/datasets/",
        data={"name": "No Auth"},
        files=files,
    )
    assert resp.status_code == 401


def test_upload_rejects_empty_file(client):
    token = register_and_login(client, "empty_uploader@example.com")
    resp = _upload(client, token, content=b"")
    assert resp.status_code == 400


def test_upload_rejects_oversized_file(client, monkeypatch):
    import app.core.config as config_module

    monkeypatch.setattr(config_module.settings, "max_dataset_upload_bytes", 10)
    token = register_and_login(client, "oversized_uploader@example.com")
    resp = _upload(client, token, content=b"way more than ten bytes of content")
    assert resp.status_code == 413


def test_download_returns_presigned_url(client):
    token = register_and_login(client, "downloader@example.com")
    upload = _upload(client, token)
    dataset_id = upload.json()["id"]

    resp = client.get(f"/api/v1/datasets/{dataset_id}/download")
    assert resp.status_code == 200
    body = resp.json()
    assert body["url"].startswith("http://fake-s3.local/")
    assert body["expires_in_seconds"] == 3600


def test_download_missing_dataset_returns_404(client):
    resp = client.get("/api/v1/datasets/999999/download")
    assert resp.status_code == 404

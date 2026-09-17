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


def test_list_datasets_filters_by_language_pair(client):
    token = register_and_login(client, "dataset_filter_uploader@example.com")
    en_ki = _upload(
        client, token, filename="en_ki.tsv", source_lang="en", target_lang="ki", content=b"hi\tniatia\n"
    )
    en_es = _upload(client, token, filename="en_es.tsv", source_lang="en", target_lang="es")
    assert en_ki.status_code == 200 and en_es.status_code == 200

    filtered = client.get("/api/v1/datasets/", params={"source_lang": "en", "target_lang": "ki"})
    assert filtered.status_code == 200
    ids = {d["id"] for d in filtered.json()}
    assert en_ki.json()["id"] in ids
    assert en_es.json()["id"] not in ids


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


def test_upload_rejects_disallowed_extension(client):
    token = register_and_login(client, "bad_extension_uploader@example.com")
    resp = _upload(client, token, filename="corpus.exe", content=b"not a dataset")
    assert resp.status_code == 400
    assert "extension" in resp.json()["detail"].lower()


def test_upload_rejects_filename_with_no_extension(client):
    token = register_and_login(client, "no_extension_uploader@example.com")
    resp = _upload(client, token, filename="corpus", content=b"hello\thola\n")
    assert resp.status_code == 400


def test_upload_accepts_allowed_extensions(client):
    token = register_and_login(client, "allowed_extension_uploader@example.com")
    for filename in ("corpus.csv", "corpus.json", "corpus.jsonl", "corpus.tmx", "corpus.xliff"):
        resp = _upload(client, token, filename=filename, content=b"a\tb\n")
        assert resp.status_code == 200, f"{filename} should be accepted"


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

    resp = client.get(f"/api/v1/datasets/{dataset_id}/download", headers=auth_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["url"].startswith("http://fake-s3.local/")
    assert body["expires_in_seconds"] == 3600


def test_download_requires_auth(client):
    token = register_and_login(client, "downloader_noauth@example.com")
    upload = _upload(client, token)
    dataset_id = upload.json()["id"]

    # TestClient persists cookies across requests on the same client instance
    # (the login above left the auth cookie in its jar) — clear it so this
    # request is genuinely unauthenticated, not just header-less.
    client.cookies.clear()
    resp = client.get(f"/api/v1/datasets/{dataset_id}/download")
    assert resp.status_code == 401


def test_download_missing_dataset_returns_404(client):
    token = register_and_login(client, "downloader2@example.com")
    resp = client.get("/api/v1/datasets/999999/download", headers=auth_headers(token))
    assert resp.status_code == 404


def test_upload_rejects_binary_content_disguised_with_allowed_extension(client):
    token = register_and_login(client, "binary_uploader@example.com")
    resp = _upload(client, token, filename="corpus.csv", content=b"\xff\xd8\xff\xe0not really text")
    assert resp.status_code == 400

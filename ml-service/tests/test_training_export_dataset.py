import json

import pytest

from training.export_dataset import ExportError, _auth_header, export


def test_auth_header_picks_bearer_for_long_token():
    assert _auth_header("x" * 200) == {"Authorization": f"Bearer {'x' * 200}"}


def test_auth_header_picks_api_key_for_short_token():
    assert _auth_header("short-api-key") == {"X-API-Key": "short-api-key"}


def test_auth_header_empty_for_no_token():
    assert _auth_header(None) == {}


class _FakeBackend:
    """Fakes the two HTTP calls export_dataset.py makes: listing datasets
    and resolving a download URL — real presigned-URL fetching is a
    separate get_bytes call, faked independently, the same seam the app's
    own backend tests use for its S3 client.
    """

    def __init__(self, datasets, files):
        self.datasets = datasets
        self.files = files  # {dataset_id: bytes}
        self.requested_urls = []

    def get_json(self, url, headers):
        self.requested_urls.append(url)
        if "/download" in url:
            dataset_id = int(url.rsplit("/", 2)[-2])
            return {"url": f"presigned://{dataset_id}", "expires_in_seconds": 3600}
        return self.datasets

    def get_bytes(self, url, headers=None):
        dataset_id = int(url.replace("presigned://", ""))
        return self.files[dataset_id]


def test_export_writes_files_and_manifest(tmp_path):
    backend = _FakeBackend(
        datasets=[
            {"id": 1, "name": "kikuyu proverbs.tsv", "source_lang": "en", "target_lang": "ki"},
            {"id": 2, "name": "kikuyu news", "source_lang": "en", "target_lang": "ki"},
        ],
        files={1: b"hello\tniatia\n", 2: b"world\tthi\n"},
    )

    manifest = export(
        api_base="http://fake-backend.local/api/v1",
        token="some-api-key",
        source_lang="en",
        target_lang="ki",
        out_dir=tmp_path,
        get_json=backend.get_json,
        get_bytes=backend.get_bytes,
    )

    assert manifest["source_lang"] == "en"
    assert manifest["target_lang"] == "ki"
    assert len(manifest["datasets"]) == 2

    file1 = tmp_path / "1-kikuyu_proverbs.tsv"
    file2 = tmp_path / "2-kikuyu_news.txt"  # no extension in name -> .txt fallback
    assert file1.read_bytes() == b"hello\tniatia\n"
    assert file2.read_bytes() == b"world\tthi\n"
    assert (tmp_path / "manifest.json").exists()
    assert json.loads((tmp_path / "manifest.json").read_text()) == manifest


def test_export_raises_when_no_datasets_match(tmp_path):
    backend = _FakeBackend(datasets=[], files={})
    with pytest.raises(ExportError):
        export(
            "http://fake-backend.local/api/v1",
            "token",
            "en",
            "ki",
            tmp_path,
            get_json=backend.get_json,
            get_bytes=backend.get_bytes,
        )


def test_export_request_includes_language_filter_query_params(tmp_path):
    backend = _FakeBackend(datasets=[], files={})
    with pytest.raises(ExportError):
        export(
            "http://fake-backend.local/api/v1",
            "token",
            "en",
            "ki",
            tmp_path,
            get_json=backend.get_json,
            get_bytes=backend.get_bytes,
        )
    assert "source_lang=en" in backend.requested_urls[0]
    assert "target_lang=ki" in backend.requested_urls[0]

"""Stage 1 of the training pipeline: pull every dataset uploaded for a given
language pair (via the Datasets page / POST /api/v1/datasets/) down to local
files, ready for prepare_data.py.

Talks to the real backend over HTTP (stdlib urllib — no new HTTP client
dependency for what's a handful of GET requests) rather than reaching into
Postgres/MinIO directly, so this can run from any machine with network
access to a deployed backend, using the same auth as any other API client.

Usage:
    python -m training.export_dataset \\
        --api-base http://localhost:8000/api/v1 \\
        --token "$BEARER_TOKEN_OR_API_KEY" \\
        --source-lang en --target-lang ki \\
        --out-dir ./pipeline-data/en-ki/raw
"""
import argparse
import json
import urllib.request
from pathlib import Path
from typing import Callable, List, Optional
from urllib.parse import urlencode


class ExportError(Exception):
    pass


def _auth_header(token: Optional[str]) -> dict:
    if not token:
        return {}
    # Accept either a JWT bearer token or a raw API key — the backend's own
    # get_current_user_or_api_key dependency (deps.py) already treats
    # "Authorization: Bearer <token>" and "X-API-Key: <key>" as equally
    # valid, so this mirrors that rather than picking one.
    if len(token) > 100:  # JWTs are long; API keys (token_urlsafe(32)) are ~43 chars
        return {"Authorization": f"Bearer {token}"}
    return {"X-API-Key": token}


def http_get_json(url: str, headers: dict) -> dict:
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def http_get_bytes(url: str, headers: Optional[dict] = None) -> bytes:
    request = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def list_matching_datasets(
    api_base: str, source_lang: str, target_lang: str, headers: dict, get_json: Callable = http_get_json
) -> List[dict]:
    query = urlencode({"source_lang": source_lang, "target_lang": target_lang})
    return get_json(f"{api_base}/datasets/?{query}", headers)


def download_dataset_file(
    api_base: str,
    dataset: dict,
    headers: dict,
    get_json: Callable = http_get_json,
    get_bytes: Callable = http_get_bytes,
) -> bytes:
    download_info = get_json(f"{api_base}/datasets/{dataset['id']}/download", headers)
    # The presigned URL is already fully authorized (that's the point of a
    # presigned URL) — it doesn't take the API's own auth headers, and
    # sending them would be harmless but pointless.
    return get_bytes(download_info["url"])


def export(
    api_base: str,
    token: Optional[str],
    source_lang: str,
    target_lang: str,
    out_dir: Path,
    get_json: Callable = http_get_json,
    get_bytes: Callable = http_get_bytes,
) -> dict:
    headers = _auth_header(token)
    datasets = list_matching_datasets(api_base, source_lang, target_lang, headers, get_json)
    if not datasets:
        raise ExportError(
            f"No datasets found for {source_lang}->{target_lang}. Upload some via the "
            "Datasets page first — see training/README.md."
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for dataset in datasets:
        content = download_dataset_file(api_base, dataset, headers, get_json, get_bytes)
        # storage_key isn't in the public API response (see schemas.DatasetRead)
        # so reconstruct a safe local filename from the dataset's own name/id
        # instead, preserving whatever extension its original upload had if
        # the name carries one, else falling back to .txt (prepare_data.py's
        # tab-delimited fallback parser handles that reasonably).
        safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in dataset["name"])
        extension = Path(safe_name).suffix or ".txt"
        filename = f"{dataset['id']}-{Path(safe_name).stem}{extension}"
        (out_dir / filename).write_bytes(content)
        saved.append({"id": dataset["id"], "name": dataset["name"], "file": filename, "bytes": len(content)})

    manifest = {
        "source_lang": source_lang,
        "target_lang": target_lang,
        "datasets": saved,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-base", required=True, help="e.g. http://localhost:8000/api/v1")
    parser.add_argument("--token", default=None, help="Bearer JWT or X-API-Key value")
    parser.add_argument("--source-lang", required=True)
    parser.add_argument("--target-lang", required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    manifest = export(args.api_base, args.token, args.source_lang, args.target_lang, args.out_dir)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

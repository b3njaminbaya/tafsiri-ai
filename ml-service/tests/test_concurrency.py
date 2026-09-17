import threading
import time

from app import main as ml_main


def test_inference_lock_serializes_critical_section():
    """Regression test for the tokenizer race condition: _tokenizer.src_lang
    is shared, mutable module state, and setting it then reading it back via
    _tokenizer(texts, ...) is two separate steps. Before _inference_lock,
    FastAPI's thread-pool execution of sync `def` endpoints meant a second
    request's `_tokenizer.src_lang = X` could land between another request's
    set and read, silently encoding that request under the wrong source
    language. This can't be verified by inspecting translations from the
    tiny random-weight test checkpoint (its output is gibberish regardless of
    input), so this verifies the actual mechanism directly: a thread holding
    _inference_lock genuinely blocks a second thread from entering the same
    critical section until the first releases it.
    """
    events = []

    def holder():
        with ml_main._inference_lock:
            events.append("holder-acquired")
            time.sleep(0.3)
            events.append("holder-released")

    t1 = threading.Thread(target=holder)
    t1.start()
    time.sleep(0.05)  # let t1 acquire the lock first

    def contender():
        with ml_main._inference_lock:
            events.append("contender-acquired")

    t2 = threading.Thread(target=contender)
    t2.start()
    t1.join(timeout=5)
    t2.join(timeout=5)

    assert events == ["holder-acquired", "holder-released", "contender-acquired"]


def test_concurrent_translate_requests_all_succeed(client):
    """Live smoke test: many concurrent /translate calls with different
    source languages complete successfully and each response is paired with
    its own request (no crashes, no cross-request mixups at the HTTP layer).
    """
    results = {}
    errors = []

    def _make_request(key: str, source_lang: str, text: str):
        try:
            resp = client.post(
                "/translate",
                json={"text": text, "source_lang": source_lang, "target_lang": "en"},
            )
            results[key] = (resp.status_code, resp.json().get("source_lang"))
        except Exception as exc:  # pragma: no cover
            errors.append(exc)

    threads = [
        threading.Thread(
            target=_make_request,
            args=(i, "sw" if i % 2 == 0 else "so", "habari" if i % 2 == 0 else "salaan"),
        )
        for i in range(20)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)

    assert not errors, f"requests raised exceptions: {errors}"
    assert len(results) == 20
    for i, (status_code, reported_source_lang) in results.items():
        assert status_code == 200
        assert reported_source_lang == ("sw" if i % 2 == 0 else "so")

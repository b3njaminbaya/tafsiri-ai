"""Parsers for the parallel-corpus formats the app accepts on upload (see
backend/app/api/v1/routes/datasets.py:ALLOWED_DATASET_EXTENSIONS). Each parser
takes raw file bytes and returns a flat list of (source_text, target_text)
pairs — nothing here judges quality; that's prepare_data.py's job.
"""
import csv
import io
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class SentencePair:
    source: str
    target: str


class UnsupportedFormatError(Exception):
    pass


def _lang_matches(xml_lang: Optional[str], code: str) -> bool:
    """TMX/XLIFF language attributes are often region-tagged (en-US, sw-KE);
    match on the primary subtag rather than requiring an exact string match.
    """
    if not xml_lang:
        return False
    return xml_lang.split("-")[0].lower() == code.lower()


def _parse_delimited(text: str, delimiter: str) -> List[SentencePair]:
    pairs = []
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    for row in reader:
        if len(row) < 2:
            continue
        source, target = row[0], row[1]
        pairs.append(SentencePair(source=source, target=target))
    return pairs


def _parse_tsv(text: str) -> List[SentencePair]:
    return _parse_delimited(text, "\t")


def _parse_csv(text: str) -> List[SentencePair]:
    return _parse_delimited(text, ",")


def _parse_txt(text: str) -> List[SentencePair]:
    # No single standard for .txt — this project's convention (matching what
    # upload_dataset's own extension allowlist implies) is tab-delimited,
    # same as .tsv. A pipe-delimited fallback is tried if no line has a tab,
    # since that's the next most common plain-text parallel-corpus
    # convention in the wild.
    if "\t" in text:
        return _parse_tsv(text)
    return _parse_delimited(text, "|")


def _extract_json_pair(obj: dict, source_lang: str, target_lang: str) -> Optional[SentencePair]:
    # Support a few common key conventions rather than forcing one schema:
    # {"source": ..., "target": ...}, {"source_text": ..., "target_text": ...},
    # or keyed directly by language code, e.g. {"en": ..., "ki": ...}.
    if "source" in obj and "target" in obj:
        return SentencePair(source=str(obj["source"]), target=str(obj["target"]))
    if "source_text" in obj and "target_text" in obj:
        return SentencePair(source=str(obj["source_text"]), target=str(obj["target_text"]))
    if source_lang in obj and target_lang in obj:
        return SentencePair(source=str(obj[source_lang]), target=str(obj[target_lang]))
    return None


def _parse_json(text: str, source_lang: str, target_lang: str) -> List[SentencePair]:
    data = json.loads(text)
    if not isinstance(data, list):
        raise UnsupportedFormatError("Expected a JSON array of objects at the top level")
    pairs = []
    for obj in data:
        if not isinstance(obj, dict):
            continue
        pair = _extract_json_pair(obj, source_lang, target_lang)
        if pair:
            pairs.append(pair)
    return pairs


def _parse_jsonl(text: str, source_lang: str, target_lang: str) -> List[SentencePair]:
    pairs = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        if not isinstance(obj, dict):
            continue
        pair = _extract_json_pair(obj, source_lang, target_lang)
        if pair:
            pairs.append(pair)
    return pairs


def _parse_tmx(text: str, source_lang: str, target_lang: str) -> List[SentencePair]:
    """TMX (Translation Memory eXchange): <tu> translation units, each
    holding one <tuv xml:lang="..."><seg>text</seg></tuv> per language.
    """
    ns = {"xml": "http://www.w3.org/XML/1998/namespace"}
    root = ET.fromstring(text)
    pairs = []
    for tu in root.iter("tu"):
        source_text = None
        target_text = None
        for tuv in tu.findall("tuv"):
            lang = tuv.get("{http://www.w3.org/XML/1998/namespace}lang") or tuv.get("lang")
            seg = tuv.find("seg")
            if seg is None or seg.text is None:
                continue
            if _lang_matches(lang, source_lang):
                source_text = seg.text
            elif _lang_matches(lang, target_lang):
                target_text = seg.text
        if source_text and target_text:
            pairs.append(SentencePair(source=source_text, target=target_text))
    return pairs


def _parse_xliff(text: str, source_lang: str, target_lang: str) -> List[SentencePair]:
    """XLIFF 1.2: <file source-language=".." target-language="..">, each
    containing <trans-unit><source>..</source><target>..</target></trans-unit>.
    Namespace-agnostic (strips the {namespace} prefix ElementTree adds)
    since XLIFF producers vary on whether/which namespace they declare.
    """
    root = ET.fromstring(text)

    def local_name(tag: str) -> str:
        return tag.split("}")[-1] if "}" in tag else tag

    pairs = []
    for elem in root.iter():
        if local_name(elem.tag) != "trans-unit":
            continue
        source_el = next((c for c in elem if local_name(c.tag) == "source"), None)
        target_el = next((c for c in elem if local_name(c.tag) == "target"), None)
        if source_el is not None and target_el is not None and source_el.text and target_el.text:
            pairs.append(SentencePair(source=source_el.text, target=target_el.text))
    return pairs


def parse_parallel_file(
    content: bytes, filename: str, source_lang: str, target_lang: str
) -> List[SentencePair]:
    text = content.decode("utf-8")
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension == "tsv":
        return _parse_tsv(text)
    if extension == "csv":
        return _parse_csv(text)
    if extension == "txt":
        return _parse_txt(text)
    if extension == "json":
        return _parse_json(text, source_lang, target_lang)
    if extension == "jsonl":
        return _parse_jsonl(text, source_lang, target_lang)
    if extension == "tmx":
        return _parse_tmx(text, source_lang, target_lang)
    if extension in ("xliff", "xlf"):
        return _parse_xliff(text, source_lang, target_lang)

    raise UnsupportedFormatError(f"No parser for .{extension} files")

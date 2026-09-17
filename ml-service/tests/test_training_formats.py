from training.formats import SentencePair, UnsupportedFormatError, parse_parallel_file


def test_parse_tsv():
    content = b"hello\tniatia\nworld\tthi\n"
    pairs = parse_parallel_file(content, "corpus.tsv", "en", "ki")
    assert pairs == [SentencePair("hello", "niatia"), SentencePair("world", "thi")]


def test_parse_csv():
    content = b"hello,niatia\nworld,thi\n"
    pairs = parse_parallel_file(content, "corpus.csv", "en", "ki")
    assert pairs == [SentencePair("hello", "niatia"), SentencePair("world", "thi")]


def test_parse_txt_tab_delimited():
    content = b"hello\tniatia\n"
    pairs = parse_parallel_file(content, "corpus.txt", "en", "ki")
    assert pairs == [SentencePair("hello", "niatia")]


def test_parse_txt_pipe_delimited_fallback():
    content = b"hello|niatia\nworld|thi\n"
    pairs = parse_parallel_file(content, "corpus.txt", "en", "ki")
    assert pairs == [SentencePair("hello", "niatia"), SentencePair("world", "thi")]


def test_parse_json_source_target_keys():
    content = b'[{"source": "hello", "target": "niatia"}, {"source": "world", "target": "thi"}]'
    pairs = parse_parallel_file(content, "corpus.json", "en", "ki")
    assert pairs == [SentencePair("hello", "niatia"), SentencePair("world", "thi")]


def test_parse_json_language_code_keys():
    content = b'[{"en": "hello", "ki": "niatia"}]'
    pairs = parse_parallel_file(content, "corpus.json", "en", "ki")
    assert pairs == [SentencePair("hello", "niatia")]


def test_parse_jsonl():
    content = b'{"source": "hello", "target": "niatia"}\n{"source": "world", "target": "thi"}\n'
    pairs = parse_parallel_file(content, "corpus.jsonl", "en", "ki")
    assert pairs == [SentencePair("hello", "niatia"), SentencePair("world", "thi")]


def test_parse_jsonl_skips_blank_lines():
    content = b'{"source": "hello", "target": "niatia"}\n\n   \n'
    pairs = parse_parallel_file(content, "corpus.jsonl", "en", "ki")
    assert pairs == [SentencePair("hello", "niatia")]


TMX_SAMPLE = b"""<?xml version="1.0" encoding="UTF-8"?>
<tmx version="1.4">
  <body>
    <tu>
      <tuv xml:lang="en"><seg>hello</seg></tuv>
      <tuv xml:lang="ki"><seg>niatia</seg></tuv>
    </tu>
    <tu>
      <tuv xml:lang="en"><seg>world</seg></tuv>
      <tuv xml:lang="ki"><seg>thi</seg></tuv>
    </tu>
  </body>
</tmx>
"""


def test_parse_tmx():
    pairs = parse_parallel_file(TMX_SAMPLE, "corpus.tmx", "en", "ki")
    assert pairs == [SentencePair("hello", "niatia"), SentencePair("world", "thi")]


def test_parse_tmx_matches_region_tagged_codes():
    content = TMX_SAMPLE.replace(b'xml:lang="en"', b'xml:lang="en-US"').replace(
        b'xml:lang="ki"', b'xml:lang="ki-KE"'
    )
    pairs = parse_parallel_file(content, "corpus.tmx", "en", "ki")
    assert pairs == [SentencePair("hello", "niatia"), SentencePair("world", "thi")]


XLIFF_SAMPLE = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">
  <file source-language="en" target-language="ki" datatype="plaintext">
    <body>
      <trans-unit id="1">
        <source>hello</source>
        <target>niatia</target>
      </trans-unit>
      <trans-unit id="2">
        <source>world</source>
        <target>thi</target>
      </trans-unit>
    </body>
  </file>
</xliff>
"""


def test_parse_xliff():
    pairs = parse_parallel_file(XLIFF_SAMPLE, "corpus.xliff", "en", "ki")
    assert pairs == [SentencePair("hello", "niatia"), SentencePair("world", "thi")]


def test_parse_xlf_extension_uses_xliff_parser():
    pairs = parse_parallel_file(XLIFF_SAMPLE, "corpus.xlf", "en", "ki")
    assert pairs == [SentencePair("hello", "niatia"), SentencePair("world", "thi")]


def test_unsupported_extension_raises():
    try:
        parse_parallel_file(b"whatever", "corpus.pdf", "en", "ki")
        assert False, "expected UnsupportedFormatError"
    except UnsupportedFormatError:
        pass


def test_delimited_row_with_only_one_column_is_skipped():
    content = b"hello\tniatia\njustonecolumn\nworld\tthi\n"
    pairs = parse_parallel_file(content, "corpus.tsv", "en", "ki")
    assert pairs == [SentencePair("hello", "niatia"), SentencePair("world", "thi")]

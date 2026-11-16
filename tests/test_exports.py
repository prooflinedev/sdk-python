from __future__ import annotations

import csv
import io
from concurrent.futures import ThreadPoolExecutor
from itertools import product

import httpx
import pytest

from proofline import ProoflineError
from proofline._transport import MAX_RESPONSE_BYTES
from proofline.exports import decode_export


def response(text: str) -> httpx.Response:
    return httpx.Response(
        200,
        content=text.encode(),
        headers={
            "Content-Type": "text/csv",
            "X-Proofline-Export-Version": "1",
            "X-Proofline-Export-Settled-Until": "2026-11-16T00:00:00Z",
        },
    )


@pytest.mark.parametrize("size", [131_072, 131_073, 150_000])
def test_large_csv_field_preserved(size: int) -> None:
    claim = 'é, "quoted"\r\n' + "x" * size
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(["dataset_version", "claim"])
    writer.writerow(["1", claim])
    text = stream.getvalue()
    page = decode_export(response(text), "csv")
    assert page.rows == [{"dataset_version": "1", "claim": claim}]
    assert page.text == text


@pytest.mark.parametrize("extra", [0, 1])
def test_csv_response_byte_bound(extra: int) -> None:
    prefix = "dataset_version,claim\n1,"
    text = prefix + "x" * (MAX_RESPONSE_BYTES - len(prefix) + extra)
    if extra:
        with pytest.raises(ProoflineError, match="HTTP 200") as caught:
            decode_export(response(text), "csv")
        assert caught.value.type == "urn:proofline:sdk:invalid-response"
    else:
        assert len(decode_export(response(text), "csv").rows[0]["claim"]) == (
            MAX_RESPONSE_BYTES - len(prefix)
        )


@pytest.mark.parametrize(
    "text",
    [
        "",
        'dataset_version,claim\n1,"unfinished',
        'dataset_version,claim\n1,"closed"junk',
        "dataset_version,claim,claim\n1,a,b",
        "dataset_version,claim\n1",
        "dataset_version,claim\n1,a,b",
        "dataset_version,claim\n\n",
    ],
)
def test_invalid_csv_retains_typed_error(text: str) -> None:
    with pytest.raises(ProoflineError) as caught:
        decode_export(response(text), "csv")
    assert caught.value.type == "urn:proofline:sdk:invalid-response"
    assert caught.value.status == 200


def test_csv_parser_matches_standard_dialect() -> None:
    from proofline._csv import parse_csv

    # Exhaust short combinations to exercise transitions, including malformed quoting.
    samples = ("".join(chars) for length in range(6) for chars in product('a,"\r\n', repeat=length))
    for text in samples:
        try:
            expected = list(csv.reader(io.StringIO(text, newline=""), strict=True))
        except csv.Error:
            with pytest.raises(ValueError):
                parse_csv(text)
        else:
            assert parse_csv(text) == expected, repr(text)
    for text in ['a,"é,\r\n""quote""",\r\n', "a,b\r1,2", 'a,""', "a,b\n"]:
        assert parse_csv(text) == list(csv.reader(io.StringIO(text, newline=""), strict=True))


def test_concurrent_decoding_preserves_global_csv_limit() -> None:
    before = csv.field_size_limit()

    def decode(index: int) -> str:
        if index % 2:
            with pytest.raises(ProoflineError):
                decode_export(response('dataset_version,claim\n1,"unfinished'), "csv")
        else:
            assert decode_export(response("dataset_version,claim\n1," + "x" * 150_000), "csv")
        return str(csv.field_size_limit())

    with ThreadPoolExecutor(max_workers=4) as pool:
        assert set(pool.map(decode, range(12))) == {str(before)}
    assert csv.field_size_limit() == before

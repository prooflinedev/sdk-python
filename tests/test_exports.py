from __future__ import annotations

import csv
import io

import httpx
import pytest

from proofline import ExportWriter
from proofline.exports import ExportFormat, ExportPage, decode_export


def export(text: str, format: ExportFormat = "csv") -> ExportPage:
    return decode_export(
        httpx.Response(
            200,
            content=text.encode(),
            headers={
                "content-type": "text/csv" if format == "csv" else "application/x-ndjson",
                "x-proofline-export-version": "1",
                "x-proofline-export-settled-until": "2026-10-25T00:00:00Z",
            },
        ),
        format,
    )


def test_csv_pages_keep_one_header_and_original_multiline_content() -> None:
    stream = io.StringIO(newline="")
    writer = ExportWriter(stream)
    header = 'dataset_version,"claim\ntext"\r\n'
    first = header + '1,"comma, quote "" and\nnewline"\r\n'
    second = header + '1,"second"\r\n'
    writer.write_page(export(first))
    writer.write_page(export(header))
    writer.write_page(export(second))
    assert stream.getvalue() == first + '1,"second"\r\n'
    assert len(list(csv.reader(io.StringIO(stream.getvalue())))) == 3
    assert not stream.closed


def test_ndjson_pages_without_final_newline_remain_separate_records() -> None:
    stream = io.StringIO()
    writer = ExportWriter(stream)
    writer.write_page(export('{"dataset_version":1}', "ndjson"))
    writer.write_page(export("", "ndjson"))
    writer.write_page(export('{"dataset_version":1}\n', "ndjson"))
    assert stream.getvalue() == '{"dataset_version":1}\n{"dataset_version":1}\n'


@pytest.mark.parametrize("header", ["claim,dataset_version\n", "dataset_version,other\n"])
def test_changed_schema_is_refused_before_writing(header: str) -> None:
    stream = io.StringIO()
    writer = ExportWriter(stream)
    writer.write_page(export("dataset_version,claim\n"))
    with pytest.raises(ValueError, match="same columns"):
        writer.write_page(export(header))
    assert stream.getvalue() == "dataset_version,claim\n"
    writer.write_page(export("dataset_version,claim\n1,ok\n"))
    assert stream.getvalue().endswith("1,ok\n")


def test_changed_format_is_refused_before_writing() -> None:
    stream = io.StringIO()
    writer = ExportWriter(stream)
    writer.write_page(export("", "ndjson"))
    with pytest.raises(ValueError, match="same format"):
        writer.write_page(export("dataset_version,claim\n"))
    assert stream.getvalue() == ""


def test_csv_pages_without_final_newline_remain_separate_records() -> None:
    stream = io.StringIO(newline="")
    writer = ExportWriter(stream)
    writer.write_page(export("dataset_version,claim\n1,first"))
    writer.write_page(export("dataset_version,claim\n1,second"))
    assert stream.getvalue() == "dataset_version,claim\n1,first\n1,second\n"


def test_ndjson_lone_carriage_return_gets_line_feed() -> None:
    stream = io.StringIO(newline="")
    writer = ExportWriter(stream)
    writer.write_page(export('{"dataset_version":1}\r', "ndjson"))
    writer.write_page(export('{"dataset_version":1}\n', "ndjson"))
    assert stream.getvalue() == '{"dataset_version":1}\r\n{"dataset_version":1}\n'

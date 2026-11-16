"""Fixed-dialect CSV parsing without changing Python's global field-size limit.

The caller bounds the UTF-8 input before parsing. Text runs are consumed together
so large cells do not require one allocation per character.
"""

from __future__ import annotations

import re

_TOKENS = re.compile(r'[^,"\r\n]+|.', re.DOTALL)


def parse_csv(text: str) -> list[list[str]]:
    records: list[list[str]] = []
    row: list[str] = []
    fragments: list[str] = []
    state = "start"
    skip_lf = False
    for match in _TOKENS.finditer(text):
        token = match[0]
        if skip_lf:
            skip_lf = False
            if token == "\n":
                continue
        if state == "quoted":
            if token == '"':
                state = "after_quote"
            else:
                fragments.append(token)
            continue
        if state == "after_quote":
            if token == '"':
                fragments.append('"')
                state = "quoted"
                continue
            if token not in (",", "\r", "\n"):
                raise ValueError("Unexpected text after a closing CSV quote.")
        if token == ",":
            row.append("".join(fragments))
            fragments.clear()
            state = "start"
        elif token in ("\r", "\n"):
            if state != "start" or row:
                row.append("".join(fragments))
            records.append(row)
            row = []
            fragments.clear()
            state = "start"
            skip_lf = token == "\r"
        elif token == '"' and state == "start":
            state = "quoted"
        else:
            fragments.append(token)
            state = "unquoted"
    if state == "quoted":
        raise ValueError("Unterminated CSV quote.")
    if state != "start" or row:
        row.append("".join(fragments))
        records.append(row)
    return records

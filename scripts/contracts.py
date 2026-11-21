"""Check public JSON-operation coverage and the SDK's outcome vocabulary."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any, get_type_hints
from uuid import UUID

from generate import HTTP_METHODS, json_operations

ROOT = Path(__file__).resolve().parents[1]
REVIEW_LIST_PATHS = (
    "/api/v1/organizations/{org_id}/reviews",
    "/api/v1/organizations/{org_id}/reviews/pr/{repository}/{pull_request_number}",
)


def _filter_type(schema: dict[str, Any]) -> object:
    kind = schema.get("type")
    fmt = schema.get("format")
    if kind == ["string", "null"] and fmt == "uuid":
        return UUID | None
    if kind == ["string", "null"] and fmt is None:
        return str | None
    if kind == ["integer", "null"]:
        return int | None
    return object()


def main() -> None:
    document = json.loads((ROOT / "openapi.public.json").read_text())
    declared = {
        operation["operationId"]
        for item in json_operations(document)["paths"].values()
        for method, operation in item.items()
        if method in HTTP_METHODS
    }
    generated = {
        path.stem
        for path in (ROOT / "proofline/_generated/api").glob("*/*.py")
        if path.name != "__init__.py"
    }
    if declared != generated:
        raise SystemExit("Generated JSON operations differ from the public contract.")
    sys.path.insert(0, str(ROOT))
    from proofline import AsyncProoflineClient, ProoflineClient, ReviewFilters

    for client in (ProoflineClient, AsyncProoflineClient):
        helpers = {"close", "aclose", "iter_export_pages", "iter_reviews", "wait_for_review"}
        exposed = {
            name
            for name in dir(client)
            if not name.startswith("_") and name not in helpers and callable(getattr(client, name))
        }
        if exposed != declared | {"export_reviews"}:
            raise SystemExit(f"{client.__name__} operations differ from the public contract.")
    filter_hints = get_type_hints(ReviewFilters)
    for review_path in REVIEW_LIST_PATHS:
        query_parameters = [
            parameter
            for parameter in document["paths"][review_path]["get"].get("parameters", [])
            if parameter.get("in") == "query"
        ]
        expected_filters = {
            parameter["name"]: _filter_type(parameter.get("schema", {}))
            for parameter in query_parameters
            if not parameter.get("required", False)
        }
        if (
            len(expected_filters) != len(query_parameters)
            or filter_hints != expected_filters
            or ReviewFilters.__optional_keys__ != set(expected_filters)
        ):
            raise SystemExit("ReviewFilters differs from the public review-list query parameters.")
    prohibited = {"safe", "passed", "clean"}
    for path in (ROOT / "proofline").rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            identifier = None
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                identifier = node.name
            elif isinstance(node, ast.Name):
                identifier = node.id
            elif isinstance(node, ast.Attribute):
                identifier = node.attr
            elif isinstance(node, ast.arg):
                identifier = node.arg
            if identifier in prohibited:
                raise SystemExit("SDK identifiers cannot claim a change is safe, passed or clean.")
    print("Python operation and outcome-vocabulary contracts passed.")


if __name__ == "__main__":
    main()

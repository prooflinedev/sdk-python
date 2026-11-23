"""Check public JSON-operation coverage and the SDK's outcome vocabulary."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

from generate import HTTP_METHODS, json_operations

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    document = json.loads((ROOT / "openapi.public.json").read_text(encoding="utf-8"))
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

    # The review list helpers take their filters as one TypedDict, so a filter
    # the document adds stays untyped in Python until it is named here.
    filters = {
        parameter["name"]
        for item in document["paths"].values()
        for parameter in item.get("get", {}).get("parameters", [])
        if item.get("get", {}).get("operationId") == "list_reviews" and parameter["in"] == "query"
    }
    if set(ReviewFilters.__annotations__) != filters:
        raise SystemExit("ReviewFilters differs from the list_reviews query parameters.")

    for client in (ProoflineClient, AsyncProoflineClient):
        helpers = {"close", "aclose", "iter_export_pages", "iter_reviews", "wait_for_review"}
        exposed = {
            name
            for name in dir(client)
            if not name.startswith("_") and name not in helpers and callable(getattr(client, name))
        }
        if exposed != declared | {"export_reviews"}:
            raise SystemExit(f"{client.__name__} operations differ from the public contract.")
    prohibited = {"safe", "passed", "clean"}
    for path in (ROOT / "proofline").rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
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

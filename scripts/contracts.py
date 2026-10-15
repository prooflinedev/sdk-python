"""Check public JSON-operation coverage and the SDK's outcome vocabulary."""

from __future__ import annotations

import ast
import json
from pathlib import Path

from generate import json_operations

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    document = json.loads((ROOT / "openapi.public.json").read_text())
    declared = {
        operation["operationId"]
        for item in json_operations(document)["paths"].values()
        for method, operation in item.items()
        if method in {"get", "post", "put", "patch", "delete"}
    }
    generated = {
        path.stem
        for path in (ROOT / "proofline/_generated/api/default").glob("*.py")
        if path.name != "__init__.py"
    }
    if declared != generated or len(declared) != 18:
        raise SystemExit(
            "The generated JSON operations must match the eighteen public JSON token routes."
        )
    tree = ast.parse((ROOT / "proofline/client.py").read_text())
    helpers = {"close", "aclose", "iter_reviews", "wait_for_review"}
    clients = {
        node.name: {
            member.name
            for member in node.body
            if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
            and not member.name.startswith("_")
            and member.name not in helpers
        }
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name in {"ProoflineClient", "AsyncProoflineClient"}
    }
    if clients != {"ProoflineClient": declared, "AsyncProoflineClient": declared}:
        raise SystemExit("Both client facades must expose exactly the generated public operations.")
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

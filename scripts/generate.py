"""Generate the typed API from the committed public document."""

from __future__ import annotations

import argparse
import ast
import importlib.metadata
import json
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

VERSION = "0.29.1"
RUFF_VERSION = "0.14.3"
ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "openapi.public.json"
OUTPUT = ROOT / "proofline" / "_generated"
HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}


def json_operations(document: dict) -> dict:
    """Keep JSON callers; the one metadata stream uses its public HTTP contract."""
    paths = {}
    for path, item in document["paths"].items():
        operations = {}
        for method, operation in item.items():
            if method not in HTTP_METHODS:
                continue
            success: dict = next(
                (
                    response
                    for status, response in operation["responses"].items()
                    if status.isdigit() and 200 <= int(status) < 300
                ),
                {},
            )
            media = success.get("content", {})
            if operation.get("operationId") == "export_reviews":
                rows = (
                    document.get("components", {})
                    .get("schemas", {})
                    .get("ExportRow", {})
                    .get("anyOf", [])
                )
                if (
                    path != "/api/v1/organizations/{org_id}/exports/{dataset}"
                    or method != "get"
                    or set(media) != {"application/x-ndjson", "text/csv"}
                    or any(
                        value.get("schema", {}).get("$ref")
                        != "#/components/schemas/ReviewsMetadataStream"
                        or value.get("x-proofline-row-schema", {}).get("$ref")
                        != "#/components/schemas/ExportRow"
                        for value in media.values()
                    )
                    or not isinstance(rows, list)
                    or len(rows) != 5
                    or any(not isinstance(row, dict) or set(row) != {"$ref"} for row in rows)
                    or {row["$ref"] for row in rows}
                    != {
                        "#/components/schemas/ReviewsExportRow",
                        "#/components/schemas/FindingOutcomesExportRow",
                        "#/components/schemas/FindingValidationsExportRow",
                        "#/components/schemas/SpendExportRow",
                        "#/components/schemas/FindingsExportRow",
                    }
                ):
                    raise SystemExit(
                        "export_reviews requires its declared metadata stream and row schemas"
                    )
                continue
            if set(media) != {"application/json"}:
                raise SystemExit("JSON convenience generation requires a named JSON response")
            operations[method] = operation
        if operations:
            paths[path] = {**{k: v for k, v in item.items() if k not in HTTP_METHODS}, **operations}
    return {**document, "paths": paths}


def generate(destination: Path) -> None:
    if importlib.metadata.version("openapi-python-client") != VERSION:
        raise SystemExit(f"Generation requires openapi-python-client=={VERSION}.")
    if importlib.metadata.version("ruff") != RUFF_VERSION:
        raise SystemExit(f"Generation requires ruff=={RUFF_VERSION}.")
    document = json.loads(DOCUMENT.read_text())
    with tempfile.TemporaryDirectory(prefix="proofline-json-contract-") as temporary:
        json_document = Path(temporary) / "openapi.json"
        json_document.write_text(json.dumps(json_operations(document)))
        generate_json(destination, json_document)


def check_version() -> None:
    document = json.loads(DOCUMENT.read_text())
    version = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    package_version = tuple(map(int, version.split(".")))
    api_version = tuple(map(int, document["info"]["version"].split(".")))
    if package_version[:2] != api_version[:2] or package_version[2] < api_version[2]:
        raise SystemExit(
            "The SDK must follow the public API major/minor and not precede its patch."
        )


def generate_json(destination: Path, document: Path) -> None:
    from openapi_python_client import Config, GeneratorData, GeneratorError, MetaType, Project
    from openapi_python_client.config import ConfigFile

    config = Config.from_sources(
        ConfigFile.load_from_path(ROOT / "generator.json"),
        MetaType.NONE,
        document,
        "utf-8",
        False,
        destination,
    )
    data = GeneratorData.from_dict(json.loads(document.read_bytes()), config=config)
    if isinstance(data, GeneratorError):
        raise SystemExit(data)
    project = Project(openapi=data, config=config, custom_template_path=ROOT / "templates")
    if errors := project.build():
        raise SystemExit(errors)

    # Existing public adapters keep their signatures, pagination and stream behavior.
    clients = ast.parse((ROOT / "proofline/client.py").read_bytes())
    custom = {
        cls.name: {
            method.name
            for method in cls.body
            if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        for cls in clients.body
        if isinstance(cls, ast.ClassDef)
    }
    endpoints = [
        (tag, endpoint)
        for tag, group in sorted(data.endpoint_collections_by_tag.items())
        for endpoint in sorted(group.endpoints, key=lambda operation: operation.name)
    ]
    facade = project.env.get_template("operations.py.jinja").render(
        endpoints=endpoints,
        sync=custom["ProoflineClient"],
        asynchronous=custom["AsyncProoflineClient"],
    )
    (destination / "api/operations.py").write_text(facade)
    body = json.loads(document.read_text())["paths"][
        "/api/v1/organizations/{org_id}/repositories/{repo_id}/pull-requests/{number}/review"
    ]["post"].get("requestBody")
    if body is not None:
        if (
            body.get("required", False)
            or set(body.get("content", {})) != {"application/json"}
            or body["content"]["application/json"].get("schema", {}).get("$ref")
            != "#/components/schemas/RunNowRequest"
        ):
            raise SystemExit("request_review requires its optional named RunNowRequest JSON body.")
        endpoint = destination / "api" / "default" / "request_review.py"
        source = endpoint.read_text()
        header = '    headers["Content-Type"] = "application/json"\n'
        json_body = (
            '    if not isinstance(body, Unset):\n        _kwargs["json"] = body.to_dict()\n'
        )
        if (
            source.count(header) != 1
            or source.count(json_body) != 1
            or "body: RunNowRequest | Unset = UNSET" not in source
        ):
            raise SystemExit("The pinned optional request_review body template has changed.")
        # The pinned generator sets this header even when its optional body is UNSET.
        endpoint.write_text(
            source.replace(header, "    if not isinstance(body, Unset):\n    " + header)
        )
    shutil.copyfile(ROOT / "templates" / "LICENSE.openapi-python-client", destination / "LICENSE")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--fix",
            "--select",
            "E,F,I,UP",
            "--ignore",
            "E501",
            str(destination),
        ],
        check=True,
        cwd=ROOT,
    )
    subprocess.run([sys.executable, "-m", "ruff", "format", str(destination)], check=True, cwd=ROOT)


def files(directory: Path) -> dict[Path, bytes]:
    return {
        path.relative_to(directory): path.read_bytes()
        for path in directory.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="proofline-sdk-generation-") as temporary:
        generated = Path(temporary) / "generated"
        generate(generated)
        if args.check:
            check_version()
            if files(generated) != files(OUTPUT):
                raise SystemExit("The generated Python API differs; run scripts/generate.py.")
        else:
            if OUTPUT.exists():
                shutil.rmtree(OUTPUT)
            shutil.copytree(generated, OUTPUT)


if __name__ == "__main__":
    main()

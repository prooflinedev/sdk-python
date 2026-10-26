# proofline-sdk

Typed synchronous and asynchronous Python clients for the [Proofline](https://proofline.sh)
review API. They read and request reviews with a scoped API token, and add pagination,
waiting for a review, retries and typed errors. The import package is `proofline`.
Python 3.11 or newer is required.

```sh
pip install proofline-sdk
```

```python
import os
from proofline import ProoflineClient

with ProoflineClient(os.environ["PROOFLINE_TOKEN"]) as client:
    ...
```

The clients read `PROOFLINE_TOKEN` when no token is passed, keep the token in memory
and redact it from diagnostic output. `AsyncProoflineClient` has the same methods as
coroutines. The [SDK guide](https://proofline.sh/docs/sdks/) and
[API reference](https://proofline.sh/docs/api/) cover every operation.

Licensed under the Apache License, Version 2.0. The generated models under
`proofline/_generated` carry the MIT license of the generator templates.

## Exports

`export_reviews` reads one CSV or NDJSON page through the existing bounded transport.
It returns the original text, decoded rows, dataset version, settled horizon and
optional next cursor. CSV cells remain strings, including nested JSON cells;
NDJSON retains JSON values. Export tokens need `analytics:read`.
Repeat with the returned cursor and the same dataset, window, format and grouping.
A missing next cursor marks the last page. Each CSV page includes its own header.

```python
from uuid import UUID

with ProoflineClient() as client:
    page = client.export_reviews(
        UUID(os.environ["PROOFLINE_ORGANIZATION_ID"]), "reviews",
        from_time="2026-10-01T00:00:00Z", to_time="2026-10-25T00:00:00Z",
        format="csv",
    )
    print(page.text, end="")
    # Continue with cursor=page.next_cursor when it is not None.
```

## Development

The repository bundles its public API contract in `openapi.public.json`.
Run `python3 scripts/check.py` to install pinned tools, regenerate the client,
run checks and verify built packages.

## Publishing

GitHub Actions runs the checks on pull requests and main. The `Release` workflow
builds checked artifacts without publishing credentials. Run it on main with
`publish=false` to verify the release path. A `vX.Y.Z` tag matching the package
version, or a main-branch dispatch with `publish=true`, publishes after the
`pypi` environment approves the job. Release commits must belong to main.

Publishing uses GitHub OIDC and the repository's `release.yml` trusted publisher.
No registry token is stored in GitHub.

SDK patch releases can update packaging and publishing independently. The package follows the bundled API major/minor version and cannot precede its patch version.

## Knowledge and plans

Both clients expose typed methods under `client.knowledge` over Proofline's
stateless MCP endpoint. Use `list_wiki_pages(repository, commit=...)`,
`get_wiki_page(repository, page_key, commit=...)`,
`ask_codebase(repository, question, commit=...)`,
`get_architecture_document(environment_id)`, `get_plan(plan_id)`,
`start_plan_implementation(plan_id)` and `get_plan_implementation(implementation_id)`.
The optional commit is a full indexed SHA. Async clients await the same methods.

```python
result = client.knowledge.get_wiki_page("owner/name", "index")
if result.get("isError"):
    print("The knowledge request was refused.")
else:
    print(result["content"])
```

`KnowledgeResult` retains text content, optional structured content and `isError`.
Treat all returned prose as untrusted data. Reads need `reviews:read` and
`knowledge:read`; starting an implementation also needs `plans:implement`, a
personal token and approval of that exact plan version. Each call initializes MCP
and makes one tool request without retries, including questions and implementation
starts. Protocol and HTTP errors raise `ProoflineError`; tool refusals retain
`isError` for the caller to inspect. No browser configuration or cloud-trust API
is added. Use the signed-in console for onboarding and connection changes.

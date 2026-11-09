# proofline-sdk

`proofline-sdk` provides typed synchronous (`ProoflineClient`) and asynchronous (`AsyncProoflineClient`) Python clients for the [Proofline](https://proofline.sh) review API. The clients read and request reviews with a scoped API token, and include pagination, waiting for a review, retries, and typed errors. The import package is `proofline`. Python 3.11 or newer is required.

This repository is the published distribution of the Proofline Python SDK. The public OpenAPI contract in `openapi.public.json` generates the client and models in `proofline/_generated/`. [Open an issue](https://github.com/prooflinedev/sdk-python/issues) for changes to the OpenAPI contract, generated code, or workflows. Pull requests are welcome for the hand-written client in `proofline/client.py`, transport and helpers outside `proofline/_generated/`, and tests in `tests/`.

## Installation and authentication

```sh
pip install proofline-sdk
```

```python
import os
from proofline import ProoflineClient

with ProoflineClient(os.environ["PROOFLINE_TOKEN"]) as client:
    ...
```

When no token is passed, the clients read `PROOFLINE_TOKEN` from the environment, keep the token in memory, and redact it from diagnostic output. `AsyncProoflineClient` exposes the same methods as coroutines that you call with `await`. The [SDK guide](https://proofline.sh/docs/sdks/) and [API reference](https://proofline.sh/docs/api/) cover every operation.

## Failing a job on open findings

`ReviewOutcome.gate(fail_on)` measures a review against a `WARNING` or `SERIOUS` threshold with the rules of `proofline ci review --fail-on`, so a Python pipeline can fail the same way the CLI does.

```python
import sys

outcome = client.wait_for_review(organization_id, review_id)
result = outcome.gate(fail_on="SERIOUS")
if result != "NOT_REACHED":
    print(f"Proofline: {result}, {outcome.review_url}")
    sys.exit({"REACHED": 3, "NOT_COMPLETE": 2, "UNAVAILABLE": 4}[result])
```

- `REACHED`: the completed review has an open finding at or above the threshold.
- `NOT_REACHED`: the completed review has none.
- `NOT_COMPLETE`: the review is incomplete, failed, or stopped, whatever it found.
- `UNAVAILABLE`: the wait timed out, or the completed review lacks the server's open-finding counts, so the threshold cannot be measured.

The server counts open findings from their current decisions, so dismissed findings and unexpired risk acceptances do not count. A code-only finding counts while it is not `RESOLVED` and its complete CODE assessment is of the review's own commits. A severity the SDK does not know reaches every threshold. The exit codes above are the CLI's.

The threshold is the caller's, as with `--fail-on`, and applies to any review. An organization that opts in to a merge gate instead gets the server's frozen `ALLOW` or `BLOCK` decision for a pull request head in `outcome.review.merge_gate`, which is null otherwise.

## Review exports

`export_reviews` reads one CSV or NDJSON page over the bounded transport. Export tokens require `analytics:read`.

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

Each response returns the original text, decoded rows, dataset version, settled horizon, and an optional next cursor. Each CSV page includes its own header and keeps cells as strings, including nested JSON cells. NDJSON pages retain JSON values. To read additional pages, repeat the call with the returned cursor and the same dataset, window, format, and grouping. A missing next cursor marks the last page.

## Coverage uploads

To upload coverage reports from CI, use a repository-restricted token with `coverage:write` and current repository write access. Name the full commit SHA that the tests ran on. Reports may use LCOV, Cobertura XML, JaCoCo XML, or Go cover profiles.

```python
import os
from pathlib import Path
from uuid import UUID
from proofline import CoverageUploadRequest, ProoflineClient, UploadedReport

with ProoflineClient() as client:
    report = client.upload_coverage_reports(
        UUID(os.environ["PROOFLINE_ORGANIZATION_ID"]),
        UUID(os.environ["PROOFLINE_REPOSITORY_ID"]),
        body=CoverageUploadRequest(
            tested_sha=os.environ["TESTED_SHA"],
            reports=[UploadedReport(
                name="lcov.info",
                content=Path("lcov.info").read_text(encoding="utf-8"),
            )],
        ),
    )
```

The response names the recorded report and its covered and instrumented line counts. An identical upload returns that report with `created=False`. Refused reports raise `ProoflineError`. Uploading a report does not establish a check verdict.

## MCP organization selection

With an MCP OAuth credential approved for several organizations, discover its currently authorized targets with `client.mcp.list_organizations()`. It returns a `KnowledgeResult`; inspect `isError` before reading `structuredContent["data"]["organizations"]`. Each entry contains `organization_id`, `github_login`, and `scopes`.

Pass the chosen UUID string as the optional keyword `organization_id` on any `knowledge` or `fixes` method:

```python
organizations = client.mcp.list_organizations()
if organizations.get("isError"):
    raise RuntimeError("Organization discovery was refused.")
print(organizations["structuredContent"]["data"]["organizations"])
# Set organization_id to the UUID of the organization you intend to use.
result = client.fixes.get_fix_context(finding_id, organization_id=organization_id)
result = client.knowledge.get_wiki_page(
    "owner/name", "index", organization_id=organization_id,
)
```

The async client exposes the same helpers with `await`. Selection applies only to that call, including concurrent calls on one client. A single-organization credential can omit the keyword. An ambiguous omission retains the server's `ORGANIZATION_REQUIRED` tool refusal; a foreign or revoked target retains `NOT_AUTHORIZED` and `isError`. The SDK chooses no default and never retries a tool call. Discovery and targeting use MCP only; an MCP OAuth credential cannot call the REST API. Each organization's scopes and repository restrictions still apply.

## Knowledge and plans

Both clients expose typed methods under `client.knowledge` over Proofline's stateless MCP endpoint. Every method accepts the optional `organization_id` keyword described above:

- `list_wiki_pages(repository, commit=...)`
- `get_wiki_page(repository, page_key, commit=...)`
- `ask_codebase(repository, question, commit=...)`
- `get_architecture_document(environment_id)`
- `get_plan(plan_id)`
- `start_plan_implementation(plan_id)`
- `get_plan_implementation(implementation_id)`

The optional `commit` is a full indexed SHA. Read operations require `reviews:read` and `knowledge:read`. Starting a plan implementation also requires `plans:implement`, a personal token, and approval of that exact plan version.

```python
result = client.knowledge.get_wiki_page("owner/name", "index")
if result.get("isError"):
    print("The knowledge request was refused.")
else:
    print(result["content"])
```

Each call initializes MCP and makes one tool request without retries, including questions and implementation starts. `KnowledgeResult` retains text content, optional structured content, and `isError`. Protocol and HTTP errors raise `ProoflineError`, while tool refusals retain `isError` for the caller to inspect. Treat all returned prose as untrusted data. No browser configuration or cloud-trust API is added; use the signed-in console for onboarding and connection changes.

## Fix context and re-verification

Both clients expose finding and re-verification methods under `client.fixes` over the stateless MCP endpoint. Every method accepts the optional `organization_id` keyword described above:

- `list_open_findings(repository, pull_request_number)`
- `get_fix_context(finding_id)`
- `request_reverification(review_id, finding_ids, commit_sha, note=...)`
- `get_reverification(request_id)`

Read operations require `reviews:read`. Requesting re-verification also requires `reviews:request` and repository write access. `commit_sha` must be the live pushed head, which the server confirms. `request_reverification` accepts 1 to 20 distinct findings of one review and an optional note of 1 to 2,000 characters.

```python
result = client.fixes.request_reverification(
    review_id, [finding_id], pushed_commit_sha,
    note="Fixed the null case and added a regression test.",
)
if result.get("isError"):
    raise RuntimeError("Re-verification was refused.")
```

Calls under `client.fixes` never retry. Results retain untrusted-text wrappers, availability, assessment gaps, and `isError`. `PENDING` and `NOT_VERIFIED` do not establish a fix, and a tool request never records a human disposition.

## Development

The repository bundles its public API contract in `openapi.public.json`. New public operations generate typed methods on both `ProoflineClient` and `AsyncProoflineClient` along with the code in `proofline/_generated/`.

Run `python3 scripts/check.py` to install pinned tools, regenerate the client, run checks, and verify built packages. GitHub Actions runs the checks on pull requests and `main`.

## Publishing

The `Release` workflow builds checked artifacts without publishing credentials. Run it on `main` with `publish=false` to verify the release path. A `vX.Y.Z` tag matching the package version, or a `main`-branch dispatch with `publish=true`, publishes after the `pypi` environment approves the job. Release commits must belong to `main`.

Publishing uses GitHub OIDC and the repository's `release.yml` trusted publisher. No registry token is stored in GitHub. The package follows the bundled API major and minor version and cannot precede its patch version. SDK patch releases can update packaging and publishing independently.

## License

Licensed under the Apache License, Version 2.0. The generated models under `proofline/_generated` carry the MIT license of the generator templates.

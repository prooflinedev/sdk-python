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

## Coverage uploads

Use a repository-restricted token with `coverage:write` and current repository write
access to upload reports from your CI. Name the full commit SHA the tests ran on.
Reports may use LCOV, Cobertura XML, JaCoCo XML or Go cover profiles.

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

The response names the recorded report and its covered and instrumented line counts.
An identical upload returns that report with `created=False`. Refused reports raise
`ProoflineError`; uploading a report does not establish a check verdict.

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

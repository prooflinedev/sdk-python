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

## Development

The repository bundles its public API contract in `openapi.public.json`.
Run `python3 scripts/check.py` to install pinned tools, regenerate the client,
run checks and verify built packages.

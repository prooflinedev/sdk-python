"""Exercise an installed artifact against a real local HTTP peer."""

from __future__ import annotations

import asyncio
import importlib.metadata
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from uuid import UUID

import proofline
from proofline import AsyncProoflineClient, ProoflineClient, SecretStr

ORG = UUID("00000000-0000-4000-8000-000000000001")
REVIEW = UUID("00000000-0000-4000-8000-000000000002")
ASSESSMENT = UUID("00000000-0000-4000-8000-000000000003")
FINDING = UUID("00000000-0000-4000-8000-000000000004")
TOKEN = "pln_synthetic_installed_package_token"


def main() -> None:
    if not Path(proofline.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):
        raise SystemExit("The smoke test must import the installed artifact, not checkout source.")
    assert importlib.metadata.version("proofline-sdk") == "1.0.3"
    assert proofline.__version__ == "1.0.3"
    calls: list[str] = []
    finding = {
        "id": str(FINDING),
        "severity": "HIGH",
        "risk_domain": "SECURITY",
        "claim": "Synthetic installed-package finding.",
        "impact": "Synthetic consequence.",
        "symbols": [],
        "lifecycle_state": "OPEN",
        "evidence_refs": [],
        "rule_refs": [],
        "comment_reactions": [],
    }
    review = {
        "id": str(REVIEW),
        "public_key": "synthetic-review",
        "kind": "PR",
        "status": "COMPLETED",
        "assessment_count": 1,
        "environment_display_names": [],
        "finding_count": 0,
        "trigger_origin": "MANUAL",
        "publication": "WITHHELD",
        "created_at": "2026-01-01T00:00:00Z",
        "stoppable": False,
        "related_reviews": [],
        "subjects": [],
        "actions": {
            "promote_findings": False,
            "publish": False,
            "rerun": False,
            "stop": False,
            "validate_findings": False,
        },
        "assessments": [
            {
                "id": str(ASSESSMENT),
                "environment_display_name": "Synthetic",
                "status": "INCOMPLETE",
                "domains": [],
                "findings": [],
                "reason_codes": ["WORLD_UNAVAILABLE"],
                "checks": {"families": [], "receipt_recorded": False, "status": "UNKNOWN"},
            }
        ],
    }

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            pass

        def do_GET(self) -> None:
            assert self.headers["Authorization"] == f"Bearer {TOKEN}"
            assert self.headers["User-Agent"] == "proofline-python/1.0.3"
            calls.append(self.path)
            body = finding if "/findings/" in self.path else review
            payload = json.dumps(body).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01})
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}"

    async def asynchronous() -> None:
        async with AsyncProoflineClient(SecretStr(TOKEN), base_url=url) as client:
            assert (await client.get_finding(ORG, FINDING)).id == FINDING
            result = await client.wait_for_review(ORG, REVIEW, timeout=2)
            assert result.status == "INCOMPLETE"
            assert result.gaps[0].reason_codes[0] == "WORLD_UNAVAILABLE"
            assert TOKEN not in repr(client)

    try:
        with ProoflineClient(SecretStr(TOKEN), base_url=url) as client:
            assert client.get_finding(ORG, FINDING).id == FINDING
            result = client.wait_for_review(ORG, REVIEW, timeout=2)
            assert result.status == "INCOMPLETE"
            assert result.gaps[0].reason_codes[0] == "WORLD_UNAVAILABLE"
            assert TOKEN not in repr(client)
        asyncio.run(asynchronous())
        assert len(calls) == 4
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
    print("Installed Python SDK sync/async HTTP smoke passed.")


if __name__ == "__main__":
    main()

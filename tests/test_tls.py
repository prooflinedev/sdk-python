"""Real local HTTPS and fail-closed validation tests for custom CA roots and TLS isolation."""

from __future__ import annotations

import asyncio
import inspect
import json
import os
import shutil
import socket
import ssl
import subprocess
import threading
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractContextManager, asynccontextmanager
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Self

import httpx2
import pytest

from proofline import (
    AsyncProoflineClient,
    ProoflineClient,
    ProoflineError,
    SecretStr,
    _sync_http,
    _tls,
    _transport,
)
from tests.fixtures import FINDING, ORG, TOKEN, finding

MODES = pytest.mark.parametrize("mode", ["sync", "async"])


@dataclass(frozen=True)
class TlsMaterial:
    ca_a: Path
    ca_a_hash_dir: Path
    ca_b: Path
    server_a_cert: Path
    server_a_key: Path
    server_b_cert: Path
    server_b_key: Path
    wrong_host_cert: Path
    wrong_host_key: Path
    bundle_ab: Path


def _openssl() -> str:
    binary = shutil.which("openssl")
    if binary is None:
        pytest.fail("openssl is required to run real local TLS integration tests.")
    return binary


def _run_openssl(*args: str, cwd: Path) -> str:
    completed = subprocess.run(
        [_openssl(), *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def _create_ca(directory: Path, name: str, common_name: str) -> tuple[Path, Path]:
    key = directory / f"{name}-key.pem"
    cert = directory / f"{name}.pem"
    ext = directory / f"{name}-ext.cnf"
    ext.write_text(
        "[v3_ca]\n"
        "basicConstraints = critical, CA:TRUE, pathlen:0\n"
        "keyUsage = critical, keyCertSign, cRLSign\n"
        "subjectKeyIdentifier = hash\n",
        encoding="utf-8",
    )
    _run_openssl(
        "req",
        "-x509",
        "-newkey",
        "ec",
        "-pkeyopt",
        "ec_paramgen_curve:prime256v1",
        "-nodes",
        "-keyout",
        str(key),
        "-out",
        str(cert),
        "-days",
        "2",
        "-subj",
        f"/CN={common_name}",
        "-config",
        str(ext),
        "-extensions",
        "v3_ca",
        cwd=directory,
    )
    return cert, key


def _create_leaf(
    directory: Path,
    name: str,
    ca_cert: Path,
    ca_key: Path,
    *,
    common_name: str,
    san: str,
) -> tuple[Path, Path]:
    key = directory / f"{name}-key.pem"
    csr = directory / f"{name}.csr"
    cert = directory / f"{name}.pem"
    ext = directory / f"{name}-ext.cnf"
    ext.write_text(
        "basicConstraints = critical, CA:FALSE\n"
        "keyUsage = critical, digitalSignature\n"
        "extendedKeyUsage = serverAuth\n"
        f"subjectAltName = {san}\n",
        encoding="utf-8",
    )
    _run_openssl(
        "req",
        "-new",
        "-newkey",
        "ec",
        "-pkeyopt",
        "ec_paramgen_curve:prime256v1",
        "-nodes",
        "-keyout",
        str(key),
        "-out",
        str(csr),
        "-subj",
        f"/CN={common_name}",
        cwd=directory,
    )
    _run_openssl(
        "x509",
        "-req",
        "-in",
        str(csr),
        "-CA",
        str(ca_cert),
        "-CAkey",
        str(ca_key),
        "-CAcreateserial",
        "-out",
        str(cert),
        "-days",
        "2",
        "-extfile",
        str(ext),
        cwd=directory,
    )
    return cert, key


@pytest.fixture(scope="module")
def tls_material(tmp_path_factory: pytest.TempPathFactory) -> TlsMaterial:
    directory = tmp_path_factory.mktemp("proofline-tls")
    ca_a, ca_a_key = _create_ca(directory, "ca-a", "Proofline Test Root A")
    ca_b, ca_b_key = _create_ca(directory, "ca-b", "Proofline Test Root B")

    # Populate a real OpenSSL subject-hash directory so capath/SSL_CERT_DIR genuinely resolves ca_a.
    ca_a_hash_dir = directory / "ca-a-hash-dir"
    ca_a_hash_dir.mkdir()
    subject_hash = _run_openssl("x509", "-in", str(ca_a), "-subject_hash", "-noout", cwd=directory)
    shutil.copyfile(ca_a, ca_a_hash_dir / f"{subject_hash.strip()}.0")

    server_a_cert, server_a_key = _create_leaf(
        directory,
        "server-a",
        ca_a,
        ca_a_key,
        common_name="127.0.0.1",
        san="IP:127.0.0.1",
    )
    server_b_cert, server_b_key = _create_leaf(
        directory,
        "server-b",
        ca_b,
        ca_b_key,
        common_name="127.0.0.1",
        san="IP:127.0.0.1",
    )
    wrong_host_cert, wrong_host_key = _create_leaf(
        directory,
        "wrong-host",
        ca_a,
        ca_a_key,
        common_name="wrong.example.invalid",
        san="DNS:wrong.example.invalid",
    )
    bundle_ab = directory / "bundle-ab.pem"
    pem_a = ca_a.read_text(encoding="utf-8").replace("\n", "\r\n")
    pem_b = ca_b.read_text(encoding="utf-8")
    bundle_ab.write_bytes(
        (
            "# Corporate Proxy Bundle — Zürich\r\n"
            + pem_a
            + "\r\n# Duplicate root to verify deduplication\r\n"
            + pem_a
            + "\n# Second root\n"
            + pem_b
        ).encode("utf-8")
    )
    return TlsMaterial(
        ca_a=ca_a,
        ca_a_hash_dir=ca_a_hash_dir,
        ca_b=ca_b,
        server_a_cert=server_a_cert,
        server_a_key=server_a_key,
        server_b_cert=server_b_cert,
        server_b_key=server_b_key,
        wrong_host_cert=wrong_host_cert,
        wrong_host_key=wrong_host_key,
        bundle_ab=bundle_ab,
    )


class _QuietTlsServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(
        self,
        address: tuple[str, int],
        handler: type[BaseHTTPRequestHandler],
        ssl_context: ssl.SSLContext,
    ) -> None:
        self._ssl_context = ssl_context
        super().__init__(address, handler)

    def process_request_thread(self, request: Any, client_address: Any) -> None:
        # Perform the TLS handshake on the worker thread with a bounded socket timeout
        # so a stalled or rejecting peer can never block the server accept loop.
        request.settimeout(5.0)
        try:
            wrapped = self._ssl_context.wrap_socket(request, server_side=True)
        except (OSError, ssl.SSLError):
            self.shutdown_request(request)
            return
        super().process_request_thread(wrapped, client_address)

    def handle_error(self, request: object, client_address: object) -> None:
        # Expected TLS handshake rejections from negative tests should stay quiet.
        return


class TlsServer(AbstractContextManager["TlsServer"]):
    def __init__(self, cert: Path, key: Path) -> None:
        self.requests: list[str] = []
        lock = threading.Lock()
        owner = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, format: str, *args: object) -> None:
                pass

            def do_GET(self) -> None:
                with lock:
                    owner.requests.append(self.path)
                payload = json.dumps(finding()).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                try:
                    self.wfile.write(payload)
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError, ssl.SSLError):
                    pass

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=str(cert), keyfile=str(key))
        self._server = _QuietTlsServer(("127.0.0.1", 0), Handler, context)
        self._thread = threading.Thread(
            target=self._server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
        )
        self.port = self._server.server_port
        self.url = f"https://127.0.0.1:{self.port}"

    def __enter__(self) -> Self:
        self._thread.start()
        return self

    def __exit__(self, *args: object) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=2)


@asynccontextmanager
async def client_session(
    mode: str,
    base_url: str,
    *,
    ca_cert: str | os.PathLike[str] | None = None,
) -> AsyncIterator[ProoflineClient | AsyncProoflineClient]:
    if mode == "sync":
        with ProoflineClient(TOKEN, base_url=base_url, timeout=5, ca_cert=ca_cert) as client:
            yield client
    else:
        async with AsyncProoflineClient(
            TOKEN, base_url=base_url, timeout=5, ca_cert=ca_cert
        ) as client:
            yield client


async def fetch_finding(client: ProoflineClient | AsyncProoflineClient) -> Any:
    result = client.get_finding(ORG, FINDING)
    return await result if inspect.isawaitable(result) else result


@pytest.fixture(autouse=True)
def clear_tls_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for variable in ("PROOFLINE_CA_CERT", "SSL_CERT_FILE", "SSL_CERT_DIR"):
        monkeypatch.delenv(variable, raising=False)


def _handshake(port: int, context: ssl.SSLContext, server_hostname: str) -> None:
    with socket.create_connection(("127.0.0.1", port), timeout=5) as raw_sock:
        with context.wrap_socket(raw_sock, server_hostname=server_hostname):
            pass


@MODES
async def test_https_fails_without_ca_cert(mode: str, tls_material: TlsMaterial) -> None:
    with TlsServer(tls_material.server_a_cert, tls_material.server_a_key) as server:
        async with client_session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as caught:
                await fetch_finding(client)
            assert caught.value.status == 0
            assert caught.value.type == "urn:proofline:sdk:transport-unavailable"
        assert server.requests == []


@MODES
@pytest.mark.parametrize("env_var", ["SSL_CERT_FILE", "SSL_CERT_DIR"])
async def test_https_ignores_ambient_ssl_cert_env_vars(
    mode: str, env_var: str, tls_material: TlsMaterial, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_value = (
        str(tls_material.ca_a) if env_var == "SSL_CERT_FILE" else str(tls_material.ca_a_hash_dir)
    )
    monkeypatch.setenv(env_var, env_value)

    with TlsServer(tls_material.server_a_cert, tls_material.server_a_key) as server:
        # Positive control: OpenSSL default context honoring this env var trusts server_a.
        control_ctx = (
            ssl.create_default_context(cafile=env_value)
            if env_var == "SSL_CERT_FILE"
            else ssl.create_default_context(capath=env_value)
        )
        _handshake(server.port, control_ctx, "127.0.0.1")

        # Proofline clients must ignore the ambient env var and reject the untrusted root.
        async with client_session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as caught:
                await fetch_finding(client)
            assert caught.value.status == 0
            assert caught.value.type == "urn:proofline:sdk:transport-unavailable"
        assert server.requests == []


@MODES
@pytest.mark.parametrize("as_path", [False, True])
async def test_https_succeeds_with_explicit_ca_cert(
    mode: str, as_path: bool, tls_material: TlsMaterial
) -> None:
    ca_arg: str | Path = tls_material.ca_a if as_path else str(tls_material.ca_a)
    with TlsServer(tls_material.server_a_cert, tls_material.server_a_key) as server:
        async with client_session(mode, server.url, ca_cert=ca_arg) as client:
            loaded = await fetch_finding(client)
            assert loaded.id == FINDING
        assert len(server.requests) == 1


@MODES
async def test_https_succeeds_with_proofline_ca_cert_env(
    mode: str, tls_material: TlsMaterial, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PROOFLINE_CA_CERT", str(tls_material.ca_a))
    with TlsServer(tls_material.server_a_cert, tls_material.server_a_key) as server:
        async with client_session(mode, server.url) as client:
            loaded = await fetch_finding(client)
            assert loaded.id == FINDING
        assert len(server.requests) == 1


@MODES
async def test_https_explicit_ca_cert_overrides_env(
    mode: str, tls_material: TlsMaterial, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PROOFLINE_CA_CERT", str(tls_material.ca_b))
    with TlsServer(tls_material.server_a_cert, tls_material.server_a_key) as server:
        async with client_session(mode, server.url, ca_cert=tls_material.ca_a) as client:
            loaded = await fetch_finding(client)
            assert loaded.id == FINDING

    monkeypatch.setenv("PROOFLINE_CA_CERT", str(tls_material.ca_a))
    with TlsServer(tls_material.server_a_cert, tls_material.server_a_key) as server:
        async with client_session(mode, server.url, ca_cert=tls_material.ca_b) as client:
            with pytest.raises(ProoflineError) as caught:
                await fetch_finding(client)
            assert caught.value.type == "urn:proofline:sdk:transport-unavailable"


@MODES
async def test_https_empty_env_counts_as_unset(
    mode: str, tls_material: TlsMaterial, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PROOFLINE_CA_CERT", "")
    with TlsServer(tls_material.server_a_cert, tls_material.server_a_key) as server:
        async with client_session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as caught:
                await fetch_finding(client)
            assert caught.value.type == "urn:proofline:sdk:transport-unavailable"


@MODES
async def test_https_multi_cert_bundle_with_utf8_comments_crlf_and_duplicates(
    mode: str, tls_material: TlsMaterial
) -> None:
    for cert, key in (
        (tls_material.server_a_cert, tls_material.server_a_key),
        (tls_material.server_b_cert, tls_material.server_b_key),
    ):
        with TlsServer(cert, key) as server:
            async with client_session(mode, server.url, ca_cert=tls_material.bundle_ab) as client:
                loaded = await fetch_finding(client)
                assert loaded.id == FINDING


@MODES
async def test_https_enforces_hostname_verification_with_trusted_ca(
    mode: str, tls_material: TlsMaterial
) -> None:
    with TlsServer(tls_material.wrong_host_cert, tls_material.wrong_host_key) as server:
        # Positive control against the exact same leaf: verifying with its matching SAN succeeds,
        # while verifying against 127.0.0.1 specifically raises SSLCertVerificationError.
        ctx = _tls.build_ssl_context(tls_material.ca_a)
        _handshake(server.port, ctx, "wrong.example.invalid")
        with pytest.raises(ssl.SSLCertVerificationError):
            _handshake(server.port, ctx, "127.0.0.1")

        # Client connecting to https://127.0.0.1 must therefore fail verification.
        async with client_session(mode, server.url, ca_cert=tls_material.ca_a) as client:
            with pytest.raises(ProoflineError) as caught:
                await fetch_finding(client)
            assert caught.value.status == 0
            assert caught.value.type == "urn:proofline:sdk:transport-unavailable"
        assert server.requests == []


@pytest.mark.parametrize("factory", [ProoflineClient, AsyncProoflineClient])
def test_ca_cert_validation_fails_fast_before_requests(
    factory: Callable[..., ProoflineClient | AsyncProoflineClient],
    tmp_path: Path,
    tls_material: TlsMaterial,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    missing = tmp_path / "missing.pem"
    with pytest.raises(FileNotFoundError):
        factory(TOKEN, ca_cert=missing)

    with pytest.raises(OSError):
        factory(TOKEN, ca_cert=tmp_path)

    for bad_path in ("", "   "):
        with pytest.raises(ValueError):
            factory(TOKEN, ca_cert=bad_path)

    monkeypatch.setenv("PROOFLINE_CA_CERT", "   ")
    with pytest.raises(ValueError):
        factory(TOKEN)
    monkeypatch.delenv("PROOFLINE_CA_CERT")

    valid_pem = tls_material.ca_a.read_text(encoding="utf-8")
    valid_lines = valid_pem.splitlines()
    punctuated_pem = "\n".join([valid_lines[0], "!" + valid_lines[1], *valid_lines[2:]]) + "\n"

    invalid_cases: dict[str, bytes] = {
        "empty.pem": b"",
        "plain.pem": b"not a certificate\n",
        "non-utf8.der": b"\x30\x82\x01\x0a\xff\xfe",
        "public-key-only.pem": (
            b"-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE\n"
            b"-----END PUBLIC KEY-----\n"
        ),
        "empty-block.pem": b"-----BEGIN CERTIFICATE-----\n-----END CERTIFICATE-----\n",
        "unterminated.pem": b"-----BEGIN CERTIFICATE-----\nAAAA\n",
        "nested-begin.pem": (
            b"-----BEGIN CERTIFICATE-----\n-----BEGIN CERTIFICATE-----\n"
            b"AAAA\n-----END CERTIFICATE-----\n"
        ),
        "stray-end.pem": b"-----END CERTIFICATE-----\n",
        "bad-base64.pem": (
            b"-----BEGIN CERTIFICATE-----\n***invalid***\n-----END CERTIFICATE-----\n"
        ),
        "punctuated-base64.pem": punctuated_pem.encode("utf-8"),
        "invalid-asn1.pem": b"-----BEGIN CERTIFICATE-----\nAAAA\n-----END CERTIFICATE-----\n",
        "mixed-valid-and-invalid-b64.pem": (
            valid_pem + "\n-----BEGIN CERTIFICATE-----\n***invalid***\n-----END CERTIFICATE-----\n"
        ).encode("utf-8"),
        "mixed-valid-and-invalid-asn1.pem": (
            valid_pem + "\n-----BEGIN CERTIFICATE-----\nAAAA\n-----END CERTIFICATE-----\n"
        ).encode("utf-8"),
    }
    for filename, payload in invalid_cases.items():
        path = tmp_path / filename
        path.write_bytes(payload)
        with pytest.raises(ValueError, match="CA certificate"):
            factory(TOKEN, ca_cert=path)

    oversized = tmp_path / "oversized.pem"
    oversized.write_bytes(b"a" * (_tls.MAX_CA_CERT_BYTES + 1))
    with pytest.raises(ValueError, match="limit"):
        factory(TOKEN, ca_cert=oversized)


def test_read_bounded_stops_at_limit_plus_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    oversized = tmp_path / "very-large.pem"
    oversized.write_bytes(b"a" * (_tls.MAX_CA_CERT_BYTES + 65_536))
    requested_sizes: list[int] = []
    real_fdopen = os.fdopen

    class TrackingHandle:
        def __init__(self, inner: Any) -> None:
            self._inner = inner

        def __enter__(self) -> Self:
            self._inner.__enter__()
            return self

        def __exit__(self, *args: object) -> None:
            self._inner.__exit__(*args)

        def read(self, size: int = -1) -> bytes:
            requested_sizes.append(size)
            return bytes(self._inner.read(size))

    monkeypatch.setattr(
        _tls.os, "fdopen", lambda fd, mode="r": TrackingHandle(real_fdopen(fd, mode))
    )
    with pytest.raises(ValueError, match="limit"):
        _tls._read_bounded(oversized)
    assert requested_sizes == [_tls.MAX_CA_CERT_BYTES + 1]


def test_ca_cert_rejects_fifo_without_blocking(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mkfifo = getattr(os, "mkfifo", None)
    if mkfifo is not None:
        fifo = tmp_path / "blocking.fifo"
        mkfifo(fifo)
        with pytest.raises(ValueError, match="regular file"):
            _tls.build_ssl_context(fifo)
        return

    # On Windows (no POSIX mkfifo), verify the fstat non-regular-file guard directly.
    import stat

    dummy = tmp_path / "dummy.pem"
    dummy.write_bytes(b"")
    real_fstat = os.fstat

    class FakeFifoStat:
        def __init__(self, inner: os.stat_result) -> None:
            self.st_mode = stat.S_IFIFO | 0o600
            self._inner = inner

    with monkeypatch.context() as patch:
        patch.setattr(_tls.os, "fstat", lambda fd: FakeFifoStat(real_fstat(fd)))
        with pytest.raises(ValueError, match="regular file"):
            _tls.build_ssl_context(dummy)


def test_build_ssl_context_preserves_verification_invariants(tls_material: TlsMaterial) -> None:
    default_ctx = _tls.build_ssl_context()
    assert default_ctx.verify_mode == ssl.CERT_REQUIRED
    assert default_ctx.check_hostname is True

    merged_ctx = _tls.build_ssl_context(tls_material.ca_a)
    assert merged_ctx.verify_mode == ssl.CERT_REQUIRED
    assert merged_ctx.check_hostname is True


@MODES
async def test_https_merges_ca_cert_beside_existing_roots_without_replacing_them(
    mode: str, tls_material: TlsMaterial, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Simulate a Linux stdlib SSLContext preloaded with ca_b, then merge ca_a beside it."""

    def base_context(*, _trust_env: bool = True) -> ssl.SSLContext:
        assert _trust_env is False
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.load_verify_locations(cafile=str(tls_material.ca_b))
        return ctx

    monkeypatch.setattr(_tls.httpcore2, "default_ssl_context", base_context)
    for cert, key in (
        (tls_material.server_a_cert, tls_material.server_a_key),
        (tls_material.server_b_cert, tls_material.server_b_key),
    ):
        with TlsServer(cert, key) as server:
            async with client_session(mode, server.url, ca_cert=tls_material.ca_a) as client:
                loaded = await fetch_finding(client)
                assert loaded.id == FINDING


@MODES
async def test_https_accepts_utf8_bom_pem(
    mode: str, tls_material: TlsMaterial, tmp_path: Path
) -> None:
    bom_ca = tmp_path / "bom-ca.pem"
    bom_ca.write_bytes(b"\xef\xbb\xbf" + tls_material.ca_a.read_bytes())
    with TlsServer(tls_material.server_a_cert, tls_material.server_a_key) as server:
        async with client_session(mode, server.url, ca_cert=bom_ca) as client:
            loaded = await fetch_finding(client)
            assert loaded.id == FINDING


@pytest.mark.parametrize("env_var", ["SSL_CERT_FILE", "SSL_CERT_DIR"])
def test_direct_transports_ignore_ambient_ssl_cert_env(
    env_var: str, tls_material: TlsMaterial, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_value = (
        str(tls_material.ca_a) if env_var == "SSL_CERT_FILE" else str(tls_material.ca_a_hash_dir)
    )
    monkeypatch.setenv(env_var, env_value)
    with TlsServer(tls_material.server_a_cert, tls_material.server_a_key) as server:
        sync_transport = _sync_http.Transport()
        try:
            with pytest.raises(httpx2.TransportError):
                sync_transport.handle_request(httpx2.Request("GET", server.url))
        finally:
            sync_transport.close()

        async def run_async() -> None:
            async_transport = _transport.AsyncRetryTransport(SecretStr(TOKEN), 5.0)
            try:
                with pytest.raises(httpx2.TransportError):
                    await async_transport.handle_async_request(httpx2.Request("GET", server.url))
            finally:
                await async_transport.aclose()

        asyncio.run(run_async())

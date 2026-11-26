"""TLS trust-store isolation and additive custom CA root loading.

By default, both sync and async clients trust only the operating system's
root store and ignore ambient ``SSL_CERT_FILE`` / ``SSL_CERT_DIR`` overrides.
Passing ``ca_cert`` or setting ``PROOFLINE_CA_CERT`` merges additional PEM root
certificates beside the system roots without weakening certificate or hostname
verification.
"""

from __future__ import annotations

import base64
import binascii
import errno
import os
import ssl
import stat
from pathlib import Path

import httpcore2

CA_CERT_ENV = "PROOFLINE_CA_CERT"
MAX_CA_CERT_BYTES = 4 * 1024 * 1024
_PEM_BEGIN = "-----BEGIN CERTIFICATE-----"
_PEM_END = "-----END CERTIFICATE-----"


def _resolve_path(ca_cert: str | os.PathLike[str] | None) -> Path | None:
    if ca_cert is not None:
        raw_path = os.fspath(ca_cert)
        if not isinstance(raw_path, str):
            raise TypeError("ca_cert must be a str or os.PathLike[str].")
        if not raw_path or not raw_path.strip():
            raise ValueError("The CA certificate path must not be empty.")
        return Path(raw_path)
    env_value = os.environ.get(CA_CERT_ENV)
    if env_value is None or env_value == "":
        return None
    if not env_value.strip():
        raise ValueError(f"{CA_CERT_ENV} must not be whitespace-only.")
    return Path(env_value)


def _read_bounded(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NONBLOCK", 0)
    fd = os.open(path, flags)
    owned = True
    try:
        metadata = os.fstat(fd)
        if stat.S_ISDIR(metadata.st_mode):
            raise IsADirectoryError(errno.EISDIR, os.strerror(errno.EISDIR), str(path))
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError(f"The CA certificate path {path} must be a regular file.")
        owned = False
        handle = os.fdopen(fd, "rb")
    except BaseException:
        if owned:
            os.close(fd)
        raise
    with handle:
        data = handle.read(MAX_CA_CERT_BYTES + 1)
    if len(data) > MAX_CA_CERT_BYTES:
        raise ValueError(
            f"The CA certificate file {path} exceeds the {MAX_CA_CERT_BYTES}-byte limit."
        )
    return data


def _parse_pem_certificates(raw: bytes, path: Path) -> list[str]:
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError(f"The CA certificate file {path} is not valid UTF-8 PEM.") from None

    certificates: list[str] = []
    seen: set[bytes] = set()
    in_block = False
    body_lines: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped == _PEM_BEGIN:
            if in_block:
                raise ValueError(f"The CA certificate file {path} has malformed PEM framing.")
            in_block = True
            body_lines = []
        elif stripped == _PEM_END:
            if not in_block:
                raise ValueError(f"The CA certificate file {path} has malformed PEM framing.")
            body = "".join(body_lines)
            if not body:
                raise ValueError(
                    f"The CA certificate file {path} contains an empty PEM certificate."
                )
            try:
                der = base64.b64decode(body.encode("ascii"), validate=True)
            except (UnicodeEncodeError, binascii.Error, ValueError):
                raise ValueError(
                    f"The CA certificate file {path} contains an invalid PEM certificate."
                ) from None
            if der not in seen:
                seen.add(der)
                certificates.append(ssl.DER_cert_to_PEM_cert(der))
            in_block = False
            body_lines = []
        elif in_block:
            body_lines.append(stripped)

    if in_block:
        raise ValueError(f"The CA certificate file {path} has an unterminated PEM certificate.")
    if not certificates:
        raise ValueError(f"The CA certificate file {path} contains no PEM certificate.")
    return certificates


def build_ssl_context(ca_cert: str | os.PathLike[str] | None = None) -> ssl.SSLContext:
    """Build an SSLContext using OS roots (ignoring SSL_CERT_*) plus optional PEM roots."""
    path = _resolve_path(ca_cert)
    context = httpcore2.default_ssl_context(_trust_env=False)
    if path is None:
        return context
    raw = _read_bounded(path)
    for certificate in _parse_pem_certificates(raw, path):
        try:
            context.load_verify_locations(cadata=certificate)
        except (ssl.SSLError, ValueError):
            raise ValueError(
                f"The CA certificate file {path} contains an invalid X.509 certificate."
            ) from None
    return context

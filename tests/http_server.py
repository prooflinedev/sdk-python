"""A real loopback HTTP peer for the generated sync and async clients."""

from __future__ import annotations

import json
import threading
import time
from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Self


@dataclass
class Request:
    method: str
    path: str
    headers: dict[str, str]
    body: bytes
    peer_port: int


@dataclass
class Reply:
    status: int = 200
    body: Any = None
    headers: dict[str, str] = field(default_factory=dict)
    split: int | None = None
    pause: float = 0
    chunk_size: int | None = None
    header_pause: float = 0
    first_pause: float = 0


class Server(AbstractContextManager["Server"]):
    def __init__(self, respond: Callable[[Request, int], Reply]) -> None:
        self.requests: list[Request] = []
        self._lock = threading.Lock()
        owner = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, format: str, *args: object) -> None:
                pass

            def do_GET(self) -> None:
                self.dispatch()

            def do_POST(self) -> None:
                self.dispatch()

            def dispatch(self) -> None:
                request = Request(
                    self.command,
                    self.path,
                    dict(self.headers),
                    self.rfile.read(int(self.headers.get("Content-Length", 0))),
                    self.client_address[1],
                )
                with owner._lock:
                    owner.requests.append(request)
                    index = len(owner.requests) - 1
                reply = respond(request, index)
                payload = (
                    reply.body if isinstance(reply.body, bytes) else json.dumps(reply.body).encode()
                )
                time.sleep(reply.header_pause)
                self.send_response(reply.status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                for key, value in reply.headers.items():
                    self.send_header(key, value)
                self.end_headers()
                try:
                    time.sleep(reply.first_pause)
                    if reply.chunk_size:
                        for start in range(0, len(payload), reply.chunk_size):
                            self.wfile.write(payload[start : start + reply.chunk_size])
                            self.wfile.flush()
                            time.sleep(reply.pause)
                    else:
                        split = len(payload) if reply.split is None else reply.split
                        self.wfile.write(payload[:split])
                        self.wfile.flush()
                        time.sleep(reply.pause)
                        self.wfile.write(payload[split:])
                        self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    pass

        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._server.daemon_threads = True
        self._thread = threading.Thread(
            target=self._server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
        )
        self.url = f"http://127.0.0.1:{self._server.server_port}"

    def __enter__(self) -> Self:
        self._thread.start()
        return self

    def __exit__(self, *args: object) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=2)

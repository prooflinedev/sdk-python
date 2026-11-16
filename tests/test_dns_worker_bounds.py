"""Diagnostic regression test for abandoned DNS workers."""

import socket
import threading

import httpcore
import pytest

from proofline._sync_http import resolve


def test_repeated_dns_timeouts_bound_outstanding_workers(monkeypatch):
    release = threading.Event()
    started = threading.Event()
    workers = []
    lock = threading.Lock()

    def slow_dns(*args, **kwargs):
        with lock:
            workers.append(threading.current_thread())
            started.set()
        release.wait(timeout=5)
        return [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                ("127.0.0.1", 443),
            )
        ]

    monkeypatch.setattr(socket, "getaddrinfo", slow_dns)

    try:
        for _ in range(16):
            with pytest.raises(httpcore.ConnectTimeout):
                resolve("slow-dns.example.invalid", 443, 0.005)

        assert started.is_set()
        active = sum(worker.is_alive() for worker in workers)
        print(f"Outstanding DNS workers: {active}")

        # Exploratory safety threshold, not yet a product requirement.
        assert active <= 8, (
            f"{active} DNS workers remain active after timeouts"
        )
    finally:
        release.set()
        for worker in workers:
            worker.join(timeout=2)

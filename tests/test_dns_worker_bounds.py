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
        assert active <= 8, f"{active} DNS workers remain active after timeouts"
    finally:
        release.set()
        for worker in workers:
            worker.join(timeout=2)


def test_dns_slot_wait_uses_shared_timeout(monkeypatch):
    """Waiting for a DNS slot consumes the lookup timeout."""
    import importlib
    import time

    module = importlib.import_module("proofline._sync_http")
    received = []

    class DelayedSlots:
        def acquire(self, timeout=None):
            time.sleep(0.05)
            return True

        def release(self):
            pass

    class FakeLookup:
        def __init__(self, host, port):
            pass

        def addresses(self, timeout):
            received.append(timeout)
            return ["127.0.0.1"]

    monkeypatch.setattr(module, "_DNS_WORKER_SLOTS", DelayedSlots())
    monkeypatch.setattr(module, "Lookup", FakeLookup)

    result = module.resolve("delayed-dns.example.invalid", 443, 0.2)

    assert result == ["127.0.0.1"]
    assert len(received) == 1
    assert received[0] is not None
    assert 0 < received[0] < 0.18

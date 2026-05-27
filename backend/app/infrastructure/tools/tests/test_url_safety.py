"""DEBT-075 · SSRF defense in depth — is_public_host.

Cubre: dominio público (allow), localhost/127.0.0.1 (reject), 169.254.169.254
metadata cloud (reject), RFC1918 10.x/192.168.x/172.16.x (reject) e IP pública
normal (allow). El DNS se mockea (socket.getaddrinfo) para no tocar red. IPs
literales se validan sin DNS. Fail-safe: ante cualquier duda => False.
"""
import socket
import pytest

from app.infrastructure.tools import _url_safety
from app.infrastructure.tools._url_safety import is_public_host


def _fake_getaddrinfo(ip: str):
    def _inner(host, *a, **k):
        return [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", (ip, 0))]
    return _inner


def test_public_domain_allowed(monkeypatch):
    monkeypatch.setattr(_url_safety.socket, "getaddrinfo", _fake_getaddrinfo("93.184.216.34"))
    assert is_public_host("https://example.com/path") is True


def test_public_ip_literal_allowed():
    assert is_public_host("https://8.8.8.8/") is True
    assert is_public_host("http://93.184.216.34") is True


def test_localhost_rejected(monkeypatch):
    monkeypatch.setattr(_url_safety.socket, "getaddrinfo", _fake_getaddrinfo("127.0.0.1"))
    assert is_public_host("http://localhost/admin") is False


def test_loopback_ip_rejected():
    assert is_public_host("http://127.0.0.1:8000/") is False
    assert is_public_host("http://[::1]/") is False


def test_metadata_link_local_rejected():
    assert is_public_host("http://169.254.169.254/latest/meta-data/") is False


@pytest.mark.parametrize("ip", ["10.0.0.5", "192.168.1.1", "172.16.0.1", "172.31.255.255"])
def test_rfc1918_private_rejected(ip):
    assert is_public_host(f"http://{ip}/") is False


def test_domain_resolving_to_private_rejected(monkeypatch):
    # DNS-rebinding-style: dominio que resuelve a IP interna => reject.
    monkeypatch.setattr(_url_safety.socket, "getaddrinfo", _fake_getaddrinfo("10.1.2.3"))
    assert is_public_host("https://evil.example.com/") is False


def test_unspecified_and_bad_input_rejected():
    assert is_public_host("http://0.0.0.0/") is False
    assert is_public_host("not-a-url") is False
    assert is_public_host("") is False


def test_dns_failure_is_failsafe(monkeypatch):
    def _boom(*a, **k):
        raise socket.gaierror("no such host")
    monkeypatch.setattr(_url_safety.socket, "getaddrinfo", _boom)
    assert is_public_host("https://nonexistent.invalid/") is False

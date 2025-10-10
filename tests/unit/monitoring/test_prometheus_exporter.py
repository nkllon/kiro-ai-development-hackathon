import types

import pytest

from src.beast_mode.monitoring import prometheus_exporter


@pytest.fixture(autouse=True)
def reset_prometheus_exporter_singleton(monkeypatch):
    """Reset singleton state between tests."""
    monkeypatch.setattr(prometheus_exporter.PrometheusExporter, "_instance", None)
    monkeypatch.setattr(prometheus_exporter.PrometheusExporter, "_initialized", False)
    yield
    prometheus_exporter.PrometheusExporter._instance = None
    prometheus_exporter.PrometheusExporter._initialized = False


def test_prometheus_exporter_accepts_prometheus_url(monkeypatch):
    """Ensure legacy exporter accepts prometheus_url parameter without raising."""
    monkeypatch.setattr(prometheus_exporter, "PROMETHEUS_AVAILABLE", False)
    exporter = prometheus_exporter.PrometheusExporter(
        prometheus_url="http://localhost:9090",
        enable_http_server=False,
    )
    assert exporter.prometheus_url == "http://localhost:9090"
    assert exporter._ignored_kwargs == {}


def test_prometheus_exporter_ignores_unknown_kwargs(monkeypatch):
    """Unknown kwargs should not break initialization but be tracked for diagnostics."""
    monkeypatch.setattr(prometheus_exporter, "PROMETHEUS_AVAILABLE", False)
    exporter = prometheus_exporter.PrometheusExporter(
        prometheus_url="http://localhost:9090",
        enable_http_server=False,
        some_new_arg="value",
    )
    assert exporter._ignored_kwargs == {"some_new_arg": "value"}

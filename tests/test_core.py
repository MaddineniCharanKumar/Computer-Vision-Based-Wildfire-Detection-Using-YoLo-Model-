from __future__ import annotations

from fastapi.testclient import TestClient

from fireguard.api import app
from fireguard.environment import DemoProvider, UnavailableProvider
from fireguard.risk import calculate_risk
from fireguard.domain import area_proxy, growth_rate


def test_risk_is_bounded() -> None:
    result = calculate_risk({"visual": 100})
    assert 0 <= result["score"] <= 100


def test_area_proxy_is_not_physical_area() -> None:
    assert area_proxy((0, 0, 0.5, 0.2)) == 0.1


def test_growth() -> None:
    assert growth_rate(10, 15) == 50


def test_unavailable_provider_marks_data_unavailable() -> None:
    provider = UnavailableProvider()
    payload = provider.current()
    assert payload["freshness"] == "UNAVAILABLE"
    assert payload["status"] == "UNAVAILABLE"


def test_demo_provider_is_explicitly_labeled() -> None:
    payload = DemoProvider().current()
    assert payload["demo"] is True
    assert payload["status"] == "DEMO_MODE"


def test_api_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert "status" in response.json()

from __future__ import annotations

import asyncio

from fireguard.environment import DemoProvider, OpenMeteoProvider, UnavailableProvider
from fireguard.services.environment_service import EnvironmentalService


def test_unavailable_provider_marks_data_unavailable() -> None:
    payload = asyncio.run(EnvironmentalService(UnavailableProvider()).fetch())
    assert payload["freshness"] == "UNAVAILABLE"
    assert payload["status"] == "UNAVAILABLE"


def test_demo_provider_is_explicitly_labeled() -> None:
    payload = asyncio.run(EnvironmentalService(DemoProvider()).fetch())
    assert payload["demo"] is True
    assert payload["status"] == "DEMO_MODE"


def test_live_provider_requires_coordinates() -> None:
    payload = asyncio.run(EnvironmentalService(OpenMeteoProvider("https://api.open-meteo.com/v1/forecast")).fetch())
    assert payload["status"] == "UNAVAILABLE"
    assert payload["freshness"] == "UNAVAILABLE"

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ForecastResult:
    horizon_minutes: int
    spread_speed: float
    direction: str
    risk_score: float
    perimeters: list[dict[str, float]]
    status: str = "PROTOTYPE"

    def to_dict(self) -> dict[str, object]:
        return {
            "horizon_minutes": self.horizon_minutes,
            "spread_speed": self.spread_speed,
            "direction": self.direction,
            "risk_score": self.risk_score,
            "perimeters": self.perimeters,
            "status": self.status,
        }


class ForecastService:
    """Minimal prototype forecast model. It is an engineering placeholder and must not be treated as validated fire physics."""

    @staticmethod
    def predict(
        wind_speed: float = 0.0,
        wind_direction: float = 0.0,
        humidity: float = 50.0,
        temperature: float = 30.0,
        slope: float = 0.0,
        fuel_load: float = 0.5,
        horizon_minutes: int = 30,
    ) -> dict[str, object]:
        normalized_wind = max(0.0, min(100.0, wind_speed))
        normalized_humidity = max(0.0, min(100.0, humidity))
        normalized_heat = max(0.0, min(100.0, temperature))
        normalized_slope = max(0.0, min(100.0, slope))
        hazard = (
            0.35 * normalized_wind
            + 0.25 * (100.0 - normalized_humidity)
            + 0.20 * normalized_heat
            + 0.20 * normalized_slope
            + 0.15 * (fuel_load * 100.0)
        )
        risk_score = max(0.0, min(100.0, hazard))
        spread_speed = (hazard / 100.0) * 2.2
        direction = "NORTH" if 315 <= wind_direction or wind_direction < 45 else "EAST" if 45 <= wind_direction < 135 else "SOUTH" if 135 <= wind_direction < 225 else "WEST"
        perimeter = [
            {"x": 0.0, "y": 0.0},
            {"x": 0.2 + horizon_minutes / 1000.0, "y": 0.1},
            {"x": 0.35 + horizon_minutes / 1000.0, "y": 0.25},
            {"x": 0.2, "y": 0.4},
        ]
        return ForecastResult(
            horizon_minutes=horizon_minutes,
            spread_speed=round(spread_speed, 3),
            direction=direction,
            risk_score=round(risk_score, 2),
            perimeters=perimeter,
            status="PROTOTYPE",
        ).to_dict()

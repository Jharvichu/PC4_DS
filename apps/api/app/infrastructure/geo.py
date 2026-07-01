"""Geospatial utilities (SRP: only geographic calculations)."""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class GeoPoint:
    """Immutable geographic coordinate."""

    latitude: float
    longitude: float

    def to_string(self) -> str:
        """Serialize as 'lat,lon' for storage in a simple String column."""
        return f"{self.latitude},{self.longitude}"

    @staticmethod
    def from_string(value: str) -> "GeoPoint":
        """Parse a 'lat,lon' string back into a GeoPoint."""
        lat_str, lon_str = value.split(",")
        return GeoPoint(latitude=float(lat_str), longitude=float(lon_str))


EARTH_RADIUS_KM = 6371.0


class GeospatialService:
    """Only geographic calculations. No persistence, no I/O."""

    @staticmethod
    def calculate_distance_km(point1: GeoPoint, point2: GeoPoint) -> float:
        """Haversine formula: great-circle distance between two points in km."""
        lat1, lon1 = math.radians(point1.latitude), math.radians(point1.longitude)
        lat2, lon2 = math.radians(point2.latitude), math.radians(point2.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        return EARTH_RADIUS_KM * c

    @staticmethod
    def is_within_radius(center: GeoPoint, point: GeoPoint, radius_km: float) -> bool:
        """Check whether `point` lies within `radius_km` of `center`."""
        return GeospatialService.calculate_distance_km(center, point) <= radius_km

    @staticmethod
    def bounding_box(center: GeoPoint, radius_km: float) -> tuple[float, float, float, float]:
        """Compute a lat/lon bounding box for a cheap pre-filter before Haversine.

        Returns (min_lat, max_lat, min_lon, max_lon).
        """
        lat_delta = radius_km / 111.0  # ~111km per degree latitude
        lon_delta = radius_km / (111.0 * math.cos(math.radians(center.latitude)) or 1e-9)

        return (
            center.latitude - lat_delta,
            center.latitude + lat_delta,
            center.longitude - lon_delta,
            center.longitude + lon_delta,
        )

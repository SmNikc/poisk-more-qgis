"""Utility functions for working with coordinates."""


def parse_coords(coord_str: str):
    """Parse a coordinate string formatted as 'lat, lon'."""
    try:
        lat, lon = map(float, coord_str.strip().split(","))
        return lat, lon
    except ValueError:
        return None, None


def format_coords(lat: float, lon: float) -> str:
    """Format latitude and longitude as a string."""
    return f"{lat:.4f}, {lon:.4f}"

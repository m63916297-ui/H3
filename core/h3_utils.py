import h3
import json
from typing import Any
from .config import settings


def get_h3_index(lat: float, lng: float, resolution: int | None = None) -> str:
    resolution = resolution or settings.H3_RESOLUTION
    return h3.latlng_to_cell(lat, lng, resolution)


def get_h3_center(index: str) -> tuple[float, float]:
    return h3.cell_to_latlng(index)


def get_h3_neighbors(index: str) -> list[str]:
    return h3.grid_disk(index, 1)


def get_h3_kring(index: str, k: int = 1) -> list[str]:
    return h3.grid_disk(index, k)


def get_h3_resolution(index: str) -> int:
    return h3.get_resolution(index)


def cell_to_geojson(index: str) -> dict[str, Any]:
    boundary = h3.cell_to_boundary(index)
    coords = [[coord[1], coord[0]] for coord in boundary]
    coords.append(coords[0])

    center_lat, center_lng = h3.cell_to_latlng(index)

    return {
        "type": "Feature",
        "geometry": {"type": "Polygon", "coordinates": [coords]},
        "properties": {
            "h3_index": index,
            "center_lat": center_lat,
            "center_lng": center_lng,
            "resolution": h3.get_resolution(index),
        },
    }


def cells_to_geojson(cells: list[str]) -> dict[str, Any]:
    features = [cell_to_geojson(cell) for cell in cells]
    return {"type": "FeatureCollection", "features": features}


def get_h3_density(
    incidents: list[dict], resolution: int | None = None
) -> dict[str, int]:
    resolution = resolution or settings.H3_RESOLUTION
    density = {}

    for incident in incidents:
        lat = incident.get("latitude")
        lng = incident.get("longitude")

        if lat is not None and lng is not None:
            index = h3.latlng_to_cell(lat, lng, resolution)
            density[index] = density.get(index, 0) + 1

    return density

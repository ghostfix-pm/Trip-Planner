import math
import os
import logging
import aiohttp

logger = logging.getLogger("trip_planner")
MAPBOX_TOKEN = os.getenv("NEXT_PUBLIC_MAPBOX_TOKEN") or os.getenv("MAPBOX_ACCESS_TOKEN", "")

def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

async def get_mapbox_matrix_distances(coords: list[str]) -> list[list[float]]:
    if not MAPBOX_TOKEN or not coords or len(coords) < 2:
        return []
    
    coords_string = ";".join(coords[:25])
    url = f"https://api.mapbox.com/directions-matrix/v1/mapbox/driving/{coords_string}"
    params = {"access_token": MAPBOX_TOKEN, "annotations": "distance"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    matrix = data.get("distances", [])
                    return [[(val / 1000.0 if val is not None else 999.0) for val in row] for row in matrix]
    except Exception as e:
        logger.error(f"Lỗi Mapbox API: {e}")
    return []
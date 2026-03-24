"""Mock importer for government land sales"""

import random
from typing import List, Optional

from app.bounded_contexts.integrations.base_importer import BaseImporter
from app.schemas.land import LandCreate


class GovernmentSalesImporter(BaseImporter):
    """
    Mock importer for government land sales.
    Generates 30 records with deal_type = "purchase" or "lease".
    Features often defined (official records).
    """

    source_type = "government"

    REGIONS = [
        {"name": "Moscow", "id": 1, "lat": 55.7558, "lon": 37.6173},
        {"name": "Saint Petersburg", "id": 2, "lat": 59.9519, "lon": 30.3594},
        {"name": "Novosibirsk", "id": 3, "lat": 55.0415, "lon": 82.9346},
    ]

    CITIES = [
        {"name": "Moscow", "region_id": 1, "id": 1, "lat": 55.7558, "lon": 37.6173},
        {"name": "Krasnogorsk", "region_id": 1, "id": 2, "lat": 55.8635, "lon": 37.3254},
        {"name": "Saint Petersburg", "region_id": 2, "id": 3, "lat": 59.9519, "lon": 30.3594},
        {"name": "Pushkin", "region_id": 2, "id": 4, "lat": 59.7239, "lon": 30.4084},
        {"name": "Novosibirsk", "region_id": 3, "id": 5, "lat": 55.0415, "lon": 82.9346},
        {"name": "Akademgorodok", "region_id": 3, "id": 6, "lat": 54.8674, "lon": 83.1084},
    ]

    DEAL_TYPES = ["purchase", "lease"]
    CATEGORIES = ["agricultural", "residential"]

    def fetch_raw_data(self) -> List[dict]:
        """Generate 30 mock government sales records"""
        items = []
        for i in range(1, 31):
            region = random.choice(self.REGIONS)
            city_choice = random.choice(
                [c for c in self.CITIES if c["region_id"] == region["id"]]
            )

            lat = region["lat"] + random.uniform(-0.2, 0.2)
            lon = region["lon"] + random.uniform(-0.2, 0.2)

            item = {
                "external_id": f"gov-{i:05d}",
                "title": f"Government land sale in {city_choice['name']} #{i}",
                "description": f"Government-owned land parcel for sale. Structured data from official records. Boundaries defined.",
                "address": f"{random.randint(1, 500)} State Road, {city_choice['name']}",
                "latitude": lat,
                "longitude": lon,
                "price": random.randint(800000, 8000000),
                "area": random.choice([2000, 5000, 10000, 15000, 20000, 50000]),
                "deal_type": random.choice(self.DEAL_TYPES),
                "land_category": random.choice(self.CATEGORIES),
                "region_id": region["id"],
                "city_id": city_choice["id"],
                "boundaries_defined": True,
                "has_roads": True,
            }
            items.append(item)

        return items

    def normalize(self, raw: dict, source_id: int) -> Optional[LandCreate]:
        """Normalize raw government record to LandCreate schema"""
        try:
            return LandCreate(
                external_id=raw["external_id"],
                source_id=source_id,
                region_id=raw["region_id"],
                city_id=raw.get("city_id"),
                title=raw["title"],
                description=raw.get("description"),
                address=raw["address"],
                latitude=raw["latitude"],
                longitude=raw["longitude"],
                price=raw.get("price"),
                area=raw.get("area"),
                land_category=raw.get("land_category"),
                deal_type=raw.get("deal_type"),
            )
        except Exception:
            return None

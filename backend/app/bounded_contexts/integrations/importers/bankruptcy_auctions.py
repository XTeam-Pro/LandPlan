"""Mock importer for bankruptcy auction lands"""

import random
from typing import List, Optional

from app.bounded_contexts.integrations.base_importer import BaseImporter
from app.schemas.land import LandCreate


class BankruptcyAuctionsImporter(BaseImporter):
    """
    Mock importer for bankruptcy auction lands.
    Generates 20 records with deal_type = "auction" and typically lower prices.
    """

    source_type = "bankruptcy"

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

    CATEGORIES = ["commercial", "industrial"]

    def fetch_raw_data(self) -> List[dict]:
        """Generate 20 mock bankruptcy auction records"""
        items = []
        for i in range(1, 21):
            region = random.choice(self.REGIONS)
            city_choice = random.choice(
                [c for c in self.CITIES if c["region_id"] == region["id"]]
            )

            lat = region["lat"] + random.uniform(-0.1, 0.1)
            lon = region["lon"] + random.uniform(-0.1, 0.1)

            item = {
                "external_id": f"bkr-{i:05d}",
                "title": f"Bankruptcy auction property in {city_choice['name']} #{i}",
                "description": f"Distressed commercial/industrial property from bankruptcy auction",
                "address": f"{random.randint(1, 500)} Industrial Ave, {city_choice['name']}",
                "latitude": lat,
                "longitude": lon,
                "price": random.randint(200000, 5000000),  # Lower prices for auctions
                "area": random.choice([1000, 2000, 5000, 10000, 20000]),
                "deal_type": "auction",
                "land_category": random.choice(self.CATEGORIES),
                "region_id": region["id"],
                "city_id": city_choice["id"],
            }
            items.append(item)

        return items

    def normalize(self, raw: dict, source_id: int) -> Optional[LandCreate]:
        """Normalize raw auction record to LandCreate schema"""
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
                deal_type=raw.get("deal_type", "auction"),
            )
        except Exception:
            return None

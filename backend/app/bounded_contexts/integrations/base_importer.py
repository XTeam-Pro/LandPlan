"""Abstract base class for data importers"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import Land, Source, ImportJob
from app.schemas.land import LandCreate
from app.bounded_contexts.lands.service import LandsService
from app.core.logging import get_logger

logger = get_logger(__name__)


class BaseImporter(ABC):
    """Abstract base class for data importers"""

    source_type: str  # "private" | "bankruptcy" | "government"

    @abstractmethod
    def fetch_raw_data(self) -> List[dict]:
        """Fetch raw data from source. Returns list of raw item dicts."""
        pass

    @abstractmethod
    def normalize(self, raw: dict, source_id: int) -> Optional[LandCreate]:
        """Normalize raw item to LandCreate schema. Return None to skip item."""
        pass

    def run(self, db: Session, source: Source) -> ImportJob:
        """
        Full import pipeline:
        1. Create ImportJob with status "in_progress"
        2. Fetch raw data
        3. For each item:
           a. Normalize to LandCreate
           b. Check for duplicate (external_id + source_id)
           c. If new → insert with LandFeature
           d. If exists → optionally update if data changed
        4. Complete/fail ImportJob with stats
        """
        job = ImportJob(
            source_id=source.id,
            status="in_progress",
            started_at=datetime.utcnow(),
        )
        db.add(job)
        db.flush()

        try:
            # Fetch raw data
            raw_data = self.fetch_raw_data()
            job.total_items = len(raw_data)
            db.commit()

            # Process each item
            for raw_item in raw_data:
                try:
                    # Normalize
                    land_create = self.normalize(raw_item, source.id)
                    if not land_create:
                        continue

                    # Check for duplicate
                    existing = db.query(Land).filter(
                        Land.source_id == source.id,
                        Land.external_id == land_create.external_id,
                    ).first()

                    if existing:
                        job.duplicates_found += 1
                        # Optionally update if data changed
                        logger.info(f"Duplicate found: {land_create.external_id}")
                    else:
                        # Insert new land
                        LandsService.create_land(db, land_create)
                        job.imported_items += 1
                        logger.info(f"Imported land: {land_create.external_id}")

                except Exception as e:
                    job.errors += 1
                    error_msg = f"Error processing item: {str(e)}\n"
                    job.error_log = (job.error_log or "") + error_msg
                    logger.error(error_msg)
                    continue

            # Complete job
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            db.commit()

        except Exception as e:
            # Fail job
            job.status = "failed"
            job.completed_at = datetime.utcnow()
            job.error_log = f"Fatal error: {str(e)}"
            db.commit()
            logger.error(f"Import job {job.id} failed: {str(e)}")

        db.refresh(job)
        return job

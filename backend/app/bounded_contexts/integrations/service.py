"""Integration and import service"""

from typing import List
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Source, ImportJob
from app.bounded_contexts.integrations.importers.private_listings import (
    PrivateListingsImporter,
)
from app.bounded_contexts.integrations.importers.bankruptcy_auctions import (
    BankruptcyAuctionsImporter,
)
from app.bounded_contexts.integrations.importers.government_sales import (
    GovernmentSalesImporter,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class ImportService:
    """Service for managing data imports and sources"""

    IMPORTERS = {
        "private": PrivateListingsImporter,
        "bankruptcy": BankruptcyAuctionsImporter,
        "government": GovernmentSalesImporter,
    }

    @staticmethod
    def get_sources(db: Session) -> List[Source]:
        """Get all data sources"""
        return db.query(Source).order_by(Source.created_at.desc()).all()

    @staticmethod
    def get_source(db: Session, source_id: int) -> Source:
        """Get source by ID"""
        source = db.query(Source).filter(Source.id == source_id).first()

        if not source:
            raise NotFoundError("Source", source_id)

        return source

    @staticmethod
    def create_source(db: Session, data: dict) -> Source:
        """Create new data source"""
        source = Source(**data)
        db.add(source)
        db.commit()
        db.refresh(source)

        return source

    @staticmethod
    def run_import(db: Session, source_id: int) -> ImportJob:
        """
        Trigger import for a source.
        Looks up Source, picks the right importer by source.type, runs it.
        """
        source = ImportService.get_source(db, source_id)

        if source.type not in ImportService.IMPORTERS:
            raise ValueError(f"Unknown importer type: {source.type}")

        importer_class = ImportService.IMPORTERS[source.type]
        importer = importer_class()

        logger.info(f"Running import for source {source.id} ({source.type})")
        job = importer.run(db, source)

        # Update source's last_sync
        from datetime import datetime

        source.last_sync = datetime.utcnow()
        db.commit()

        logger.info(
            f"Import job {job.id} completed: "
            f"{job.imported_items} imported, "
            f"{job.duplicates_found} duplicates, "
            f"{job.errors} errors"
        )

        return job

    @staticmethod
    def get_import_jobs(db: Session, source_id: int = None) -> List[ImportJob]:
        """Get import jobs, optionally filtered by source"""
        query = db.query(ImportJob)

        if source_id is not None:
            query = query.filter(ImportJob.source_id == source_id)

        return query.order_by(ImportJob.created_at.desc()).all()

    @staticmethod
    def get_import_job(db: Session, job_id: int) -> ImportJob:
        """Get import job by ID"""
        job = db.query(ImportJob).filter(ImportJob.id == job_id).first()

        if not job:
            raise NotFoundError("ImportJob", job_id)

        return job

    @staticmethod
    def seed_default_sources(db: Session) -> List[Source]:
        """
        Create 3 default sources if none exist.
        These correspond to the 3 concrete importers.
        """
        # Check if sources already exist
        existing = db.query(Source).filter(Source.type.in_(["private", "bankruptcy", "government"])).all()
        if existing:
            logger.info("Default sources already exist, skipping seed")
            return existing

        sources_config = [
            {
                "type": "private",
                "name": "Private Listings (Mock)",
                "config": {
                    "description": "Private land listings from classifieds platforms",
                    "update_frequency": "weekly",
                },
                "is_active": True,
            },
            {
                "type": "bankruptcy",
                "name": "Bankruptcy Auctions (Mock)",
                "config": {
                    "description": "Distressed property auctions from bankruptcy proceedings",
                    "update_frequency": "biweekly",
                },
                "is_active": True,
            },
            {
                "type": "government",
                "name": "Government Sales (Mock)",
                "config": {
                    "description": "Government-owned land for public sale",
                    "update_frequency": "monthly",
                },
                "is_active": True,
            },
        ]

        created_sources = []
        for config in sources_config:
            source = ImportService.create_source(db, config)
            created_sources.append(source)
            logger.info(f"Created source: {source.name} ({source.type})")

        return created_sources

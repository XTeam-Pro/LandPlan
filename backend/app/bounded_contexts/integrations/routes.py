"""Admin import API routes"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.bounded_contexts.integrations.service import ImportService
from app.db.session import get_db
from app.schemas.importer import (
    SourceResponse,
    SourceCreate,
    ImportJobResponse,
    ImportRunResponse,
)

router = APIRouter(prefix="/api/v1/admin/imports", tags=["Admin - Imports"])


@router.get(
    "/sources",
    response_model=list[SourceResponse],
    status_code=status.HTTP_200_OK,
    summary="List data sources",
    description="Get all available data sources for import",
)
async def list_sources(db: Session = Depends(get_db)):
    """
    List all configured data sources.

    **Returns:**
    - List of source configurations
    - Each includes source type, name, config, and last sync timestamp
    """
    sources = ImportService.get_sources(db)
    return [SourceResponse.from_orm(s) for s in sources]


@router.post(
    "/sources",
    response_model=SourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create data source",
    description="Create a new data source configuration",
)
async def create_source(
    source_data: SourceCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new data source.

    **Parameters:**
    - **type**: Source type (private, bankruptcy, government)
    - **name**: Human-readable name
    - **config**: Configuration metadata (JSON)
    - **is_active**: Whether source is active

    **Returns:**
    - Created source with ID
    """
    source = ImportService.create_source(db, source_data.dict())
    return SourceResponse.from_orm(source)


@router.get(
    "/sources/{source_id}",
    response_model=SourceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get source details",
    description="Get details of a specific data source",
)
async def get_source(
    source_id: int,
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a source.

    **Parameters:**
    - **source_id**: ID of the source

    **Returns:**
    - Source configuration and metadata
    """
    source = ImportService.get_source(db, source_id)
    return SourceResponse.from_orm(source)


@router.post(
    "/sources/{source_id}/run",
    response_model=ImportRunResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Trigger import job",
    description="Start an import job for a data source immediately",
)
async def trigger_import(
    source_id: int,
    db: Session = Depends(get_db),
):
    """
    Trigger an import job for a source.
    This will fetch data, normalize it, check for duplicates, and insert new items.

    **Parameters:**
    - **source_id**: ID of the source to import

    **Returns:**
    - Import job with ID and initial stats
    """
    job = ImportService.run_import(db, source_id)
    return ImportRunResponse.from_orm(job)


@router.get(
    "/import-jobs",
    response_model=list[ImportJobResponse],
    status_code=status.HTTP_200_OK,
    summary="List import jobs",
    description="Get all import jobs (newest first)",
)
async def list_import_jobs(
    source_id: int = None,
    db: Session = Depends(get_db),
):
    """
    List all import jobs.

    **Query Parameters:**
    - **source_id**: Optional filter by source ID

    **Returns:**
    - List of import jobs with stats, ordered by creation time (newest first)
    """
    jobs = ImportService.get_import_jobs(db, source_id)
    return [ImportJobResponse.from_orm(j) for j in jobs]


@router.get(
    "/import-jobs/{job_id}",
    response_model=ImportJobResponse,
    status_code=status.HTTP_200_OK,
    summary="Get import job details",
    description="Get detailed information about an import job",
)
async def get_import_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    """
    Get detailed information about an import job.

    **Parameters:**
    - **job_id**: ID of the import job

    **Returns:**
    - Job details including:
      - status (pending, in_progress, completed, failed)
      - imported_items, duplicates_found, errors counts
      - start and completion times
      - error log (if any)
    """
    job = ImportService.get_import_job(db, job_id)
    return ImportJobResponse.from_orm(job)

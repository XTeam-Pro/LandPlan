"""Importer-related Pydantic schemas"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class SourceCreate(BaseModel):
    """Source creation schema"""

    type: str  # private, bankruptcy, government
    name: str
    config: Optional[Dict[str, Any]] = {}
    is_active: bool = True


class SourceResponse(BaseModel):
    """Source response schema"""

    id: int
    type: str
    name: str
    config: Dict[str, Any]
    is_active: bool
    last_sync: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ImportJobResponse(BaseModel):
    """Import job response schema"""

    id: int
    source_id: int
    status: str  # pending, in_progress, completed, failed
    total_items: int
    imported_items: int
    duplicates_found: int
    errors: int
    error_log: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ImportRunResponse(BaseModel):
    """Import run trigger response"""

    id: int
    source_id: int
    status: str
    total_items: int
    imported_items: int
    duplicates_found: int
    errors: int
    started_at: Optional[datetime] = None

    class Config:
        from_attributes = True

"""Integration tests for import endpoints"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Source, ImportJob, Land
from app.bounded_contexts.integrations.service import ImportService


class TestImportEndpoints:
    """Integration tests for admin import endpoints"""

    @pytest.fixture
    def setup_sources(self, db_session: Session):
        """Setup: Create test sources"""
        sources = ImportService.seed_default_sources(db_session)
        return {s.id: s for s in sources}

    def test_list_sources(self, client: TestClient, setup_sources):
        """Test listing data sources"""
        response = client.get("/api/v1/admin/imports/sources")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(s["type"] in ["private", "bankruptcy", "government"] for s in data)

    def test_get_source(self, client: TestClient, setup_sources):
        """Test getting a specific source"""
        source_id = list(setup_sources.keys())[0]
        response = client.get(f"/api/v1/admin/imports/sources/{source_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == source_id
        assert data["type"] in ["private", "bankruptcy", "government"]

    def test_get_source_not_found(self, client: TestClient):
        """Test getting non-existent source"""
        response = client.get("/api/v1/admin/imports/sources/999")

        assert response.status_code == 404

    def test_create_source(self, client: TestClient):
        """Test creating a new source"""
        source_data = {
            "type": "test_source",
            "name": "Test Source",
            "config": {"test": "config"},
            "is_active": True,
        }
        response = client.post("/api/v1/admin/imports/sources", json=source_data)

        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "test_source"
        assert data["name"] == "Test Source"
        assert data["is_active"] is True

    def test_trigger_import_private_listings(self, client: TestClient, setup_sources):
        """Test triggering private listings import"""
        private_source_id = [
            s for s, src in setup_sources.items() if src.type == "private"
        ][0]

        response = client.post(
            f"/api/v1/admin/imports/sources/{private_source_id}/run"
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "completed"
        assert data["total_items"] == 50
        assert data["imported_items"] == 50
        assert data["duplicates_found"] == 0

    def test_trigger_import_bankruptcy_auctions(self, client: TestClient, setup_sources):
        """Test triggering bankruptcy auctions import"""
        bankruptcy_source_id = [
            s for s, src in setup_sources.items() if src.type == "bankruptcy"
        ][0]

        response = client.post(
            f"/api/v1/admin/imports/sources/{bankruptcy_source_id}/run"
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "completed"
        assert data["total_items"] == 20
        assert data["imported_items"] == 20

    def test_trigger_import_government_sales(self, client: TestClient, setup_sources):
        """Test triggering government sales import"""
        government_source_id = [
            s for s, src in setup_sources.items() if src.type == "government"
        ][0]

        response = client.post(
            f"/api/v1/admin/imports/sources/{government_source_id}/run"
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "completed"
        assert data["total_items"] == 30
        assert data["imported_items"] == 30

    def test_deduplication_same_source(
        self, client: TestClient, setup_sources, db_session: Session
    ):
        """Test deduplication when running same import twice"""
        private_source_id = [
            s for s, src in setup_sources.items() if src.type == "private"
        ][0]

        # First import
        response1 = client.post(
            f"/api/v1/admin/imports/sources/{private_source_id}/run"
        )
        assert response1.status_code == 201
        data1 = response1.json()
        assert data1["imported_items"] == 50
        assert data1["duplicates_found"] == 0

        # Second import (same source)
        response2 = client.post(
            f"/api/v1/admin/imports/sources/{private_source_id}/run"
        )
        assert response2.status_code == 201
        data2 = response2.json()
        assert data2["imported_items"] == 0  # All duplicates
        assert data2["duplicates_found"] == 50

        # Verify total lands in DB is still 50
        total_lands = db_session.query(Land).count()
        assert total_lands == 50

    def test_list_import_jobs(self, client: TestClient, setup_sources):
        """Test listing import jobs"""
        private_source_id = [
            s for s, src in setup_sources.items() if src.type == "private"
        ][0]

        # Trigger import
        client.post(f"/api/v1/admin/imports/sources/{private_source_id}/run")

        # List jobs
        response = client.get("/api/v1/admin/imports/import-jobs")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["status"] == "completed"
        assert data[0]["source_id"] == private_source_id

    def test_list_import_jobs_filtered_by_source(
        self, client: TestClient, setup_sources
    ):
        """Test listing import jobs filtered by source"""
        private_source_id = [
            s for s, src in setup_sources.items() if src.type == "private"
        ][0]
        bankruptcy_source_id = [
            s for s, src in setup_sources.items() if src.type == "bankruptcy"
        ][0]

        # Trigger both imports
        client.post(f"/api/v1/admin/imports/sources/{private_source_id}/run")
        client.post(f"/api/v1/admin/imports/sources/{bankruptcy_source_id}/run")

        # Filter by private source
        response = client.get(
            f"/api/v1/admin/imports/import-jobs?source_id={private_source_id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert all(j["source_id"] == private_source_id for j in data)

    def test_get_import_job(self, client: TestClient, setup_sources, db_session: Session):
        """Test getting import job details"""
        private_source_id = [
            s for s, src in setup_sources.items() if src.type == "private"
        ][0]

        # Trigger import
        response = client.post(
            f"/api/v1/admin/imports/sources/{private_source_id}/run"
        )
        job_id = response.json()["id"]

        # Get job details
        response = client.get(f"/api/v1/admin/imports/import-jobs/{job_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id
        assert data["status"] == "completed"
        assert data["source_id"] == private_source_id
        assert data["imported_items"] == 50
        assert data["duplicates_found"] == 0
        assert data["errors"] == 0

    def test_get_import_job_not_found(self, client: TestClient):
        """Test getting non-existent import job"""
        response = client.get("/api/v1/admin/imports/import-jobs/999")

        assert response.status_code == 404

    def test_imported_lands_are_queryable(
        self, client: TestClient, setup_sources, db_session: Session
    ):
        """Test that imported lands appear in the lands API"""
        private_source_id = [
            s for s, src in setup_sources.items() if src.type == "private"
        ][0]

        # Trigger import
        client.post(f"/api/v1/admin/imports/sources/{private_source_id}/run")

        # Query lands API
        response = client.get("/api/v1/lands")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 50
        assert len(data["items"]) > 0

    def test_imported_lands_have_correct_source(
        self, client: TestClient, setup_sources
    ):
        """Test that imported lands have correct source_id"""
        private_source_id = [
            s for s, src in setup_sources.items() if src.type == "private"
        ][0]

        # Trigger import
        client.post(f"/api/v1/admin/imports/sources/{private_source_id}/run")

        # Query lands and verify source
        response = client.get("/api/v1/lands")
        data = response.json()

        # Get first land detail to check source_id
        if data["items"]:
            land_id = data["items"][0]["id"]
            land_detail_response = client.get(f"/api/v1/lands/{land_id}")
            assert land_detail_response.status_code == 200
            land_detail = land_detail_response.json()
            assert land_detail["source_id"] == private_source_id

    def test_all_three_imports_run_independently(
        self, client: TestClient, setup_sources, db_session: Session
    ):
        """Test running all three importers and verifying totals"""
        # Get source IDs
        sources_by_type = {src.type: sid for sid, src in setup_sources.items()}

        # Run all imports
        private_response = client.post(
            f"/api/v1/admin/imports/sources/{sources_by_type['private']}/run"
        )
        bankruptcy_response = client.post(
            f"/api/v1/admin/imports/sources/{sources_by_type['bankruptcy']}/run"
        )
        government_response = client.post(
            f"/api/v1/admin/imports/sources/{sources_by_type['government']}/run"
        )

        assert private_response.status_code == 201
        assert bankruptcy_response.status_code == 201
        assert government_response.status_code == 201

        # Verify counts
        private_data = private_response.json()
        bankruptcy_data = bankruptcy_response.json()
        government_data = government_response.json()

        assert private_data["imported_items"] == 50
        assert bankruptcy_data["imported_items"] == 20
        assert government_data["imported_items"] == 30

        # Total lands in DB should be 100
        total_lands = db_session.query(Land).count()
        assert total_lands == 100

        # Query lands API should return all 100
        response = client.get("/api/v1/lands")
        data = response.json()
        assert data["total"] == 100

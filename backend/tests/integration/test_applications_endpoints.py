"""Integration tests for applications endpoints"""

import pytest
from fastapi.testclient import TestClient


class TestApplicationsEndpoints:
    """Integration tests for applications endpoints"""

    @pytest.fixture
    def setup_data(self, client: TestClient, user_data):
        """Setup: Create user, land, service, and company"""
        # Register user
        user_response = client.post("/api/v1/auth/register", json=user_data)
        user_id = user_response.json()["id"]

        # Login user
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
        )
        access_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # Create land
        land_data = {
            "title": "Test Land",
            "address": "123 Test St",
            "region": "Test Region",
            "city": "Test City",
            "price": 100000.0,
            "area": 1000.0,
            "coordinates": {"lat": 55.75, "lng": 37.62},
            "deal_type": "purchase",
            "source_id": 1,
        }
        land_response = client.post("/api/v1/lands", json=land_data, headers=headers)
        land_id = land_response.json()["id"]

        # Create service
        service_data = {
            "name": "Test Service",
            "category_id": 1,
            "priority": "CRITICAL",
        }
        service_response = client.post("/api/v1/services", json=service_data, headers=headers)
        service_id = service_response.json()["id"]

        # Create company user
        company_user_data = {
            "email": "company@example.com",
            "password": "Company@1234567",
            "full_name": "Company User",
            "role": "company",
        }
        company_user_response = client.post("/api/v1/auth/register", json=company_user_data)
        company_user_id = company_user_response.json()["id"]

        # Create company
        company_data = {
            "public_name": "Test Company",
            "legal_name": "Test Company LLC",
            "contact_email": "company@company.com",
            "contact_phone": "+1234567890",
            "owner_user_id": company_user_id,
        }
        company_response = client.post("/api/v1/companies", json=company_data, headers=headers)
        company_id = company_response.json()["id"]

        return {
            "user_id": user_id,
            "land_id": land_id,
            "service_id": service_id,
            "company_id": company_id,
            "access_token": access_token,
            "headers": headers,
        }

    def test_create_application(self, client: TestClient, setup_data):
        """Test creating an application"""
        app_data = {
            "land_id": setup_data["land_id"],
            "service_id": setup_data["service_id"],
            "company_id": setup_data["company_id"],
            "message": "I would like to use your services for this land",
        }
        response = client.post(
            "/api/v1/applications",
            json=app_data,
            headers=setup_data["headers"],
        )

        assert response.status_code == 201
        data = response.json()
        assert data["land_id"] == setup_data["land_id"]
        assert data["service_id"] == setup_data["service_id"]
        assert data["company_id"] == setup_data["company_id"]
        assert data["status"] == "pending"
        assert data["user_id"] == setup_data["user_id"]

    def test_create_duplicate_application_rejected(self, client: TestClient, setup_data):
        """Test that duplicate applications are rejected"""
        app_data = {
            "land_id": setup_data["land_id"],
            "service_id": setup_data["service_id"],
            "company_id": setup_data["company_id"],
        }

        # Create first application
        response1 = client.post(
            "/api/v1/applications",
            json=app_data,
            headers=setup_data["headers"],
        )
        assert response1.status_code == 201

        # Try to create duplicate
        response2 = client.post(
            "/api/v1/applications",
            json=app_data,
            headers=setup_data["headers"],
        )
        assert response2.status_code == 409  # Conflict

    def test_get_user_applications(self, client: TestClient, setup_data):
        """Test retrieving applications for a user"""
        # Create application
        app_data = {
            "land_id": setup_data["land_id"],
            "service_id": setup_data["service_id"],
            "company_id": setup_data["company_id"],
        }
        create_response = client.post(
            "/api/v1/applications",
            json=app_data,
            headers=setup_data["headers"],
        )
        assert create_response.status_code == 201

        # Get applications
        response = client.get(
            "/api/v1/applications",
            headers=setup_data["headers"],
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 1
        assert len(data["items"]) == 1

    def test_get_application_by_id(self, client: TestClient, setup_data):
        """Test retrieving a specific application"""
        # Create application
        app_data = {
            "land_id": setup_data["land_id"],
            "service_id": setup_data["service_id"],
            "company_id": setup_data["company_id"],
        }
        create_response = client.post(
            "/api/v1/applications",
            json=app_data,
            headers=setup_data["headers"],
        )
        app_id = create_response.json()["id"]

        # Get application details
        response = client.get(f"/api/v1/applications/{app_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == app_id
        assert data["status"] == "pending"

    def test_update_application_status(self, client: TestClient, setup_data):
        """Test updating application status"""
        # Create application
        app_data = {
            "land_id": setup_data["land_id"],
            "service_id": setup_data["service_id"],
            "company_id": setup_data["company_id"],
        }
        create_response = client.post(
            "/api/v1/applications",
            json=app_data,
            headers=setup_data["headers"],
        )
        app_id = create_response.json()["id"]

        # Update status
        update_data = {"status": "accepted"}
        response = client.patch(
            f"/api/v1/applications/{app_id}/status",
            json=update_data,
            headers=setup_data["headers"],
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"

    def test_application_status_workflow(self, client: TestClient, setup_data):
        """Test complete application status workflow"""
        # Create application
        app_data = {
            "land_id": setup_data["land_id"],
            "service_id": setup_data["service_id"],
            "company_id": setup_data["company_id"],
        }
        create_response = client.post(
            "/api/v1/applications",
            json=app_data,
            headers=setup_data["headers"],
        )
        app_id = create_response.json()["id"]

        # pending -> accepted
        response = client.patch(
            f"/api/v1/applications/{app_id}/status",
            json={"status": "accepted"},
            headers=setup_data["headers"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == "accepted"

        # accepted -> in_progress
        response = client.patch(
            f"/api/v1/applications/{app_id}/status",
            json={"status": "in_progress"},
            headers=setup_data["headers"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"

        # in_progress -> completed
        response = client.patch(
            f"/api/v1/applications/{app_id}/status",
            json={"status": "completed"},
            headers=setup_data["headers"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    def test_cannot_update_completed_application(self, client: TestClient, setup_data):
        """Test that completed applications cannot be changed"""
        # Create and complete application
        app_data = {
            "land_id": setup_data["land_id"],
            "service_id": setup_data["service_id"],
            "company_id": setup_data["company_id"],
        }
        create_response = client.post(
            "/api/v1/applications",
            json=app_data,
            headers=setup_data["headers"],
        )
        app_id = create_response.json()["id"]

        # Complete it
        client.patch(
            f"/api/v1/applications/{app_id}/status",
            json={"status": "completed"},
            headers=setup_data["headers"],
        )

        # Try to change completed application
        response = client.patch(
            f"/api/v1/applications/{app_id}/status",
            json={"status": "pending"},
            headers=setup_data["headers"],
        )
        assert response.status_code == 422  # Validation error

    def test_get_application_stats(self, client: TestClient, setup_data):
        """Test getting application statistics"""
        # Create multiple applications with different statuses
        app_data = {
            "land_id": setup_data["land_id"],
            "service_id": setup_data["service_id"],
            "company_id": setup_data["company_id"],
        }
        create_response = client.post(
            "/api/v1/applications",
            json=app_data,
            headers=setup_data["headers"],
        )
        assert create_response.status_code == 201

        # Get stats
        response = client.get(
            "/api/v1/applications/stats",
            headers=setup_data["headers"],
        )
        assert response.status_code == 200
        stats = response.json()
        assert "total" in stats
        assert "pending" in stats
        assert "accepted" in stats
        assert stats["total"] == 1
        assert stats["pending"] == 1

    def test_filter_applications_by_status(self, client: TestClient, setup_data):
        """Test filtering applications by status"""
        # Create application
        app_data = {
            "land_id": setup_data["land_id"],
            "service_id": setup_data["service_id"],
            "company_id": setup_data["company_id"],
        }
        client.post(
            "/api/v1/applications",
            json=app_data,
            headers=setup_data["headers"],
        )

        # Filter by pending status
        response = client.get(
            "/api/v1/applications?status_filter=pending",
            headers=setup_data["headers"],
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

        # Filter by rejected status (should be empty)
        response = client.get(
            "/api/v1/applications?status_filter=rejected",
            headers=setup_data["headers"],
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

"""Integration tests for reviews endpoints"""

import pytest
from fastapi.testclient import TestClient


class TestReviewsEndpoints:
    """Integration tests for reviews endpoints"""

    @pytest.fixture
    def setup_data(self, client: TestClient, user_data):
        """Setup: Create users and company"""
        # Register regular user
        user_response = client.post("/api/v1/auth/register", json=user_data)
        user_id = user_response.json()["id"]

        # Login user
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
        )
        access_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

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
            "company_id": company_id,
            "access_token": access_token,
            "headers": headers,
        }

    def test_create_review(self, client: TestClient, setup_data):
        """Test creating a review"""
        review_data = {
            "rating": 4.5,
            "text": "Great service, very professional",
        }
        response = client.post(
            f"/api/v1/companies/{setup_data['company_id']}/reviews",
            json=review_data,
            headers=setup_data["headers"],
        )

        assert response.status_code == 201
        data = response.json()
        assert data["rating"] == 4.5
        assert data["text"] == "Great service, very professional"
        assert data["status"] == "pending"
        assert data["company_id"] == setup_data["company_id"]
        assert data["user_id"] == setup_data["user_id"]

    def test_create_review_with_rating_only(self, client: TestClient, setup_data):
        """Test creating a review with just a rating"""
        review_data = {
            "rating": 5.0,
        }
        response = client.post(
            f"/api/v1/companies/{setup_data['company_id']}/reviews",
            json=review_data,
            headers=setup_data["headers"],
        )

        assert response.status_code == 201
        data = response.json()
        assert data["rating"] == 5.0
        assert data["text"] is None

    def test_create_duplicate_review_rejected(self, client: TestClient, setup_data):
        """Test that duplicate reviews are rejected"""
        review_data = {
            "rating": 4.0,
            "text": "Good service",
        }

        # Create first review
        response1 = client.post(
            f"/api/v1/companies/{setup_data['company_id']}/reviews",
            json=review_data,
            headers=setup_data["headers"],
        )
        assert response1.status_code == 201

        # Try to create duplicate
        response2 = client.post(
            f"/api/v1/companies/{setup_data['company_id']}/reviews",
            json=review_data,
            headers=setup_data["headers"],
        )
        assert response2.status_code == 409  # Conflict

    def test_get_company_reviews_and_stats(self, client: TestClient, setup_data):
        """Test retrieving reviews and stats for a company"""
        # Create review
        review_data = {
            "rating": 4.5,
            "text": "Excellent work",
        }
        client.post(
            f"/api/v1/companies/{setup_data['company_id']}/reviews",
            json=review_data,
            headers=setup_data["headers"],
        )

        # Get reviews
        response = client.get(
            f"/api/v1/companies/{setup_data['company_id']}/reviews",
        )

        assert response.status_code == 200
        data = response.json()
        assert "reviews" in data
        assert "stats" in data

    def test_update_review(self, client: TestClient, setup_data):
        """Test updating own review"""
        # Create review
        review_data = {
            "rating": 3.0,
            "text": "Average service",
        }
        create_response = client.post(
            f"/api/v1/companies/{setup_data['company_id']}/reviews",
            json=review_data,
            headers=setup_data["headers"],
        )
        review_id = create_response.json()["id"]

        # Update review
        update_data = {
            "rating": 4.5,
            "text": "Actually better than I thought",
        }
        response = client.patch(
            f"/api/v1/reviews/{review_id}",
            json=update_data,
            headers=setup_data["headers"],
        )

        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == 4.5
        assert data["text"] == "Actually better than I thought"
        # Should reset to pending after update
        assert data["status"] == "pending"

    def test_update_review_partial(self, client: TestClient, setup_data):
        """Test partially updating a review (only rating)"""
        # Create review
        review_data = {
            "rating": 2.0,
            "text": "Not great",
        }
        create_response = client.post(
            f"/api/v1/companies/{setup_data['company_id']}/reviews",
            json=review_data,
            headers=setup_data["headers"],
        )
        review_id = create_response.json()["id"]

        # Update only rating
        update_data = {
            "rating": 5.0,
        }
        response = client.patch(
            f"/api/v1/reviews/{review_id}",
            json=update_data,
            headers=setup_data["headers"],
        )

        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == 5.0
        assert data["text"] == "Not great"  # Unchanged

    def test_delete_review(self, client: TestClient, setup_data):
        """Test deleting own review"""
        # Create review
        review_data = {
            "rating": 3.0,
            "text": "Remove this",
        }
        create_response = client.post(
            f"/api/v1/companies/{setup_data['company_id']}/reviews",
            json=review_data,
            headers=setup_data["headers"],
        )
        review_id = create_response.json()["id"]

        # Delete review
        response = client.delete(
            f"/api/v1/reviews/{review_id}",
            headers=setup_data["headers"],
        )

        assert response.status_code == 200
        assert "message" in response.json()

    def test_cannot_update_other_users_review(self, client: TestClient, user_data):
        """Test that users cannot update other users' reviews"""
        # Create two users
        user1_response = client.post("/api/v1/auth/register", json=user_data)
        user1_id = user1_response.json()["id"]

        user2_data = {
            "email": "user2@example.com",
            "password": "User2@1234567",
            "full_name": "User Two",
        }
        client.post("/api/v1/auth/register", json=user2_data)

        # Create company
        company_user_data = {
            "email": "company@example.com",
            "password": "Company@1234567",
            "full_name": "Company User",
            "role": "company",
        }
        company_user_response = client.post("/api/v1/auth/register", json=company_user_data)
        company_user_id = company_user_response.json()["id"]

        company_data = {
            "public_name": "Test Company",
            "legal_name": "Test Company LLC",
            "contact_email": "company@company.com",
            "contact_phone": "+1234567890",
            "owner_user_id": company_user_id,
        }

        # Login as user1
        login1 = client.post(
            "/api/v1/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
        )
        token1 = login1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        company_response = client.post("/api/v1/companies", json=company_data, headers=headers1)
        company_id = company_response.json()["id"]

        # User1 creates review
        review_data = {
            "rating": 4.0,
            "text": "User1's review",
        }
        create_response = client.post(
            f"/api/v1/companies/{company_id}/reviews",
            json=review_data,
            headers=headers1,
        )
        review_id = create_response.json()["id"]

        # Login as user2
        login2 = client.post(
            "/api/v1/auth/login",
            json={"email": user2_data["email"], "password": user2_data["password"]},
        )
        token2 = login2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # User2 tries to update user1's review
        update_data = {
            "rating": 1.0,
        }
        response = client.patch(
            f"/api/v1/reviews/{review_id}",
            json=update_data,
            headers=headers2,
        )
        assert response.status_code == 422  # Validation error

    def test_cannot_delete_other_users_review(self, client: TestClient, user_data):
        """Test that users cannot delete other users' reviews"""
        # Create two users
        user1_response = client.post("/api/v1/auth/register", json=user_data)

        user2_data = {
            "email": "user2@example.com",
            "password": "User2@1234567",
            "full_name": "User Two",
        }
        client.post("/api/v1/auth/register", json=user2_data)

        # Create company
        company_user_data = {
            "email": "company@example.com",
            "password": "Company@1234567",
            "full_name": "Company User",
            "role": "company",
        }
        company_user_response = client.post("/api/v1/auth/register", json=company_user_data)
        company_user_id = company_user_response.json()["id"]

        company_data = {
            "public_name": "Test Company",
            "legal_name": "Test Company LLC",
            "contact_email": "company@company.com",
            "contact_phone": "+1234567890",
            "owner_user_id": company_user_id,
        }

        # Login as user1
        login1 = client.post(
            "/api/v1/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
        )
        token1 = login1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        company_response = client.post("/api/v1/companies", json=company_data, headers=headers1)
        company_id = company_response.json()["id"]

        # User1 creates review
        review_data = {
            "rating": 4.0,
            "text": "User1's review",
        }
        create_response = client.post(
            f"/api/v1/companies/{company_id}/reviews",
            json=review_data,
            headers=headers1,
        )
        review_id = create_response.json()["id"]

        # Login as user2
        login2 = client.post(
            "/api/v1/auth/login",
            json={"email": user2_data["email"], "password": user2_data["password"]},
        )
        token2 = login2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # User2 tries to delete user1's review
        response = client.delete(
            f"/api/v1/reviews/{review_id}",
            headers=headers2,
        )
        assert response.status_code == 422  # Validation error

    def test_review_validation_rating_range(self, client: TestClient, setup_data):
        """Test review rating validation"""
        # Rating too low
        review_data = {
            "rating": 0.5,
        }
        response = client.post(
            f"/api/v1/companies/{setup_data['company_id']}/reviews",
            json=review_data,
            headers=setup_data["headers"],
        )
        assert response.status_code == 422

        # Rating too high
        review_data = {
            "rating": 5.5,
        }
        response = client.post(
            f"/api/v1/companies/{setup_data['company_id']}/reviews",
            json=review_data,
            headers=setup_data["headers"],
        )
        assert response.status_code == 422

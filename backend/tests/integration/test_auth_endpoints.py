"""Integration tests for auth endpoints"""

import pytest
from fastapi.testclient import TestClient


class TestAuthEndpoints:
    """Integration tests for authentication endpoints"""

    def test_full_auth_flow(self, client: TestClient, user_data):
        """Test complete authentication flow: register -> login -> refresh"""

        # Step 1: Register
        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201
        register_data = register_response.json()
        user_id = register_data["id"]

        # Step 2: Login
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"],
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        tokens = login_response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        # Step 3: Get current user with access token
        headers = {"Authorization": f"Bearer {access_token}"}
        me_response = client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["id"] == user_id
        assert me_data["email"] == user_data["email"]

        # Step 4: Refresh token
        refresh_response = client.post(
            "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        new_access_token = new_tokens["access_token"]

        # Step 5: Use new access token
        new_headers = {"Authorization": f"Bearer {new_access_token}"}
        me_response2 = client.get("/api/v1/auth/me", headers=new_headers)
        assert me_response2.status_code == 200
        assert me_response2.json()["id"] == user_id

    def test_register_with_company_role(self, client: TestClient, company_user_data):
        """Test registering a company user"""
        response = client.post("/api/v1/auth/register", json=company_user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "company"

    def test_access_protected_endpoint_without_token(self, client: TestClient):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403

    def test_access_protected_endpoint_with_invalid_token(
        self, client: TestClient
    ):
        """Test accessing protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

    def test_multiple_users_isolation(self, client: TestClient):
        """Test that multiple users don't see each other's data"""
        user1 = {
            "email": "user1@example.com",
            "password": "Password123",
            "full_name": "User One",
        }
        user2 = {
            "email": "user2@example.com",
            "password": "Password123",
            "full_name": "User Two",
        }

        # Register both users
        client.post("/api/v1/auth/register", json=user1)
        client.post("/api/v1/auth/register", json=user2)

        # Login as user1
        login1 = client.post(
            "/api/v1/auth/login",
            json={"email": user1["email"], "password": user1["password"]},
        )
        token1 = login1.json()["access_token"]

        # Login as user2
        login2 = client.post(
            "/api/v1/auth/login",
            json={"email": user2["email"], "password": user2["password"]},
        )
        token2 = login2.json()["access_token"]

        # User1 should see their own data
        headers1 = {"Authorization": f"Bearer {token1}"}
        me1 = client.get("/api/v1/auth/me", headers=headers1).json()
        assert me1["email"] == user1["email"]

        # User2 should see their own data
        headers2 = {"Authorization": f"Bearer {token2}"}
        me2 = client.get("/api/v1/auth/me", headers=headers2).json()
        assert me2["email"] == user2["email"]

        # Confirm they're different
        assert me1["id"] != me2["id"]

    def test_error_responses_have_correct_format(self, client: TestClient):
        """Test that error responses follow the expected format"""
        # Test 409 conflict error
        user_data = {
            "email": "duplicate@example.com",
            "password": "Password123",
        }
        client.post("/api/v1/auth/register", json=user_data)
        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 409
        data = response.json()
        assert "error" in data
        assert "code" in data

    def test_password_validation(self, client: TestClient):
        """Test password validation rules"""
        # Test weak password (< 8 chars)
        weak_password = {
            "email": "weak@example.com",
            "password": "short",
        }
        response = client.post("/api/v1/auth/register", json=weak_password)
        assert response.status_code == 422

    def test_email_validation(self, client: TestClient):
        """Test email validation"""
        # Test invalid email format
        invalid_email = {
            "email": "not-an-email",
            "password": "Password123",
        }
        response = client.post("/api/v1/auth/register", json=invalid_email)
        assert response.status_code == 422

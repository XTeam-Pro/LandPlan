"""Tests for authentication API"""

import pytest
from sqlalchemy.orm import Session

from app.bounded_contexts.identity_access.service import AuthService
from app.core.exceptions import ValidationError, ConflictError, AuthenticationException
from app.models import User
from app.schemas.user import UserCreate, UserLogin


class TestAuthService:
    """Tests for AuthService"""

    def test_register_new_user(self, db_session: Session, user_data):
        """Test user registration"""
        user_create = UserCreate(**user_data)
        result = AuthService.register(db_session, user_create)

        assert result["email"] == user_data["email"]
        assert result["role"] == "user"

        # Verify user created in database
        user = db_session.query(User).filter(User.email == user_data["email"]).first()
        assert user is not None
        assert user.full_name == user_data["full_name"]

    def test_register_duplicate_email(self, db_session: Session, user_data):
        """Test registering with existing email"""
        user_create = UserCreate(**user_data)
        AuthService.register(db_session, user_create)

        # Try to register same email again
        with pytest.raises(ConflictError):
            AuthService.register(db_session, user_create)

    def test_register_weak_password(self, db_session: Session, user_data):
        """Test registration with weak password"""
        user_data["password"] = "short"
        user_create = UserCreate(**user_data)

        with pytest.raises(ValidationError):
            AuthService.register(db_session, user_create)

    def test_login_success(self, db_session: Session, user_data):
        """Test successful login"""
        # Register user first
        user_create = UserCreate(**user_data)
        AuthService.register(db_session, user_create)

        # Login
        login_data = UserLogin(email=user_data["email"], password=user_data["password"])
        tokens = AuthService.login(db_session, login_data)

        assert tokens.access_token
        assert tokens.refresh_token
        assert tokens.token_type == "bearer"

    def test_login_invalid_email(self, db_session: Session):
        """Test login with non-existent email"""
        login_data = UserLogin(email="nonexistent@example.com", password="password")

        with pytest.raises(AuthenticationException):
            AuthService.login(db_session, login_data)

    def test_login_invalid_password(self, db_session: Session, user_data):
        """Test login with wrong password"""
        # Register user first
        user_create = UserCreate(**user_data)
        AuthService.register(db_session, user_create)

        # Try login with wrong password
        login_data = UserLogin(email=user_data["email"], password="WrongPassword123")

        with pytest.raises(AuthenticationException):
            AuthService.login(db_session, login_data)

    def test_login_inactive_user(self, db_session: Session, user_data):
        """Test login with inactive user"""
        # Register user
        user_create = UserCreate(**user_data)
        AuthService.register(db_session, user_create)

        # Mark user as inactive
        user = db_session.query(User).filter(User.email == user_data["email"]).first()
        user.status = "inactive"
        db_session.commit()

        # Try to login
        login_data = UserLogin(email=user_data["email"], password=user_data["password"])

        with pytest.raises(AuthenticationException):
            AuthService.login(db_session, login_data)

    def test_refresh_token(self, db_session: Session, user_data):
        """Test token refresh"""
        # Register and login
        user_create = UserCreate(**user_data)
        AuthService.register(db_session, user_create)

        login_data = UserLogin(email=user_data["email"], password=user_data["password"])
        tokens = AuthService.login(db_session, login_data)

        # Refresh token
        new_tokens = AuthService.refresh_access_token(tokens.refresh_token)

        assert new_tokens.access_token
        assert new_tokens.refresh_token
        assert new_tokens.access_token != tokens.access_token

    def test_get_user(self, db_session: Session, user_data):
        """Test getting user by ID"""
        # Register user
        user_create = UserCreate(**user_data)
        result = AuthService.register(db_session, user_create)
        user_id = result["id"]

        # Get user
        user = AuthService.get_user(db_session, user_id)

        assert user.id == user_id
        assert user.email == user_data["email"]

    def test_get_user_not_found(self, db_session: Session):
        """Test getting non-existent user"""
        with pytest.raises(ValidationError):
            AuthService.get_user(db_session, 999)


class TestAuthAPI:
    """Tests for Auth API endpoints"""

    def test_register_endpoint(self, client, user_data):
        """Test registration endpoint"""
        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["role"] == "user"

    def test_register_endpoint_duplicate(self, client, user_data):
        """Test registration with duplicate email"""
        # Register first user
        response1 = client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == 201

        # Try to register same email again
        response2 = client.post("/api/v1/auth/register", json=user_data)
        assert response2.status_code == 409

    def test_login_endpoint(self, client, user_data):
        """Test login endpoint"""
        # Register first
        client.post("/api/v1/auth/register", json=user_data)

        # Login
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"],
        }
        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_endpoint_invalid(self, client, user_data):
        """Test login with invalid credentials"""
        # Register first
        client.post("/api/v1/auth/register", json=user_data)

        # Try wrong password
        login_data = {
            "email": user_data["email"],
            "password": "WrongPassword123",
        }
        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401

    def test_refresh_endpoint(self, client, user_data):
        """Test refresh token endpoint"""
        # Register and login
        client.post("/api/v1/auth/register", json=user_data)

        login_data = {
            "email": user_data["email"],
            "password": user_data["password"],
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        refresh_token = login_response.json()["refresh_token"]

        # Refresh
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

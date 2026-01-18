import pytest
from fastapi import status


class TestUserRegistration:
    """Test user registration functionality"""

    def test_create_user_success(self, client):
        """Test successful user creation"""
        response = client.post(
            "/users/",
            json={
                "email": "newuser@example.com",
                "name": "New User",
                "password": "securepassword123"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert "id" in data
        assert "hashed_password" not in data

    def test_create_user_duplicate_email(self, client, test_user):
        """Test creating user with duplicate email fails"""
        response = client.post(
            "/users/",
            json={
                "email": test_user.email,
                "name": "Another User",
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()

    def test_create_user_invalid_email(self, client):
        """Test creating user with invalid email format"""
        response = client.post(
            "/users/",
            json={
                "email": "not-an-email",
                "name": "Test User",
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_missing_password(self, client):
        """Test creating user without password fails"""
        response = client.post(
            "/users/",
            json={
                "email": "test@example.com",
                "name": "Test User"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """Test user login and JWT token generation"""

    def test_login_success(self, client, test_user):
        """Test successful login returns JWT token"""
        response = client.post(
            "/users/login",
            json={
                "email": test_user.email,
                "password": "testpassword123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_id"] == test_user.id

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password fails"""
        response = client.post(
            "/users/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent email fails"""
        response = client.post(
            "/users/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_invalid_email_format(self, client):
        """Test login with invalid email format"""
        response = client.post(
            "/users/login",
            json={
                "email": "not-an-email",
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestJWTAuthentication:
    """Test JWT token authentication"""

    def test_get_current_user_with_valid_token(self, client, auth_headers, test_user):
        """Test accessing protected endpoint with valid token"""
        response = client.get("/users/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["id"] == test_user.id

    def test_get_current_user_without_token(self, client):
        """Test accessing protected endpoint without token fails"""
        response = client.get("/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token fails"""
        response = client.get(
            "/users/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_with_malformed_header(self, client):
        """Test accessing protected endpoint with malformed auth header"""
        response = client.get(
            "/users/me",
            headers={"Authorization": "NotBearer token123"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserManagement:
    """Test user CRUD operations"""

    def test_get_all_users(self, client, test_user, second_user, auth_headers):
        """Test retrieving all users (admin functionality)"""
        response = client.get("/users/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 2
        emails = [user["email"] for user in data]
        assert test_user.email in emails
        assert second_user.email in emails

    def test_get_user_by_id(self, client, test_user, auth_headers):
        """Test retrieving specific user by ID"""
        response = client.get(f"/users/{test_user.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["id"] == test_user.id

    def test_get_nonexistent_user(self, client, auth_headers):
        """Test retrieving non-existent user returns 404"""
        response = client.get("/users/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_user(self, client, test_user, auth_headers):
        """Test updating user information"""
        response = client.put(
            f"/users/{test_user.id}",
            headers=auth_headers,
            json={"name": "Updated Name"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["email"] == test_user.email

    def test_delete_user(self, client, test_user, auth_headers):
        """Test deleting a user"""
        response = client.delete(f"/users/{test_user.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify user is deleted
        response = client.get(f"/users/{test_user.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

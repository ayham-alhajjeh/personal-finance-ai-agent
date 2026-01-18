import pytest
import sys
from pathlib import Path

# Add the backend/app directory to the Python path
backend_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(backend_dir))

from utils.security import hash_password, verify_password
from utils.jwt import create_access_token, decode_access_token
from datetime import timedelta


class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_hash_password_creates_different_hash(self):
        """Test that hashing same password twice creates different hashes"""
        password = "mypassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2  # Bcrypt adds salt, so hashes differ
        assert hash1 != password  # Hash is different from plaintext

    def test_verify_password_correct(self):
        """Test verifying correct password"""
        password = "correct_password"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test verifying incorrect password fails"""
        password = "correct_password"
        hashed = hash_password(password)

        assert verify_password("wrong_password", hashed) is False

    def test_hash_empty_password(self):
        """Test hashing empty password"""
        hashed = hash_password("")
        assert hashed is not None
        assert verify_password("", hashed) is True

    def test_hash_long_password(self):
        """Test hashing very long password"""
        long_password = "a" * 1000
        hashed = hash_password(long_password)
        assert verify_password(long_password, hashed) is True

    def test_hash_special_characters(self):
        """Test hashing password with special characters"""
        password = "P@ssw0rd!#$%^&*()"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True


class TestJWTTokens:
    """Test JWT token creation and validation"""

    def test_create_access_token(self):
        """Test creating JWT access token"""
        data = {"sub": "123"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_token(self):
        """Test decoding valid JWT token"""
        user_id = "456"
        data = {"sub": user_id}
        token = create_access_token(data)

        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == user_id

    def test_decode_invalid_token(self):
        """Test decoding invalid JWT token returns None"""
        invalid_token = "this.is.invalid"
        payload = decode_access_token(invalid_token)

        assert payload is None

    def test_decode_expired_token(self):
        """Test decoding expired JWT token returns None"""
        data = {"sub": "789"}
        # Create token that expires immediately
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))

        payload = decode_access_token(token)
        assert payload is None

    def test_token_contains_expiration(self):
        """Test that token contains expiration claim"""
        data = {"sub": "101"}
        token = create_access_token(data)

        payload = decode_access_token(token)
        assert "exp" in payload

    def test_custom_expiration_time(self):
        """Test creating token with custom expiration"""
        data = {"sub": "202"}
        custom_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=custom_delta)

        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "202"

    def test_token_with_additional_claims(self):
        """Test token with additional claims"""
        data = {
            "sub": "303",
            "email": "test@example.com",
            "role": "admin"
        }
        token = create_access_token(data)

        payload = decode_access_token(token)
        assert payload["sub"] == "303"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "admin"


class TestAuthenticationSecurity:
    """Test authentication security measures"""

    def test_password_not_in_response(self, client):
        """Test that password is never returned in API responses"""
        response = client.post(
            "/users/",
            json={
                "email": "secure@example.com",
                "name": "Secure User",
                "password": "secretpassword123"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert "password" not in data
        assert "hashed_password" not in data

    def test_sql_injection_in_email(self, client):
        """Test SQL injection attempt in email field"""
        response = client.post(
            "/users/login",
            json={
                "email": "admin' OR '1'='1",
                "password": "anything"
            }
        )

        # Should not bypass authentication
        assert response.status_code != 200

    def test_multiple_failed_login_attempts(self, client, test_user):
        """Test multiple failed login attempts"""
        # Attempt multiple failed logins
        for _ in range(5):
            response = client.post(
                "/users/login",
                json={
                    "email": test_user.email,
                    "password": "wrongpassword"
                }
            )
            assert response.status_code == 401

        # Valid login should still work (no lockout implemented yet)
        response = client.post(
            "/users/login",
            json={
                "email": test_user.email,
                "password": "testpassword123"
            }
        )
        assert response.status_code == 200

    def test_unauthorized_access_to_protected_routes(self, client):
        """Test accessing protected routes without token"""
        protected_endpoints = [
            ("/users/me", "GET"),
            ("/transactions/", "GET"),
            ("/categories/", "GET"),
            ("/budgets/", "GET"),
            ("/goals/", "GET")
        ]

        for endpoint, method in protected_endpoints:
            if method == "GET":
                response = client.get(endpoint)

            assert response.status_code in [401, 403], f"Endpoint {endpoint} should be protected"

    def test_token_reuse_across_users(self, client, test_user, second_user, test_user_token):
        """Test that token from one user cannot access another user's data"""
        # User 2 creates a transaction
        second_token = create_access_token(data={"sub": str(second_user.id)})
        second_headers = {"Authorization": f"Bearer {second_token}"}

        from datetime import date
        trans_response = client.post(
            "/transactions/",
            headers=second_headers,
            json={
                "date": str(date.today()),
                "description": "User 2 transaction",
                "amount": 100.00
            }
        )
        transaction_id = trans_response.json()["id"]

        # User 1 tries to access User 2's transaction with their own valid token
        user1_headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.get(f"/transactions/{transaction_id}", headers=user1_headers)

        assert response.status_code == 404  # Should not find it

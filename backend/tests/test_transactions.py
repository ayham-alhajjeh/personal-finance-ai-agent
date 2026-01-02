import pytest
from datetime import date, timedelta
from fastapi import status


class TestTransactionCreation:
    """Test transaction creation functionality"""

    def test_create_transaction_success(self, client, auth_headers):
        """Test successful transaction creation"""
        response = client.post(
            "/transactions/",
            headers=auth_headers,
            json={
                "date": str(date.today()),
                "description": "Grocery shopping",
                "amount": 125.50,
                "category_id": None
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["description"] == "Grocery shopping"
        assert data["amount"] == 125.50
        assert "id" in data

    def test_create_transaction_with_category(self, client, auth_headers):
        """Test creating transaction with category"""
        # First create a category
        category_response = client.post(
            "/categories/",
            headers=auth_headers,
            json={"name": "Food", "type": "expense"}
        )
        category_id = category_response.json()["id"]

        # Create transaction with category
        response = client.post(
            "/transactions/",
            headers=auth_headers,
            json={
                "date": str(date.today()),
                "description": "Restaurant",
                "amount": 45.00,
                "category_id": category_id
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["category_id"] == category_id

    def test_create_transaction_without_auth(self, client):
        """Test creating transaction without authentication fails"""
        response = client.post(
            "/transactions/",
            json={
                "date": str(date.today()),
                "description": "Test",
                "amount": 100.00
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_transaction_missing_fields(self, client, auth_headers):
        """Test creating transaction with missing required fields"""
        response = client.post(
            "/transactions/",
            headers=auth_headers,
            json={
                "description": "Incomplete transaction"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_transaction_negative_amount(self, client, auth_headers):
        """Test creating transaction with negative amount"""
        response = client.post(
            "/transactions/",
            headers=auth_headers,
            json={
                "date": str(date.today()),
                "description": "Refund",
                "amount": -50.00
            }
        )
        # Should still succeed as refunds can be negative
        assert response.status_code == status.HTTP_201_CREATED


class TestTransactionRetrieval:
    """Test transaction retrieval functionality"""

    def test_get_all_transactions(self, client, auth_headers):
        """Test retrieving all transactions for authenticated user"""
        # Create multiple transactions
        for i in range(3):
            client.post(
                "/transactions/",
                headers=auth_headers,
                json={
                    "date": str(date.today()),
                    "description": f"Transaction {i}",
                    "amount": 100.00 * (i + 1)
                }
            )

        response = client.get("/transactions/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3

    def test_get_transaction_by_id(self, client, auth_headers):
        """Test retrieving specific transaction by ID"""
        # Create transaction
        create_response = client.post(
            "/transactions/",
            headers=auth_headers,
            json={
                "date": str(date.today()),
                "description": "Test transaction",
                "amount": 200.00
            }
        )
        transaction_id = create_response.json()["id"]

        # Retrieve transaction
        response = client.get(f"/transactions/{transaction_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == transaction_id
        assert data["description"] == "Test transaction"

    def test_get_transaction_unauthorized_user(self, client, auth_headers, second_auth_headers):
        """Test that users can only access their own transactions"""
        # User 1 creates transaction
        create_response = client.post(
            "/transactions/",
            headers=auth_headers,
            json={
                "date": str(date.today()),
                "description": "User 1 transaction",
                "amount": 100.00
            }
        )
        transaction_id = create_response.json()["id"]

        # User 2 tries to access User 1's transaction
        response = client.get(f"/transactions/{transaction_id}", headers=second_auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_nonexistent_transaction(self, client, auth_headers):
        """Test retrieving non-existent transaction returns 404"""
        response = client.get("/transactions/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_transactions_pagination(self, client, auth_headers):
        """Test transaction pagination"""
        # Create 15 transactions
        for i in range(15):
            client.post(
                "/transactions/",
                headers=auth_headers,
                json={
                    "date": str(date.today()),
                    "description": f"Transaction {i}",
                    "amount": 50.00
                }
            )

        # Test with limit
        response = client.get("/transactions/?limit=5", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5

        # Test with skip and limit
        response = client.get("/transactions/?skip=5&limit=5", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5


class TestTransactionUpdate:
    """Test transaction update functionality"""

    def test_update_transaction_success(self, client, auth_headers):
        """Test successful transaction update"""
        # Create transaction
        create_response = client.post(
            "/transactions/",
            headers=auth_headers,
            json={
                "date": str(date.today()),
                "description": "Original description",
                "amount": 100.00
            }
        )
        transaction_id = create_response.json()["id"]

        # Update transaction
        response = client.put(
            f"/transactions/{transaction_id}",
            headers=auth_headers,
            json={
                "description": "Updated description",
                "amount": 150.00
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["amount"] == 150.00

    def test_update_transaction_partial(self, client, auth_headers):
        """Test partial transaction update"""
        # Create transaction
        create_response = client.post(
            "/transactions/",
            headers=auth_headers,
            json={
                "date": str(date.today()),
                "description": "Original",
                "amount": 100.00
            }
        )
        transaction_id = create_response.json()["id"]

        # Update only description
        response = client.put(
            f"/transactions/{transaction_id}",
            headers=auth_headers,
            json={"description": "Only description changed"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Only description changed"
        assert data["amount"] == 100.00

    def test_update_transaction_unauthorized(self, client, auth_headers, second_auth_headers):
        """Test that users cannot update other users' transactions"""
        # User 1 creates transaction
        create_response = client.post(
            "/transactions/",
            headers=auth_headers,
            json={
                "date": str(date.today()),
                "description": "User 1 transaction",
                "amount": 100.00
            }
        )
        transaction_id = create_response.json()["id"]

        # User 2 tries to update
        response = client.put(
            f"/transactions/{transaction_id}",
            headers=second_auth_headers,
            json={"description": "Hacked!"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTransactionDeletion:
    """Test transaction deletion functionality"""

    def test_delete_transaction_success(self, client, auth_headers):
        """Test successful transaction deletion"""
        # Create transaction
        create_response = client.post(
            "/transactions/",
            headers=auth_headers,
            json={
                "date": str(date.today()),
                "description": "To be deleted",
                "amount": 100.00
            }
        )
        transaction_id = create_response.json()["id"]

        # Delete transaction
        response = client.delete(f"/transactions/{transaction_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        response = client.get(f"/transactions/{transaction_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_transaction_unauthorized(self, client, auth_headers, second_auth_headers):
        """Test that users cannot delete other users' transactions"""
        # User 1 creates transaction
        create_response = client.post(
            "/transactions/",
            headers=auth_headers,
            json={
                "date": str(date.today()),
                "description": "User 1 transaction",
                "amount": 100.00
            }
        )
        transaction_id = create_response.json()["id"]

        # User 2 tries to delete
        response = client.delete(f"/transactions/{transaction_id}", headers=second_auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_transaction(self, client, auth_headers):
        """Test deleting non-existent transaction"""
        response = client.delete("/transactions/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

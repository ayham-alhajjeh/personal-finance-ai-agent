import pytest
from fastapi import status


class TestCategoryCreation:
    """Test category creation functionality"""

    def test_create_category_success(self, client, auth_headers):
        """Test successful category creation"""
        response = client.post(
            "/categories/",
            headers=auth_headers,
            json={
                "name": "Groceries",
                "type": "expense"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Groceries"
        assert data["type"] == "expense"
        assert "id" in data

    def test_create_category_without_type(self, client, auth_headers):
        """Test creating category without type field"""
        response = client.post(
            "/categories/",
            headers=auth_headers,
            json={"name": "Miscellaneous"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Miscellaneous"

    def test_create_category_without_auth(self, client):
        """Test creating category without authentication fails"""
        response = client.post(
            "/categories/",
            json={"name": "Test Category"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_category_missing_name(self, client, auth_headers):
        """Test creating category without name fails"""
        response = client.post(
            "/categories/",
            headers=auth_headers,
            json={"type": "expense"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_multiple_categories(self, client, auth_headers):
        """Test creating multiple categories"""
        categories = [
            {"name": "Food", "type": "expense"},
            {"name": "Transport", "type": "expense"},
            {"name": "Salary", "type": "income"}
        ]

        for category in categories:
            response = client.post(
                "/categories/",
                headers=auth_headers,
                json=category
            )
            assert response.status_code == status.HTTP_201_CREATED


class TestCategoryRetrieval:
    """Test category retrieval functionality"""

    def test_get_all_categories(self, client, auth_headers):
        """Test retrieving all categories for authenticated user"""
        # Create multiple categories
        categories = ["Food", "Transport", "Entertainment"]
        for name in categories:
            client.post(
                "/categories/",
                headers=auth_headers,
                json={"name": name, "type": "expense"}
            )

        response = client.get("/categories/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        category_names = [cat["name"] for cat in data]
        for name in categories:
            assert name in category_names

    def test_get_category_by_id(self, client, auth_headers):
        """Test retrieving specific category by ID"""
        # Create category
        create_response = client.post(
            "/categories/",
            headers=auth_headers,
            json={"name": "Shopping", "type": "expense"}
        )
        category_id = create_response.json()["id"]

        # Retrieve category
        response = client.get(f"/categories/{category_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == category_id
        assert data["name"] == "Shopping"

    def test_get_category_unauthorized_user(self, client, auth_headers, second_auth_headers):
        """Test that users can only access their own categories"""
        # User 1 creates category
        create_response = client.post(
            "/categories/",
            headers=auth_headers,
            json={"name": "User 1 Category", "type": "expense"}
        )
        category_id = create_response.json()["id"]

        # User 2 tries to access User 1's category
        response = client.get(f"/categories/{category_id}", headers=second_auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_nonexistent_category(self, client, auth_headers):
        """Test retrieving non-existent category returns 404"""
        response = client.get("/categories/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_categories_empty_list(self, client, auth_headers):
        """Test retrieving categories when user has none"""
        response = client.get("/categories/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_categories_isolation_between_users(self, client, auth_headers, second_auth_headers):
        """Test that categories are isolated between users"""
        # User 1 creates categories
        client.post("/categories/", headers=auth_headers, json={"name": "User1 Cat1"})
        client.post("/categories/", headers=auth_headers, json={"name": "User1 Cat2"})

        # User 2 creates categories
        client.post("/categories/", headers=second_auth_headers, json={"name": "User2 Cat1"})

        # User 1 should see only their categories
        response1 = client.get("/categories/", headers=auth_headers)
        user1_categories = response1.json()
        assert len(user1_categories) == 2
        assert all("User1" in cat["name"] for cat in user1_categories)

        # User 2 should see only their categories
        response2 = client.get("/categories/", headers=second_auth_headers)
        user2_categories = response2.json()
        assert len(user2_categories) == 1
        assert user2_categories[0]["name"] == "User2 Cat1"


class TestCategoryUpdate:
    """Test category update functionality"""

    def test_update_category_success(self, client, auth_headers):
        """Test successful category update"""
        # Create category
        create_response = client.post(
            "/categories/",
            headers=auth_headers,
            json={"name": "Original Name", "type": "expense"}
        )
        category_id = create_response.json()["id"]

        # Update category
        response = client.put(
            f"/categories/{category_id}",
            headers=auth_headers,
            json={"name": "Updated Name", "type": "income"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["type"] == "income"

    def test_update_category_partial(self, client, auth_headers):
        """Test partial category update"""
        # Create category
        create_response = client.post(
            "/categories/",
            headers=auth_headers,
            json={"name": "Original", "type": "expense"}
        )
        category_id = create_response.json()["id"]

        # Update only name
        response = client.put(
            f"/categories/{category_id}",
            headers=auth_headers,
            json={"name": "Only Name Changed"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Only Name Changed"
        assert data["type"] == "expense"

    def test_update_category_unauthorized(self, client, auth_headers, second_auth_headers):
        """Test that users cannot update other users' categories"""
        # User 1 creates category
        create_response = client.post(
            "/categories/",
            headers=auth_headers,
            json={"name": "User 1 Category"}
        )
        category_id = create_response.json()["id"]

        # User 2 tries to update
        response = client.put(
            f"/categories/{category_id}",
            headers=second_auth_headers,
            json={"name": "Hacked!"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_nonexistent_category(self, client, auth_headers):
        """Test updating non-existent category"""
        response = client.put(
            "/categories/99999",
            headers=auth_headers,
            json={"name": "New Name"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCategoryDeletion:
    """Test category deletion functionality"""

    def test_delete_category_success(self, client, auth_headers):
        """Test successful category deletion"""
        # Create category
        create_response = client.post(
            "/categories/",
            headers=auth_headers,
            json={"name": "To be deleted"}
        )
        category_id = create_response.json()["id"]

        # Delete category
        response = client.delete(f"/categories/{category_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        response = client.get(f"/categories/{category_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_category_unauthorized(self, client, auth_headers, second_auth_headers):
        """Test that users cannot delete other users' categories"""
        # User 1 creates category
        create_response = client.post(
            "/categories/",
            headers=auth_headers,
            json={"name": "User 1 Category"}
        )
        category_id = create_response.json()["id"]

        # User 2 tries to delete
        response = client.delete(f"/categories/{category_id}", headers=second_auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_category(self, client, auth_headers):
        """Test deleting non-existent category"""
        response = client.delete("/categories/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCategoryTransactionRelationship:
    """Test category and transaction relationship"""

    def test_transaction_with_valid_category(self, client, auth_headers):
        """Test creating transaction with valid category"""
        # Create category
        cat_response = client.post(
            "/categories/",
            headers=auth_headers,
            json={"name": "Food", "type": "expense"}
        )
        category_id = cat_response.json()["id"]

        # Create transaction with category
        from datetime import date
        trans_response = client.post(
            "/transactions/",
            headers=auth_headers,
            json={
                "date": str(date.today()),
                "description": "Lunch",
                "amount": 15.00,
                "category_id": category_id
            }
        )
        assert trans_response.status_code == status.HTTP_201_CREATED
        assert trans_response.json()["category_id"] == category_id

    def test_multiple_transactions_same_category(self, client, auth_headers):
        """Test creating multiple transactions with same category"""
        # Create category
        cat_response = client.post(
            "/categories/",
            headers=auth_headers,
            json={"name": "Transport"}
        )
        category_id = cat_response.json()["id"]

        # Create multiple transactions
        from datetime import date
        for i in range(3):
            response = client.post(
                "/transactions/",
                headers=auth_headers,
                json={
                    "date": str(date.today()),
                    "description": f"Trip {i}",
                    "amount": 10.00 * (i + 1),
                    "category_id": category_id
                }
            )
            assert response.status_code == status.HTTP_201_CREATED

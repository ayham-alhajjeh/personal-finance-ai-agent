import pytest
from datetime import date, timedelta
from fastapi import status


class TestBudgetCreation:
    """Test budget creation functionality"""

    def test_create_budget_success(self, client, auth_headers):
        """Test successful budget creation"""
        start_date = date.today()
        end_date = start_date + timedelta(days=30)

        response = client.post(
            "/budgets/",
            headers=auth_headers,
            json={
                "name": "Monthly Budget",
                "start_date": str(start_date),
                "end_date": str(end_date)
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Monthly Budget"
        assert "id" in data

    def test_create_budget_without_auth(self, client):
        """Test creating budget without authentication fails"""
        response = client.post(
            "/budgets/",
            json={
                "name": "Test Budget",
                "start_date": str(date.today()),
                "end_date": str(date.today() + timedelta(days=30))
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_budget_missing_fields(self, client, auth_headers):
        """Test creating budget with missing required fields"""
        response = client.post(
            "/budgets/",
            headers=auth_headers,
            json={"name": "Incomplete Budget"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_multiple_budgets(self, client, auth_headers):
        """Test creating multiple budgets"""
        budgets = [
            {"name": "January", "start_date": "2024-01-01", "end_date": "2024-01-31"},
            {"name": "February", "start_date": "2024-02-01", "end_date": "2024-02-29"},
            {"name": "March", "start_date": "2024-03-01", "end_date": "2024-03-31"}
        ]

        for budget in budgets:
            response = client.post(
                "/budgets/",
                headers=auth_headers,
                json=budget
            )
            assert response.status_code == status.HTTP_201_CREATED


class TestBudgetRetrieval:
    """Test budget retrieval functionality"""

    def test_get_all_budgets(self, client, auth_headers):
        """Test retrieving all budgets for authenticated user"""
        # Create multiple budgets
        for i in range(3):
            client.post(
                "/budgets/",
                headers=auth_headers,
                json={
                    "name": f"Budget {i}",
                    "start_date": str(date.today()),
                    "end_date": str(date.today() + timedelta(days=30))
                }
            )

        response = client.get("/budgets/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3

    def test_get_budget_by_id(self, client, auth_headers):
        """Test retrieving specific budget by ID"""
        # Create budget
        create_response = client.post(
            "/budgets/",
            headers=auth_headers,
            json={
                "name": "Test Budget",
                "start_date": str(date.today()),
                "end_date": str(date.today() + timedelta(days=30))
            }
        )
        budget_id = create_response.json()["id"]

        # Retrieve budget
        response = client.get(f"/budgets/{budget_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == budget_id
        assert data["name"] == "Test Budget"

    def test_get_budget_unauthorized_user(self, client, auth_headers, second_auth_headers):
        """Test that users can only access their own budgets"""
        # User 1 creates budget
        create_response = client.post(
            "/budgets/",
            headers=auth_headers,
            json={
                "name": "User 1 Budget",
                "start_date": str(date.today()),
                "end_date": str(date.today() + timedelta(days=30))
            }
        )
        budget_id = create_response.json()["id"]

        # User 2 tries to access User 1's budget
        response = client.get(f"/budgets/{budget_id}", headers=second_auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_nonexistent_budget(self, client, auth_headers):
        """Test retrieving non-existent budget returns 404"""
        response = client.get("/budgets/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_active_budgets(self, client, auth_headers):
        """Test retrieving only active budgets"""
        # Create active budget (current date is within range)
        client.post(
            "/budgets/",
            headers=auth_headers,
            json={
                "name": "Active Budget",
                "start_date": str(date.today() - timedelta(days=5)),
                "end_date": str(date.today() + timedelta(days=25))
            }
        )

        # Create past budget
        client.post(
            "/budgets/",
            headers=auth_headers,
            json={
                "name": "Past Budget",
                "start_date": str(date.today() - timedelta(days=60)),
                "end_date": str(date.today() - timedelta(days=30))
            }
        )

        # Create future budget
        client.post(
            "/budgets/",
            headers=auth_headers,
            json={
                "name": "Future Budget",
                "start_date": str(date.today() + timedelta(days=30)),
                "end_date": str(date.today() + timedelta(days=60))
            }
        )

        response = client.get("/budgets/active", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Active Budget"

    def test_budgets_isolation_between_users(self, client, auth_headers, second_auth_headers):
        """Test that budgets are isolated between users"""
        # User 1 creates budgets
        client.post(
            "/budgets/",
            headers=auth_headers,
            json={
                "name": "User1 Budget1",
                "start_date": str(date.today()),
                "end_date": str(date.today() + timedelta(days=30))
            }
        )
        client.post(
            "/budgets/",
            headers=auth_headers,
            json={
                "name": "User1 Budget2",
                "start_date": str(date.today()),
                "end_date": str(date.today() + timedelta(days=30))
            }
        )

        # User 2 creates budget
        client.post(
            "/budgets/",
            headers=second_auth_headers,
            json={
                "name": "User2 Budget1",
                "start_date": str(date.today()),
                "end_date": str(date.today() + timedelta(days=30))
            }
        )

        # User 1 should see only their budgets
        response1 = client.get("/budgets/", headers=auth_headers)
        user1_budgets = response1.json()
        assert len(user1_budgets) == 2
        assert all("User1" in b["name"] for b in user1_budgets)

        # User 2 should see only their budget
        response2 = client.get("/budgets/", headers=second_auth_headers)
        user2_budgets = response2.json()
        assert len(user2_budgets) == 1
        assert user2_budgets[0]["name"] == "User2 Budget1"


class TestBudgetUpdate:
    """Test budget update functionality"""

    def test_update_budget_success(self, client, auth_headers):
        """Test successful budget update"""
        # Create budget
        create_response = client.post(
            "/budgets/",
            headers=auth_headers,
            json={
                "name": "Original Budget",
                "start_date": str(date.today()),
                "end_date": str(date.today() + timedelta(days=30))
            }
        )
        budget_id = create_response.json()["id"]

        # Update budget
        new_end_date = date.today() + timedelta(days=60)
        response = client.put(
            f"/budgets/{budget_id}",
            headers=auth_headers,
            json={
                "name": "Updated Budget",
                "end_date": str(new_end_date)
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Budget"

    def test_update_budget_invalid_dates(self, client, auth_headers):
        """Test updating budget with start_date after end_date fails"""
        # Create budget
        create_response = client.post(
            "/budgets/",
            headers=auth_headers,
            json={
                "name": "Test Budget",
                "start_date": str(date.today()),
                "end_date": str(date.today() + timedelta(days=30))
            }
        )
        budget_id = create_response.json()["id"]

        # Try to update with invalid dates
        response = client.put(
            f"/budgets/{budget_id}",
            headers=auth_headers,
            json={
                "start_date": str(date.today() + timedelta(days=30)),
                "end_date": str(date.today())
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_budget_partial(self, client, auth_headers):
        """Test partial budget update"""
        # Create budget
        create_response = client.post(
            "/budgets/",
            headers=auth_headers,
            json={
                "name": "Original",
                "start_date": str(date.today()),
                "end_date": str(date.today() + timedelta(days=30))
            }
        )
        budget_id = create_response.json()["id"]

        # Update only name
        response = client.put(
            f"/budgets/{budget_id}",
            headers=auth_headers,
            json={"name": "Only Name Changed"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Only Name Changed"

    def test_update_budget_unauthorized(self, client, auth_headers, second_auth_headers):
        """Test that users cannot update other users' budgets"""
        # User 1 creates budget
        create_response = client.post(
            "/budgets/",
            headers=auth_headers,
            json={
                "name": "User 1 Budget",
                "start_date": str(date.today()),
                "end_date": str(date.today() + timedelta(days=30))
            }
        )
        budget_id = create_response.json()["id"]

        # User 2 tries to update
        response = client.put(
            f"/budgets/{budget_id}",
            headers=second_auth_headers,
            json={"name": "Hacked!"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestBudgetDeletion:
    """Test budget deletion functionality"""

    def test_delete_budget_success(self, client, auth_headers):
        """Test successful budget deletion"""
        # Create budget
        create_response = client.post(
            "/budgets/",
            headers=auth_headers,
            json={
                "name": "To be deleted",
                "start_date": str(date.today()),
                "end_date": str(date.today() + timedelta(days=30))
            }
        )
        budget_id = create_response.json()["id"]

        # Delete budget
        response = client.delete(f"/budgets/{budget_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        response = client.get(f"/budgets/{budget_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_budget_unauthorized(self, client, auth_headers, second_auth_headers):
        """Test that users cannot delete other users' budgets"""
        # User 1 creates budget
        create_response = client.post(
            "/budgets/",
            headers=auth_headers,
            json={
                "name": "User 1 Budget",
                "start_date": str(date.today()),
                "end_date": str(date.today() + timedelta(days=30))
            }
        )
        budget_id = create_response.json()["id"]

        # User 2 tries to delete
        response = client.delete(f"/budgets/{budget_id}", headers=second_auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_budget(self, client, auth_headers):
        """Test deleting non-existent budget"""
        response = client.delete("/budgets/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestBudgetPagination:
    """Test budget pagination"""

    def test_get_budgets_with_pagination(self, client, auth_headers):
        """Test budget retrieval with pagination"""
        # Create 15 budgets
        for i in range(15):
            client.post(
                "/budgets/",
                headers=auth_headers,
                json={
                    "name": f"Budget {i}",
                    "start_date": str(date.today()),
                    "end_date": str(date.today() + timedelta(days=30))
                }
            )

        # Test with limit
        response = client.get("/budgets/?limit=5", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5

        # Test with skip and limit
        response = client.get("/budgets/?skip=5&limit=5", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5

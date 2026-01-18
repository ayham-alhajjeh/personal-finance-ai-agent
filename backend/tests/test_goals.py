import pytest
from datetime import date, timedelta
from fastapi import status


class TestGoalCreation:
    """Test goal creation functionality"""

    def test_create_goal_success(self, client, auth_headers):
        """Test successful goal creation"""
        target_date = date.today() + timedelta(days=365)

        response = client.post(
            "/goals/",
            headers=auth_headers,
            json={
                "name": "Save for vacation",
                "target_amount": 5000.00,
                "target_date": str(target_date)
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Save for vacation"
        assert data["target_amount"] == 5000.00
        assert "id" in data

    def test_create_goal_without_auth(self, client):
        """Test creating goal without authentication fails"""
        response = client.post(
            "/goals/",
            json={
                "name": "Test Goal",
                "target_amount": 1000.00,
                "target_date": str(date.today() + timedelta(days=30))
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_goal_missing_fields(self, client, auth_headers):
        """Test creating goal with missing required fields"""
        response = client.post(
            "/goals/",
            headers=auth_headers,
            json={}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_multiple_goals(self, client, auth_headers):
        """Test creating multiple goals"""
        goals = [
            {"name": "Emergency Fund", "target_amount": 10000.00, "target_date": str(date.today() + timedelta(days=365))},
            {"name": "New Car", "target_amount": 25000.00, "target_date": str(date.today() + timedelta(days=730))},
            {"name": "House Down Payment", "target_amount": 50000.00, "target_date": str(date.today() + timedelta(days=1095))}
        ]

        for goal in goals:
            response = client.post(
                "/goals/",
                headers=auth_headers,
                json=goal
            )
            assert response.status_code == status.HTTP_201_CREATED

    def test_create_goal_with_zero_amount(self, client, auth_headers):
        """Test creating goal with zero target amount"""
        response = client.post(
            "/goals/",
            headers=auth_headers,
            json={
                "name": "Zero Goal",
                "target_amount": 0.00,
                "target_date": str(date.today() + timedelta(days=30))
            }
        )
        assert response.status_code == status.HTTP_201_CREATED


class TestGoalRetrieval:
    """Test goal retrieval functionality"""

    def test_get_all_goals(self, client, auth_headers):
        """Test retrieving all goals for authenticated user"""
        # Create multiple goals
        for i in range(3):
            client.post(
                "/goals/",
                headers=auth_headers,
                json={
                    "name": f"Goal {i}",
                    "target_amount": 1000.00 * (i + 1),
                    "target_date": str(date.today() + timedelta(days=30 * (i + 1)))
                }
            )

        response = client.get("/goals/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3

    def test_get_goal_by_id(self, client, auth_headers):
        """Test retrieving specific goal by ID"""
        # Create goal
        create_response = client.post(
            "/goals/",
            headers=auth_headers,
            json={
                "name": "Test Goal",
                "target_amount": 2000.00,
                "target_date": str(date.today() + timedelta(days=60))
            }
        )
        goal_id = create_response.json()["id"]

        # Retrieve goal
        response = client.get(f"/goals/{goal_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == goal_id
        assert data["name"] == "Test Goal"

    def test_get_goal_unauthorized_user(self, client, auth_headers, second_auth_headers):
        """Test that users can only access their own goals"""
        # User 1 creates goal
        create_response = client.post(
            "/goals/",
            headers=auth_headers,
            json={
                "name": "User 1 Goal",
                "target_amount": 5000.00,
                "target_date": str(date.today() + timedelta(days=365))
            }
        )
        goal_id = create_response.json()["id"]

        # User 2 tries to access User 1's goal
        response = client.get(f"/goals/{goal_id}", headers=second_auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_nonexistent_goal(self, client, auth_headers):
        """Test retrieving non-existent goal returns 404"""
        response = client.get("/goals/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_active_goals(self, client, auth_headers):
        """Test retrieving only active goals (future target dates)"""
        # Create active goal (future date)
        client.post(
            "/goals/",
            headers=auth_headers,
            json={
                "name": "Active Goal",
                "target_amount": 3000.00,
                "target_date": str(date.today() + timedelta(days=180))
            }
        )

        # Create past goal (expired)
        client.post(
            "/goals/",
            headers=auth_headers,
            json={
                "name": "Past Goal",
                "target_amount": 2000.00,
                "target_date": str(date.today() - timedelta(days=30))
            }
        )

        # Create goal expiring today (should be included)
        client.post(
            "/goals/",
            headers=auth_headers,
            json={
                "name": "Today Goal",
                "target_amount": 1000.00,
                "target_date": str(date.today())
            }
        )

        response = client.get("/goals/active", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        goal_names = [g["name"] for g in data]
        assert "Active Goal" in goal_names
        assert "Today Goal" in goal_names
        assert "Past Goal" not in goal_names

    def test_goals_isolation_between_users(self, client, auth_headers, second_auth_headers):
        """Test that goals are isolated between users"""
        # User 1 creates goals
        client.post(
            "/goals/",
            headers=auth_headers,
            json={
                "name": "User1 Goal1",
                "target_amount": 1000.00,
                "target_date": str(date.today() + timedelta(days=30))
            }
        )
        client.post(
            "/goals/",
            headers=auth_headers,
            json={
                "name": "User1 Goal2",
                "target_amount": 2000.00,
                "target_date": str(date.today() + timedelta(days=60))
            }
        )

        # User 2 creates goal
        client.post(
            "/goals/",
            headers=second_auth_headers,
            json={
                "name": "User2 Goal1",
                "target_amount": 3000.00,
                "target_date": str(date.today() + timedelta(days=90))
            }
        )

        # User 1 should see only their goals
        response1 = client.get("/goals/", headers=auth_headers)
        user1_goals = response1.json()
        assert len(user1_goals) == 2
        assert all("User1" in g["name"] for g in user1_goals)

        # User 2 should see only their goal
        response2 = client.get("/goals/", headers=second_auth_headers)
        user2_goals = response2.json()
        assert len(user2_goals) == 1
        assert user2_goals[0]["name"] == "User2 Goal1"


class TestGoalUpdate:
    """Test goal update functionality"""

    def test_update_goal_success(self, client, auth_headers):
        """Test successful goal update"""
        # Create goal
        create_response = client.post(
            "/goals/",
            headers=auth_headers,
            json={
                "name": "Original Goal",
                "target_amount": 5000.00,
                "target_date": str(date.today() + timedelta(days=365))
            }
        )
        goal_id = create_response.json()["id"]

        # Update goal
        response = client.put(
            f"/goals/{goal_id}",
            headers=auth_headers,
            json={
                "name": "Updated Goal",
                "target_amount": 7500.00
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Goal"
        assert data["target_amount"] == 7500.00

    def test_update_goal_partial(self, client, auth_headers):
        """Test partial goal update"""
        # Create goal
        create_response = client.post(
            "/goals/",
            headers=auth_headers,
            json={
                "name": "Original",
                "target_amount": 1000.00,
                "target_date": str(date.today() + timedelta(days=30))
            }
        )
        goal_id = create_response.json()["id"]

        # Update only target amount
        response = client.put(
            f"/goals/{goal_id}",
            headers=auth_headers,
            json={"target_amount": 2000.00}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Original"
        assert data["target_amount"] == 2000.00

    def test_update_goal_unauthorized(self, client, auth_headers, second_auth_headers):
        """Test that users cannot update other users' goals"""
        # User 1 creates goal
        create_response = client.post(
            "/goals/",
            headers=auth_headers,
            json={
                "name": "User 1 Goal",
                "target_amount": 5000.00,
                "target_date": str(date.today() + timedelta(days=365))
            }
        )
        goal_id = create_response.json()["id"]

        # User 2 tries to update
        response = client.put(
            f"/goals/{goal_id}",
            headers=second_auth_headers,
            json={"name": "Hacked!"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_goal_change_target_date(self, client, auth_headers):
        """Test updating goal target date"""
        # Create goal
        create_response = client.post(
            "/goals/",
            headers=auth_headers,
            json={
                "name": "Test Goal",
                "target_amount": 3000.00,
                "target_date": str(date.today() + timedelta(days=180))
            }
        )
        goal_id = create_response.json()["id"]

        # Extend target date
        new_date = date.today() + timedelta(days=365)
        response = client.put(
            f"/goals/{goal_id}",
            headers=auth_headers,
            json={"target_date": str(new_date)}
        )
        assert response.status_code == status.HTTP_200_OK


class TestGoalDeletion:
    """Test goal deletion functionality"""

    def test_delete_goal_success(self, client, auth_headers):
        """Test successful goal deletion"""
        # Create goal
        create_response = client.post(
            "/goals/",
            headers=auth_headers,
            json={
                "name": "To be deleted",
                "target_amount": 1000.00,
                "target_date": str(date.today() + timedelta(days=30))
            }
        )
        goal_id = create_response.json()["id"]

        # Delete goal
        response = client.delete(f"/goals/{goal_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        response = client.get(f"/goals/{goal_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_goal_unauthorized(self, client, auth_headers, second_auth_headers):
        """Test that users cannot delete other users' goals"""
        # User 1 creates goal
        create_response = client.post(
            "/goals/",
            headers=auth_headers,
            json={
                "name": "User 1 Goal",
                "target_amount": 5000.00,
                "target_date": str(date.today() + timedelta(days=365))
            }
        )
        goal_id = create_response.json()["id"]

        # User 2 tries to delete
        response = client.delete(f"/goals/{goal_id}", headers=second_auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_goal(self, client, auth_headers):
        """Test deleting non-existent goal"""
        response = client.delete("/goals/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGoalPagination:
    """Test goal pagination"""

    def test_get_goals_with_pagination(self, client, auth_headers):
        """Test goal retrieval with pagination"""
        # Create 12 goals
        for i in range(12):
            client.post(
                "/goals/",
                headers=auth_headers,
                json={
                    "name": f"Goal {i}",
                    "target_amount": 1000.00 * (i + 1),
                    "target_date": str(date.today() + timedelta(days=30 * (i + 1)))
                }
            )

        # Test with limit
        response = client.get("/goals/?limit=5", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5

        # Test with skip and limit
        response = client.get("/goals/?skip=5&limit=5", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5


class TestGoalValidation:
    """Test goal data validation"""

    def test_create_goal_with_very_large_amount(self, client, auth_headers):
        """Test creating goal with very large target amount"""
        response = client.post(
            "/goals/",
            headers=auth_headers,
            json={
                "name": "Big Goal",
                "target_amount": 1000000000.00,
                "target_date": str(date.today() + timedelta(days=3650))
            }
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_goal_past_target_date(self, client, auth_headers):
        """Test creating goal with past target date (should still work)"""
        response = client.post(
            "/goals/",
            headers=auth_headers,
            json={
                "name": "Past Goal",
                "target_amount": 1000.00,
                "target_date": str(date.today() - timedelta(days=30))
            }
        )
        # Should succeed - business logic allows creating past goals
        assert response.status_code == status.HTTP_201_CREATED

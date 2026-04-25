"""
Tests for the Mergington High School Activities API.
Uses the AAA (Arrange-Act-Assert) pattern.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a clean state before each test."""
    original_participants = {
        name: list(details["participants"])
        for name, details in activities.items()
    }
    yield
    for name, participants in original_participants.items():
        activities[name]["participants"] = participants


client = TestClient(app)


def test_get_activities_returns_all_activities():
    # Arrange: nothing needed, activities are pre-loaded

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 9
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_get_activities_returns_correct_structure():
    # Arrange: nothing needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    for activity_name, details in data.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)


def test_signup_for_activity_success():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_for_nonexistent_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_prevents_duplicate_registration():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # already in Chess Club

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_unregister_from_activity_success():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_from_nonexistent_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_student_not_signed_up_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "notsignedup@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_activities_include_sports():
    # Arrange: nothing needed

    # Act
    response = client.get("/activities")

    # Assert
    data = response.json()
    sports_activities = ["Basketball Team", "Swimming Club", "Gym Class"]
    for sport in sports_activities:
        assert sport in data, f"Expected sport activity '{sport}' not found"


def test_activities_include_artistic():
    # Arrange: nothing needed

    # Act
    response = client.get("/activities")

    # Assert
    data = response.json()
    artistic_activities = ["Art Studio", "Drama Club"]
    for art in artistic_activities:
        assert art in data, f"Expected artistic activity '{art}' not found"


def test_activities_include_intellectual():
    # Arrange: nothing needed

    # Act
    response = client.get("/activities")

    # Assert
    data = response.json()
    intellectual_activities = ["Chess Club", "Debate Team", "Science Club", "Programming Class"]
    for intellectual in intellectual_activities:
        assert intellectual in data, f"Expected intellectual activity '{intellectual}' not found"

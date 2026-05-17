from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_get_activities():
    # Arrange
    expected_activity = "Chess Club"
    expected_empty_participation_activity = "Math Olympiad"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert expected_activity in activities
    assert expected_empty_participation_activity in activities
    assert isinstance(activities[expected_empty_participation_activity]["participants"], list)


def test_signup_activity_success():
    # Arrange
    activity_name = "Math Olympiad"
    email = "test.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    # Act
    activity_response = client.get("/activities")
    participants = activity_response.json()[activity_name]["participants"]

    # Assert
    assert email in participants

    # Cleanup
    cleanup_response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    assert cleanup_response.status_code == 200


def test_signup_nonexistent_activity():
    # Arrange
    activity_path = "Nonexistent%20Activity"
    email = "ghost@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_path}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_success():
    # Arrange
    activity_name = "Chess Club"
    email = "temp.remove@mergington.edu"
    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_response.status_code == 200

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}

    # Act
    activity_response = client.get("/activities")
    participants = activity_response.json()[activity_name]["participants"]

    # Assert
    assert email not in participants


def test_remove_nonexistent_participant():
    # Arrange
    activity_path = "Chess%20Club"
    email = "nobody@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_path}/participants?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in activity"

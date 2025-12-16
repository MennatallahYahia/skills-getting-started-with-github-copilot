"""
Tests for the Mergington High School Activity Management API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities before each test"""
    # Store original state
    original_activities = {
        "Debate Club": {
            "description": "Develop argumentation and public speaking skills through competitive debate",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu"]
        },
        "Robotics Team": {
            "description": "Build and program robots for competitions",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "sara@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball league and training",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["tyler@mergington.edu"]
        },
        "Volleyball Club": {
            "description": "Learn and play volleyball with other enthusiasts",
            "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media techniques",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["hannah@mergington.edu"]
        },
        "Theater Production": {
            "description": "Perform in school plays and musicals",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["christopher@mergington.edu", "isabella@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["ryan@mergington.edu", "sophia@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(original_activities)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10
        assert "Debate Club" in data
        assert "Robotics Team" in data

    def test_get_activities_has_correct_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Debate Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_get_activities_includes_participants(self, client):
        """Test that activities include participant information"""
        response = client.get("/activities")
        data = response.json()
        
        # Debate Club should have alex@mergington.edu
        assert "alex@mergington.edu" in data["Debate Club"]["participants"]
        # Robotics Team should have james@mergington.edu and sara@mergington.edu
        assert "james@mergington.edu" in data["Robotics Team"]["participants"]
        assert "sara@mergington.edu" in data["Robotics Team"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant(self, client):
        """Test signing up a new participant to an activity"""
        response = client.post(
            "/activities/Debate Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "newstudent@mergington.edu" in data["message"]
        assert "Debate Club" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Debate Club"]["participants"]

    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_participant(self, client):
        """Test that duplicate signups are rejected"""
        response = client.post(
            "/activities/Debate Club/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_multiple_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        response1 = client.post(
            "/activities/Debate Club/signup?email=student@mergington.edu"
        )
        assert response1.status_code == 200
        
        response2 = client.post(
            "/activities/Robotics Team/signup?email=student@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify student is in both activities
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert "student@mergington.edu" in data["Debate Club"]["participants"]
        assert "student@mergington.edu" in data["Robotics Team"]["participants"]

    def test_signup_preserves_existing_participants(self, client):
        """Test that signup doesn't affect other participants"""
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_count = len(initial_data["Debate Club"]["participants"])
        
        client.post("/activities/Debate Club/signup?email=newstudent@mergington.edu")
        
        final_response = client.get("/activities")
        final_data = final_response.json()
        assert len(final_data["Debate Club"]["participants"]) == initial_count + 1


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant"""
        response = client.delete(
            "/activities/Debate Club/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "alex@mergington.edu" in data["message"]
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "alex@mergington.edu" not in activities_data["Debate Club"]["participants"]

    def test_unregister_activity_not_found(self, client):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_participant_not_enrolled(self, client):
        """Test unregistering a participant not enrolled in the activity"""
        response = client.delete(
            "/activities/Debate Club/unregister?email=noone@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_multiple_participants(self, client):
        """Test unregistering multiple participants from same activity"""
        # Robotics Team has james and sara
        response1 = client.delete(
            "/activities/Robotics Team/unregister?email=james@mergington.edu"
        )
        assert response1.status_code == 200
        
        response2 = client.delete(
            "/activities/Robotics Team/unregister?email=sara@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify both were removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "james@mergington.edu" not in activities_data["Robotics Team"]["participants"]
        assert "sara@mergington.edu" not in activities_data["Robotics Team"]["participants"]

    def test_unregister_preserves_other_participants(self, client):
        """Test that unregister doesn't affect other participants"""
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_participants = initial_data["Robotics Team"]["participants"].copy()
        
        client.delete("/activities/Robotics Team/unregister?email=james@mergington.edu")
        
        final_response = client.get("/activities")
        final_data = final_response.json()
        remaining = final_data["Robotics Team"]["participants"]
        
        # sara should still be there
        assert "sara@mergington.edu" in remaining
        # Only james should be removed
        assert len(remaining) == len(initial_participants) - 1


class TestActivityCounts:
    """Tests for activity participant counts and availability"""

    def test_activity_count_increases_on_signup(self, client):
        """Test that participant count increases on signup"""
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_count = len(initial_data["Debate Club"]["participants"])
        
        client.post("/activities/Debate Club/signup?email=newstudent@mergington.edu")
        
        updated_response = client.get("/activities")
        updated_data = updated_response.json()
        assert len(updated_data["Debate Club"]["participants"]) == initial_count + 1

    def test_activity_count_decreases_on_unregister(self, client):
        """Test that participant count decreases on unregister"""
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_count = len(initial_data["Debate Club"]["participants"])
        
        client.delete("/activities/Debate Club/unregister?email=alex@mergington.edu")
        
        updated_response = client.get("/activities")
        updated_data = updated_response.json()
        assert len(updated_data["Debate Club"]["participants"]) == initial_count - 1

    def test_max_participants_constraint(self, client):
        """Test that max_participants value is correct"""
        response = client.get("/activities")
        data = response.json()
        
        # Verify each activity has a max_participants value
        for activity_name, activity in data.items():
            assert "max_participants" in activity
            assert activity["max_participants"] > 0
            assert len(activity["participants"]) <= activity["max_participants"]

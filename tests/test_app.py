from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_for_activity_adds_participant():
    response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    assert response.json()["message"] == "Signed up newstudent@mergington.edu for Chess Club"


def test_signup_rejects_duplicate_email():
    client.post("/activities/Chess Club/signup?email=duplicate@mergington.edu")
    response = client.post("/activities/Chess Club/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_signup_normalizes_email_address():
    response = client.post("/activities/Art Studio/signup?email=  NEW@MERGINGTON.EDU  ")
    assert response.status_code == 200
    assert "new@mergington.edu" in response.json()["message"]


def test_signup_rejects_invalid_email():
    response = client.post("/activities/Art Studio/signup?email=not-an-email")
    assert response.status_code == 422
    assert response.json()["detail"] == "A valid email address is required"


def test_signup_rejects_full_activity():
    activity = "Science Club"
    for index in range(20):
        client.post(f"/activities/{activity}/signup?email=student{index}@mergington.edu")

    response = client.post(f"/activities/{activity}/signup?email=overflow@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"

import os
os.environ["APP_VERSION"] = "v1"
from app import app

def test_health():
    response = app.test_client().get("/health")
    assert response.status_code == 200
    assert response.get_json()["version"] == "v1"

def test_update_is_not_enabled_in_v1():
    response = app.test_client().post("/update", data={"name":"Test","quantity":"1"})
    assert response.status_code == 404

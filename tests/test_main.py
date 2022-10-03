from fastapi.testclient import TestClient
import sys

#sys.path.append("../app")
from app.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/users")
    assert response.status_code == 200
    #assert response.json() == {"msg": "Hello World"}
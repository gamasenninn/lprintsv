from fastapi.testclient import TestClient
import sys

#sys.path.append("../")
from app.main import app


client = TestClient(app)


def test_read_main():
    response = client.get("/users")
    print(response.status_code)
    assert response.status_code == 200
    #assert response.json() == {"msg": "Hello World"}



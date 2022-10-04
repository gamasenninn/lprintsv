from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys

sys.path.append("../../app")
#from database import Base
from main import app,get_db
import models

SQLALCHEMY_DATABASE_URL = "sqlite://"  #For inmemory

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool  #For inmemory
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


models.Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)


def test_create_user():
    response = client.post(
        "/users/",
        json={"email": "deadpool@example.com", "password": "ono","name":"ono"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    print(data)
    assert data["email"] == "deadpool@example.com"
    assert "id" in data
    user_id = data["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "deadpool@example.com"
    assert data["id"] == user_id

def test_read_user():
    user_ids = []
    for i in range(3):
        response = client.post(
            "/users/",
            json={"email": f"email_{i}@example.com", "password": "pass_{i}","name":"ono_{i}"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["email"] == f"email_{i}@example.com"
        assert "id" in data
        user_ids.append(data["id"])

    for user_id in user_ids:
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 200, response.text
        data = response.json()
        print(user_id,data["email"])
        assert data["id"] == user_id

    response = client.get(f"/users")
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) >= 3 


def test_update_user():
    response = client.post(
        "/users/",
        json={"email": "for_update@example.com", "password": "ono","name":"ono"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    user_id = data["id"]

    response = client.put(f"/users/{user_id}",
        json={"email": "updated@example.com", "name":"ono_updated","is_active":True},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "updated@example.com"
    assert data["name"] == "ono_updated"


import sys
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from fastapi.testclient import TestClient

#from database import Base
if True:  # 自動成形で順番が変えられないようにダミー処理
    sys.path.append("../../app")
    import models
    from main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite://"  # For inmemory

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool  # For inmemory
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

models.Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# ------------ USER --------------


def test_create_user():
    response = client.post(
        "/users/",
        json={
            "email": "deadpool@example.com",
            "password": "ono", "name": "ono"
        }
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
            json={
                "email": f"email_{i}@example.com",
                "password": "pass_{i}", "name": "ono_{i}"
            }
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
        print(user_id, data["email"])
        assert data["id"] == user_id

    response = client.get(f"/users")
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) >= 3

    response = client.get(f"/users/99999")
    assert response.status_code == 404, response.text


def test_update_user():
    response = client.post(
        "/users/",
        json={
            "email": "for_update@example.com",
            "password": "ono", "name": "ono"
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    user_id = data["id"]

    response = client.put(
        f"/users/{user_id}",
        json={
            "email": "updated@example.com",
            "name": "ono_updated",
            "is_active": True
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "updated@example.com"
    assert data["name"] == "ono_updated"

    response = client.put(
        f"/users/9999",
        json={"email": "updated@example.com",
              "name": "ono_updated",
              "is_active": True
              }
    )
    assert response.status_code == 404, response.text

# ------------ ORDERS --------------


def test_create_order():
    response = client.post(
        "/users/",
        json={
            "email": "order_user@example.com",
            "password": "ono",
            "name": "ono"
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    user_id = data["id"]

    print("user_id:", user_id)

    response = client.post(
        f"/users/{user_id}/orders/",
        json={
            "scode": "1111-1",
            "title": "test-title",
            "in_date": "2022-10-01",
            "person": "ono",
            "memo": "test-memo"
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["scode"] == "1111-1"
    assert data["title"] == "test-title"


def test_read_order():
    response = client.post(
        "/users/",
        json={
            "email": "order_read_user@example.com",
            "password": "ono",
            "name": "ono"
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    user_id = data["id"]

    print("user_id:", user_id)

    order_ids = []
    for i in range(3):
        response = client.post(
            f"/users/{user_id}/orders/",
            json={
                "scode": f"22222-{i}",
                "title": "test-title-{i}",
                "in_date": "2022-10-01",
                "person": "ono{i}",
                "memo": "test-memo{i}"
            }
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["scode"] == f"22222-{i}"
        assert "id" in data
        order_ids.append(data["id"])

    response = client.get(f"/orders/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) >= 3


def test_update_order():
    response = client.post(
        "/users/",
        json={
            "email": "for_update_order@example.com",
            "password": "ono",
            "name": "ono"
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    user_id = data["id"]

    response = client.post(
        f"/users/{user_id}/orders/",
        json={
            "scode": "44444-1",
            "title": "test-title-for-update",
            "in_date": "2022-10-01",
            "person": "ono",
            "memo": "test-memo-for-update"
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["scode"] == "44444-1"
    assert data["title"] == "test-title-for-update"

    order_id = data["id"]

    response = client.put(
        f"/orders/{order_id}",
        json={
            "scode": "44444-1-updated",
            "title": "test-title-for-update-updated",
            "in_date": "2022-10-01",
            "person": "ono-updated",
            "memo": "test-memo-for-update-updated"
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["scode"] == "44444-1-updated"
    assert data["title"] == "test-title-for-update-updated"

    response = client.put(
        f"/orders/9999",
        json={
            "scode": "44444-222-updated",
            "title": "test-title-for-update-updated",
            "in_date": "2022-10-01",
            "person": "ono-updated",
            "memo": "test-memo-for-update-updated"
        }
    )
    assert response.status_code == 404, response.text


def test_delete_order():
    response = client.post(
        "/users/",
        json={
            "email": "for_delete_order@example.com",
            "password": "ono",
            "name": "ono"
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    user_id = data["id"]

    response = client.post(
        f"/users/{user_id}/orders/",
        json={
            "scode": "55555-1",
            "title": "test-title-for-delete",
            "in_date": "2022-10-01",
            "person": "ono",
            "memo": "test-memo-for-delete"
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["scode"] == "55555-1"
    assert data["title"] == "test-title-for-delete"
    order_id = data["id"]

    response = client.delete(f"/orders/{order_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["scode"] == "55555-1"
    assert data["title"] == "test-title-for-delete"

    response = client.delete(f"/orders/9999")
    assert response.status_code == 404, response.text

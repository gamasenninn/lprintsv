import sys
from fastapi import FastAPI
from fastapi.testclient import TestClient
if True:  # 自動成形で順番が変えられないようにダミー処理
    sys.path.append("../../app")
    import models
    from main import app, get_db
    import schemas

app = FastAPI()

client = TestClient(app)

test_user_id = 1
test_order_id = "S-123"
test_order = schemas.OrderCreate(
    scode="S-123",
    title="Test Order",
    receipt_date="2023-03-21",
    person=1,
    memo="This is a test order.",
    status="open",
)

def test_create_order_for_user():
    response = client.post(
        f"/users/{test_user_id}/orders/",
        json=test_order.dict()
    )
    assert response.status_code == 200
    data = response.json()
    assert data["scode"] == test_order.scode
    assert data["title"] == test_order.title
    assert data["receipt_date"] == test_order.receipt_date
    assert data["person"] == test_order.person
    assert data["memo"] == test_order.memo
    assert data["status"] == test_order.status

def test_read_orders():
    response = client.get("/orders/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_read_orders_by_id():
    response = client.get(f"/orders/{test_order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_order_id

def test_update_order():
    update_data = schemas.OrderUpdate(
        scode="S-321",
        title="Updated Test Order",
        receipt_date="2023-03-22",
        person=2,
        memo="This is an updated test order.",
        status="closed",
    )
    response = client.put(
        f"/orders/{test_order_id}",
        json=update_data.dict(exclude_unset=True)
    )
    assert response.status_code == 200
    data = response.json()
    assert data["scode"] == update_data.scode
    assert data["title"] == update_data.title
    assert data["receipt_date"] == update_data.receipt_date
    assert data["person"] == update_data.person
    assert data["memo"] == update_data.memo
    assert data["status"] == update_data.status

def test_delete_order():
    response = client.delete(f"/orders/{test_order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "ok"

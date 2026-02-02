import pytest
from backend.app import app, in_memory_storage


@pytest.fixture
def client():
    """Provides a Flask test client with a clean storage state.
    
    Configures the app for testing, clears the in-memory storage,
    and yields a test client for making API requests.
    """
    app.config["TESTING"] = True
    app.config["DEBUG"] = False
    in_memory_storage.clear()
    with app.test_client() as client:
        yield client


def test_add_order_api_success(client):
    """Test successfully adding a new order via the API.
    
    Verifies that a POST request to /api/orders creates a new order
    and returns status 201 with the order data.
    """
    order_data = {
        "order_id": "API001",
        "item_name": "API Laptop",
        "quantity": 1,
        "customer_id": "APICUST001",
    }
    response = client.post("/api/orders", json=order_data)
    assert response.status_code == 201
    assert response.json["order_id"] == "API001"


def test_get_order_api_success(client):
    """Test successfully retrieving an existing order via the API.
    
    Creates an order, then verifies that a GET request to /api/orders/{order_id}
    returns status 200 with the correct order data.
    """
    client.post(
        "/api/orders",
        json={
            "order_id": "GET001",
            "item_name": "Test Item",
            "quantity": 1,
            "customer_id": "C1",
        },
    )
    response = client.get("/api/orders/GET001")
    assert response.status_code == 200
    assert response.json["order_id"] == "GET001"


def test_get_order_api_not_found(client):
    """Test retrieving a non-existent order returns 404.
    
    Verifies that a GET request for an order that doesn't exist
    returns status 404 (Not Found).
    """
    response = client.get("/api/orders/NONEXISTENT")
    assert response.status_code == 404


def test_update_order_status_api_success(client):
    """Test successfully updating an order's status via the API.
    
    Creates an order with default status, then verifies that a PUT request
    to /api/orders/{order_id}/status successfully updates the status
    and returns status 200 with the updated order.
    """
    client.post(
        "/api/orders",
        json={
            "order_id": "UPDATE001",
            "item_name": "Test Item",
            "quantity": 1,
            "customer_id": "C1",
        },
    )
    response = client.put(
        "/api/orders/UPDATE001/status", json={"new_status": "shipped"}
    )
    assert response.status_code == 200
    assert response.json["status"] == "shipped"


def test_list_all_orders_api_with_data(client):
    """Test listing all orders when multiple orders exist.
    
    Creates multiple orders, then verifies that a GET request to /api/orders
    returns status 200 with all orders in the response.
    """
    client.post(
        "/api/orders",
        json={
            "order_id": "LST001",
            "item_name": "Item A",
            "quantity": 1,
            "customer_id": "C1",
        },
    )
    client.post(
        "/api/orders",
        json={
            "order_id": "LST002",
            "item_name": "Item B",
            "quantity": 2,
            "customer_id": "C2",
        },
    )
    response = client.get("/api/orders")
    assert response.status_code == 200
    assert len(response.json) == 2


def test_list_orders_by_status_api_matching(client):
    """Test filtering orders by status via query parameter.
    
    Creates orders with different statuses, then verifies that a GET request
    to /api/orders?status=pending returns only orders with 'pending' status.
    """
    client.post(
        "/api/orders",
        json={
            "order_id": "S001",
            "item_name": "A",
            "quantity": 1,
            "customer_id": "C1",
            "status": "pending",
        },
    )
    client.post(
        "/api/orders",
        json={
            "order_id": "S002",
            "item_name": "B",
            "quantity": 2,
            "customer_id": "C2",
            "status": "shipped",
        },
    )
    response = client.get("/api/orders?status=pending")
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["order_id"] == "S001"


def test_delete_order_api_success(client):
    """Test successfully deleting an order via the API.
    
    Creates an order, then verifies that a DELETE request to /api/orders/{order_id}
    returns status 204 and that the order is no longer retrievable.
    """
    client.post(
        "/api/orders",
        json={
            "order_id": "DEL001",
            "item_name": "To Be Deleted",
            "quantity": 1,
            "customer_id": "C1",
        },
    )
    response = client.delete("/api/orders/DEL001")
    assert response.status_code == 204

    get_response = client.get("/api/orders/DEL001")
    assert get_response.status_code == 404
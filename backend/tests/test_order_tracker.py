import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---


@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock


@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)


# --- Unit Tests ---


def test_add_order_successfully(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")

    # We expect save_order to be called once
    mock_storage.save_order.assert_called_once()


def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(
        ValueError, match="Order with ID 'ORD_EXISTING' already exists."
    ):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")


def test_add_order_incomplete_data(order_tracker):
    """Tests that adding an order with incomplete data raises a TypeError."""
    with pytest.raises(
        TypeError,
        match="missing 1 required positional argument: 'customer_id'",
    ):
        order_tracker.add_order("ORD_INCOMPLETE", "Item", 1)


def test_get_order_by_id(order_tracker, mock_storage):
    """Tests retrieving an order by its ID."""
    # Setup the mock to return a specific order
    mock_storage.get_order.return_value = {
        "order_id": "ORD002",
        "item_name": "Phone",
        "quantity": 2,
        "customer_id": "CUST002",
        "status": "shipped",
    }

    order = order_tracker.get_order_by_id("ORD002")

    assert order["order_id"] == "ORD002"
    assert order["item_name"] == "Phone"
    assert order["quantity"] == 2
    assert order["customer_id"] == "CUST002"
    assert order["status"] == "shipped"
    mock_storage.get_order.assert_called_once_with("ORD002")


def test_get_order_by_id_not_found(order_tracker, mock_storage):
    """Tests retrieving an order by its ID when the order does not exist."""
    order = order_tracker.get_order_by_id("ORD999")

    assert order is None
    mock_storage.get_order.assert_called_once_with("ORD999")


def test_update_order_status(order_tracker, mock_storage):
    """Tests updating the status of an existing order."""
    # Setup the mock to return an existing order
    mock_storage.get_order.return_value = {
        "order_id": "ORD003",
        "item_name": "Tablet",
        "quantity": 1,
        "customer_id": "CUST003",
        "status": "pending",
    }

    order_tracker.update_order_status("ORD003", "shipped")

    # Verify that save_order was called with the updated status
    mock_storage.save_order.assert_called_once_with(
        "ORD003",
        {
            "order_id": "ORD003",
            "item_name": "Tablet",
            "quantity": 1,
            "customer_id": "CUST003",
            "status": "shipped",
        },
    )


def test_update_order_status_order_not_found(order_tracker, mock_storage):
    """Tests updating the status of a non-existing order raises ValueError."""

    with pytest.raises(
        ValueError, match="Order with ID 'ORD_NOT_EXIST' does not exist."
    ):
        order_tracker.update_order_status("ORD_NOT_EXIST", "shipped")


def test_update_order_status_status_not_found(order_tracker, mock_storage):
    """Tests updating the status when the status value is not correct."""
    # Setup the mock to return an existing order
    mock_storage.get_order.return_value = {
        "order_id": "ORD003",
        "item_name": "Tablet",
        "quantity": 1,
        "customer_id": "CUST003",
        "status": "pending",
    }

    with pytest.raises(
        ValueError, match="Status 'delivered' is not a valid status."
    ):
        order_tracker.update_order_status("ORD003", "delivered")


def test_list_all_orders(order_tracker, mock_storage):
    """Tests listing all orders."""
    # Setup the mock to return multiple orders
    mock_storage.get_all_orders.return_value = {
        "ORD001": {
            "order_id": "ORD001",
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUST001",
            "status": "pending",
        },
        "ORD002": {
            "order_id": "ORD002",
            "item_name": "Phone",
            "quantity": 2,
            "customer_id": "CUST002",
            "status": "shipped",
        },
    }

    orders = order_tracker.list_all_orders()

    assert len(orders) == 2
    assert orders["ORD001"]["item_name"] == "Laptop"
    assert orders["ORD002"]["item_name"] == "Phone"
    mock_storage.get_all_orders.assert_called_once()


def test_list_all_orders_by_status(order_tracker, mock_storage):
    """Tests listing orders filtered by status."""
    # Setup the mock to return multiple orders
    mock_storage.get_all_orders.return_value = {
        "ORD001": {
            "order_id": "ORD001",
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUST001",
            "status": "pending",
        },
        "ORD002": {
            "order_id": "ORD002",
            "item_name": "Phone",
            "quantity": 2,
            "customer_id": "CUST002",
            "status": "shipped",
        },
        "ORD003": {
            "order_id": "ORD003",
            "item_name": "Tablet",
            "quantity": 1,
            "customer_id": "CUST003",
            "status": "pending",
        },
    }

    orders = order_tracker.list_orders_by_status("pending")

    assert len(orders) == 2
    assert all(order["status"] == "pending" for order in orders)
    mock_storage.get_all_orders.assert_called_once()


def test_list_all_orders_by_status_no_matches(order_tracker, mock_storage):
    """Tests listing orders by status when no orders match the status."""
    # Setup the mock to return multiple orders
    mock_storage.get_all_orders.return_value = {
        "ORD001": {
            "order_id": "ORD001",
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUST001",
            "status": "pending",
        },
        "ORD002": {
            "order_id": "ORD002",
            "item_name": "Phone",
            "quantity": 2,
            "customer_id": "CUST002",
            "status": "shipped",
        },
    }

    orders = order_tracker.list_orders_by_status("processing")

    assert len(orders) == 0
    mock_storage.get_all_orders.assert_called_once()


def test_list_orders_by_status_invalid_status(order_tracker, mock_storage):
    """Tests listing orders by an invalid status returns empty list."""
    # Setup the mock to return multiple orders
    mock_storage.get_all_orders.return_value = {
        "ORD001": {
            "order_id": "ORD001",
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUST001",
            "status": "pending",
        },
        "ORD002": {
            "order_id": "ORD002",
            "item_name": "Phone",
            "quantity": 2,
            "customer_id": "CUST002",
            "status": "shipped",
        },
    }

    orders = order_tracker.list_orders_by_status("invalid")

    assert len(orders) == 0
    mock_storage.get_all_orders.assert_called_once()
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
    # This simulates the case where an order doesn't exist in storage
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    # This simulates an empty storage state
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
    # Call add_order with valid parameters
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")

    # Verify that save_order was called exactly once to persist the new order
    # This confirms the order was saved to storage
    mock_storage.save_order.assert_called_once()

    # Verify that the saved order data is correct
    mock_storage.save_order.assert_called_once_with(
        "ORD001",
        {
            "order_id": "ORD001",
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUST001",
            "status": "pending",  # Default status
        },
    )


def test_add_order_with_status_successfully(order_tracker, mock_storage):
    """Tests adding a new order with 'processing' status."""
    # Call add_order with valid parameters
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001", status="processing")

    # Verify that save_order was called exactly once to persist the new order
    # This confirms the order was saved to storage
    mock_storage.save_order.assert_called_once()

    # Verify that the saved order data is correct
    mock_storage.save_order.assert_called_once_with(
        "ORD001",
        {
            "order_id": "ORD001",
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUST001",
            "status": "processing",  # Status set upon creation
        },
    )


def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    # Configure the mock to simulate finding an existing order in storage
    # This triggers the duplicate order validation logic
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    # Attempt to add an order with the same ID should raise ValueError
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
    # Configure the mock to return a complete order dictionary
    # This simulates successfully finding an order in storage
    mock_storage.get_order.return_value = {
        "order_id": "ORD002",
        "item_name": "Phone",
        "quantity": 2,
        "customer_id": "CUST002",
        "status": "shipped",
    }

    order = order_tracker.get_order_by_id("ORD002")

    # Verify all order fields are correctly retrieved
    assert order["order_id"] == "ORD002"
    assert order["item_name"] == "Phone"
    assert order["quantity"] == 2
    assert order["customer_id"] == "CUST002"
    assert order["status"] == "shipped"
    # Confirm the storage was queried with the correct order ID
    mock_storage.get_order.assert_called_once_with("ORD002")


@pytest.mark.parametrize("order_id", ["", "   ", None])
def test_get_order_by_id_not_found(order_id, order_tracker, mock_storage):
    """Tests retrieving an order by its ID when the order does not exist."""
    # The mock's default return value is None (configured in fixture)
    order = order_tracker.get_order_by_id(order_id)

    # Should return None when order doesn't exist
    assert order is None
    # Verify the storage was queried with the correct ID
    mock_storage.get_order.assert_called_once_with(order_id)


@pytest.mark.parametrize("status", ["pending", "processing", "shipped"])
def test_update_order_status(status, order_tracker, mock_storage):
    """Tests updating the status of an existing order."""
    # Configure the mock to return an existing order with 'pending' status
    mock_storage.get_order.return_value = {
        "order_id": "ORD003",
        "item_name": "Tablet",
        "quantity": 1,
        "customer_id": "CUST003",
        "status": "pending",
    }

    # Update the order status from 'pending' to the parameterized status
    order_tracker.update_order_status("ORD003", status)

    # Verify that save_order was called with the complete updated order
    # The status should now be the parameterized status while other fields remain unchanged
    mock_storage.save_order.assert_called_once_with(
        "ORD003",
        {
            "order_id": "ORD003",
            "item_name": "Tablet",
            "quantity": 1,
            "customer_id": "CUST003",
            "status": status,
        },
    )


def test_update_order_status_order_not_found(order_tracker, mock_storage):
    """Tests updating the status of a non-existing order raises ValueError."""
    # Mock returns None by default (order not found)
    # Attempting to update a non-existent order should raise ValueError
    with pytest.raises(
        ValueError, match="Order with ID 'ORD_NOT_EXIST' does not exist."
    ):
        order_tracker.update_order_status("ORD_NOT_EXIST", "shipped")


def test_update_order_status_status_not_found(order_tracker, mock_storage):
    """Tests updating the status when the status value is not correct."""
    # Configure the mock to return an existing order
    mock_storage.get_order.return_value = {
        "order_id": "ORD003",
        "item_name": "Tablet",
        "quantity": 1,
        "customer_id": "CUST003",
        "status": "pending",
    }

    # Attempting to set an invalid status (not in allowed list) should raise AssertionError
    # 'delivered' is not a valid status in this system
    with pytest.raises(ValueError, match="'delivered' is not a valid OrderStatus"):
        order_tracker.update_order_status("ORD003", "delivered")


def test_list_all_orders(order_tracker, mock_storage):
    """Tests listing all orders."""
    # Configure the mock to return a dictionary with multiple orders
    # Keys are order IDs, values are complete order dictionaries
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

    # Verify the correct number of orders is returned
    assert len(orders) == 2
    # Spot-check that order data is correctly passed through
    assert orders[0]["order_id"] == "ORD001"
    assert orders[0]["item_name"] == "Laptop"
    assert orders[1]["order_id"] == "ORD002"
    assert orders[1]["item_name"] == "Phone"
    # Confirm storage method was called
    mock_storage.get_all_orders.assert_called_once()


def test_list_all_orders_by_status(order_tracker, mock_storage):
    """Tests listing orders filtered by status."""
    # Configure the mock with a mix of orders with different statuses
    # 2 orders have 'pending' status, 1 has 'shipped'
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

    # Filter for 'pending' orders only
    orders = order_tracker.list_orders_by_status("pending")

    # Should return only the 2 pending orders (ORD001 and ORD003)
    assert len(orders) == 2
    # Verify all returned orders have the requested status
    assert all(order["status"] == "pending" for order in orders)
    mock_storage.get_all_orders.assert_called_once()


def test_list_all_orders_by_status_no_matches(order_tracker, mock_storage):
    """Tests listing orders by status when no orders match the status."""
    # Configure the mock with orders that have 'pending' and 'shipped' statuses
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

    # Filter for 'processing' status - none of the orders have this status
    orders = order_tracker.list_orders_by_status("processing")

    # Should return an empty list when no orders match the filter
    assert len(orders) == 0
    mock_storage.get_all_orders.assert_called_once()


def test_list_orders_by_status_invalid_status(order_tracker, mock_storage):
    """Tests listing orders by an invalid status returns empty list."""
    # Configure the mock with valid orders
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

    # Filter with a completely invalid status (not in the system's allowed statuses)
    orders = order_tracker.list_orders_by_status("invalid")

    # Should return an empty list when filtering by an invalid status
    assert len(orders) == 0
    mock_storage.get_all_orders.assert_called_once()


def test_delete_order(order_tracker, mock_storage):
    """Tests deleting an existing order."""
    # Configure the mock to simulate that the order exists
    mock_storage.get_order.return_value = {
        "order_id": "ORD004",
        "item_name": "Monitor",
        "quantity": 1,
        "customer_id": "CUST004",
        "status": "processing",
    }

    # Call delete_order to remove the order
    order_tracker.delete_order("ORD004")

    # Verify that delete_order was called on the storage with the correct ID
    mock_storage.delete_order.assert_called_once_with("ORD004")


def test_delete_order_not_found(order_tracker, mock_storage):
    """Tests deleting a non-existing order raises ValueError."""
    # Mock returns None by default (order not found)
    # Attempting to delete a non-existent order should raise ValueError
    with pytest.raises(
        ValueError, match="Order with ID 'ORD_NOT_EXIST' does not exist."
    ):
        order_tracker.delete_order("ORD_NOT_EXIST")

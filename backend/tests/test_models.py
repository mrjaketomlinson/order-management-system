import pytest
from backend.models import Order, OrderStatus


def test_order_creation():
    """Test creating an Order instance with valid data.

    Verifies that an Order object is correctly instantiated
    with the provided attributes.
    """
    order = Order(
        order_id="ORD123", item_name="Laptop", quantity=2, customer_id="CUST456"
    )
    assert order.order_id == "ORD123"
    assert order.item_name == "Laptop"
    assert order.quantity == 2
    assert order.customer_id == "CUST456"
    assert order.status == "pending"


def test_order_creation_with_status():
    """Test creating an Order instance with a specific status.

    Verifies that an Order object is correctly instantiated
    with the provided status attribute.
    """
    order = Order(
        order_id="ORD123",
        item_name="Laptop",
        quantity=2,
        customer_id="CUST456",
        status=OrderStatus.SHIPPED,
    )
    assert order.order_id == "ORD123"
    assert order.item_name == "Laptop"
    assert order.quantity == 2
    assert order.customer_id == "CUST456"
    assert order.status == "shipped"


def test_order_creation_invalid_status():
    """Test creating an Order instance with an invalid status.

    Verifies that a ValueError is raised when an invalid
    status value is provided.
    """
    with pytest.raises(ValueError) as exc_info:
        Order(
            order_id="ORD123",
            item_name="Laptop",
            quantity=2,
            customer_id="CUST456",
            status="invalid_status",  # type: ignore
        )
    assert "invalid_status" in str(exc_info.value)


def test_order_to_dict():
    """Test converting an Order instance to a dictionary.

    Verifies that the to_dict method returns the correct
    dictionary representation of the Order object.
    """
    order = Order(
        order_id="ORD123", item_name="Laptop", quantity=2, customer_id="CUST456"
    )
    order_dict = order.to_dict()
    expected_dict = {
        "order_id": "ORD123",
        "item_name": "Laptop",
        "quantity": 2,
        "customer_id": "CUST456",
        "status": "pending",
    }
    assert order_dict == expected_dict


def test_order_from_dict():
    """Test creating an Order instance from a dictionary.

    Verifies that the from_dict static method correctly
    instantiates an Order object from a given dictionary.
    """
    order_data = {
        "order_id": "ORD123",
        "item_name": "Laptop",
        "quantity": 2,
        "customer_id": "CUST456",
        "status": "processing",
    }
    order = Order.from_dict(order_data)
    assert order.order_id == "ORD123"
    assert order.item_name == "Laptop"
    assert order.quantity == 2
    assert order.customer_id == "CUST456"
    assert order.status == "processing"


def test_order_from_dict_invalid_status():
    """Test creating an Order instance from a dictionary with invalid status.

    Verifies that the from_dict method raises a ValueError
    when provided with an invalid status value.
    """
    order_data = {
        "order_id": "ORD123",
        "item_name": "Laptop",
        "quantity": 2,
        "customer_id": "CUST456",
        "status": "invalid_status",
    }
    with pytest.raises(ValueError) as exc_info:
        Order.from_dict(order_data)
    assert "invalid_status" in str(exc_info.value)

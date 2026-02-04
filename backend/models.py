from dataclasses import dataclass
from enum import Enum


class OrderStatus(str, Enum):
    """Enumeration of possible order statuses."""

    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"


@dataclass
class Order:
    """Data model for an order in the order management system."""

    order_id: str
    item_name: str
    quantity: int
    customer_id: str
    status: OrderStatus = OrderStatus.PENDING

    def __post_init__(self):
        """Validate the Order instance after initialization."""
        if self.status not in OrderStatus:
            raise ValueError(f"Status '{self.status}' is not a valid status.")

    def to_dict(self) -> dict:
        """Convert the Order dataclass to a dictionary.

        Returns:
            dict: A dictionary representation of the Order.
        """
        return {
            "order_id": self.order_id,
            "item_name": self.item_name,
            "quantity": self.quantity,
            "customer_id": self.customer_id,
            "status": self.status.value,
        }

    @staticmethod
    def from_dict(data: dict) -> "Order":
        """Create an Order instance from a dictionary.

        Args:
            data: A dictionary containing order data.

        Returns:
            Order: An instance of the Order dataclass.
        """
        return Order(
            order_id=data["order_id"],
            item_name=data["item_name"],
            quantity=data["quantity"],
            customer_id=data["customer_id"],
            status=OrderStatus(data.get("status", "pending")),
        )

"""Simple in-memory storage implementation for orders.

Data stored here will be lost when the application restarts.
"""


class InMemoryStorage:
    """A simple in-memory implementation of the storage interface.

    Stores orders in a Python dictionary.
    """

    def __init__(self):
        """Initialize the in-memory storage with an empty dictionary."""
        self._orders = {}

    def save_order(self, order_id: str, order_data: dict):
        """Save an order to the in-memory storage."""
        self._orders[order_id] = order_data.copy()

    def get_order(self, order_id: str):
        """Retrieve an order by its ID."""
        return (
            self._orders.get(order_id, {}).copy()
            if self._orders.get(order_id)
            else None
        )

    def get_all_orders(self):
        """Retrieve all orders."""
        return {k: v.copy() for k, v in self._orders.items()}

    def delete_order(self, order_id: str):
        """Delete an order by its ID."""
        if order_id in self._orders:
            del self._orders[order_id]

    def clear(self):
        """Clear all orders from storage."""
        self._orders = {}

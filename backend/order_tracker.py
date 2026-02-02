# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.


class OrderTracker:
    """
    Manages customer orders, providing functionalities to add, update,
    and retrieve order information.
    """

    def __init__(self, storage):
        """Initialize the OrderTracker with a storage backend.
        
        Args:
            storage: Storage object that must implement save_order, get_order, and get_all_orders methods.
            
        Raises:
            TypeError: If storage doesn't implement required methods.
        """
        required_methods = ["save_order", "get_order", "get_all_orders"]
        for method in required_methods:
            if not hasattr(storage, method) or not callable(getattr(storage, method)):
                raise TypeError(
                    f"Storage object must implement a callable '{method}' method."
                )
        self.storage = storage
        self.valid_statuses = {"pending", "processing", "shipped"}

    def add_order(
        self,
        order_id: str,
        item_name: str,
        quantity: int,
        customer_id: str,
        status: str = "pending",
    ):
        """Add a new order to the system.
        
        Args:
            order_id: Unique identifier for the order.
            item_name: Name of the item being ordered.
            quantity: Number of items in the order.
            customer_id: Identifier for the customer placing the order.
            status: Order status (default: 'pending'). Must be one of: pending, processing, shipped.
            
        Raises:
            ValueError: If order_id already exists or status is invalid.
        """
        if self.storage.get_order(order_id):
            raise ValueError(f"Order with ID '{order_id}' already exists.")

        if status not in self.valid_statuses:
            raise ValueError(f"Status '{status}' is not a valid status.")

        order = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status,
        }
        self.storage.save_order(order_id, order)

    def get_order_by_id(self, order_id: str):
        """Retrieve an order by its ID.
        
        Args:
            order_id: The unique identifier of the order to retrieve.
            
        Returns:
            dict: The order object if found, None otherwise.
        """
        return self.storage.get_order(order_id)

    def update_order_status(self, order_id: str, new_status: str):
        """Update the status of an existing order.
        
        Args:
            order_id: The unique identifier of the order to update.
            new_status: The new status value. Must be one of: pending, processing, shipped.
            
        Raises:
            ValueError: If order doesn't exist or new_status is invalid.
        """
        order = self.storage.get_order(order_id)
        if not order:
            raise ValueError(f"Order with ID '{order_id}' does not exist.")
        if new_status not in self.valid_statuses:
            raise ValueError(f"Status '{new_status}' is not a valid status.")

        order["status"] = new_status
        self.storage.save_order(order_id, order)

    def list_all_orders(self):
        """Retrieve all orders in the system.
        
        Returns:
            dict: Dictionary of all orders, keyed by order_id.
        """
        return self.storage.get_all_orders()

    def list_orders_by_status(self, status: str):
        """Retrieve all orders with a specific status.
        
        Args:
            status: The status to filter by.
            
        Returns:
            list: List of order objects matching the specified status.
        """
        all_orders = self.storage.get_all_orders()
        return [order for order in all_orders.values() if order.get("status") == status]

    def delete_order(self, order_id: str):
        """Delete an order by its ID.
        
        Args:
            order_id: The unique identifier of the order to delete.
            
        Raises:
            ValueError: If order doesn't exist.
        """
        order = self.storage.get_order(order_id)
        if not order:
            raise ValueError(f"Order with ID '{order_id}' does not exist.")
        self.storage.delete_order(order_id)
from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker
from backend.in_memory_storage import InMemoryStorage
from backend.decorators import json_required

app = Flask(__name__, static_folder="../frontend")
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)


@app.route("/")
def serve_index():
    """Serve the main index.html page.

    Returns:
        HTML file: The application's main frontend page.
    """
    return send_from_directory(app.static_folder, "index.html")  # type: ignore


@app.route("/<path:filename>")
def serve_static(filename):
    """Serve static files (CSS, JavaScript, etc.).

    Args:
        filename: Path to the static file relative to the frontend folder.

    Returns:
        File: The requested static file.
    """
    return send_from_directory(app.static_folder, filename)  # type: ignore


@app.route("/api/orders", methods=["POST"])
@json_required
def add_order_api():
    """Create a new order.

    Expects JSON payload with required fields:
    - order_id: Unique identifier for the order
    - item_name: Name of the item being ordered
    - quantity: Number of items ordered
    - customer_id: Identifier for the customer
    - status: (optional) Order status, defaults to 'pending'

    Returns:
        JSON: The created order object with status 201 on success.
        JSON: Error message with status 400 if validation fails or order already exists.
    """
    order_json = request.get_json()
    required_fields = ["order_id", "item_name", "quantity", "customer_id"]
    missing_fields = []
    for field in required_fields:
        if field not in order_json:
            missing_fields.append(field)
    if missing_fields:
        return (
            jsonify(
                {"error": f"Missing required field(s): {', '.join(missing_fields)}"}
            ),
            400,
        )
    try:
        order_tracker.add_order(
            order_id=order_json["order_id"],
            item_name=order_json["item_name"],
            quantity=order_json["quantity"],
            customer_id=order_json["customer_id"],
            status=order_json.get("status", "pending"),
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(order_tracker.get_order_by_id(order_json["order_id"])), 201


@app.route("/api/orders/<string:order_id>", methods=["GET"])
def get_order_api(order_id):
    """Retrieve a specific order by its ID.

    Args:
        order_id: The unique identifier of the order to retrieve.

    Returns:
        JSON: The order object with status 200 if found.
        JSON: Error message with status 404 if order doesn't exist.
    """
    order = order_tracker.get_order_by_id(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order), 200


@app.route("/api/orders/<string:order_id>/status", methods=["PUT"])
@json_required
def update_order_status_api(order_id):
    """Update the status of an existing order.

    Args:
        order_id: The unique identifier of the order to update.

    Expects JSON payload with:
    - new_status: The new status value for the order

    Returns:
        JSON: The updated order object with status 200 on success.
        JSON: Error message with status 400 if new_status is missing.
        JSON: Error message with status 404 if order doesn't exist or status is invalid.
    """
    order_json = request.get_json()
    if "new_status" not in order_json:
        return jsonify({"error": "Missing required field: new_status"}), 400
    try:
        order_tracker.update_order_status(order_id, order_json["new_status"])
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    updated_order = order_tracker.get_order_by_id(order_id)
    return jsonify(updated_order), 200


@app.route("/api/orders", methods=["GET"])
def list_orders_api():
    """List all orders, optionally filtered by status.

    Query Parameters:
        status (optional): Filter orders by this status value.

    Returns:
        JSON: List of orders matching the filter (or all orders if no filter).
              Returns status 200.

    Examples:
        GET /api/orders - Returns all orders
        GET /api/orders?status=pending - Returns only pending orders
    """
    status_filter = request.args.get("status")
    if status_filter:
        orders = order_tracker.list_orders_by_status(status_filter)
        return jsonify(orders), 200
    else:
        orders = order_tracker.list_all_orders()
        return jsonify(list(orders.values())), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

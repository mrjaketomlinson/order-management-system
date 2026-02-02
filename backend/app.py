from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker
from backend.in_memory_storage import InMemoryStorage
from backend.decorators import json_required

app = Flask(__name__, static_folder="../frontend")
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)


@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")  # type: ignore


@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)  # type: ignore


@app.route("/api/orders", methods=["POST"])
@json_required
def add_order_api():
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
    order = order_tracker.get_order_by_id(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order), 200


@app.route("/api/orders/<string:order_id>/status", methods=["PUT"])
@json_required
def update_order_status_api(order_id):
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
    status_filter = request.args.get("status")
    if status_filter:
        orders = order_tracker.list_orders_by_status(status_filter)
        return jsonify(orders), 200
    else:
        orders = order_tracker.list_all_orders()
        return jsonify(list(orders.values())), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

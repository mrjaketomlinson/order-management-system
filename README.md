# Order Management System

A Flask-based REST API for managing customer orders with a simple web frontend. The system allows you to create, read, update, and delete orders with status tracking (pending, processing, shipped).

## Features

- Create and manage customer orders
- Track order status through lifecycle (pending -> processing -> shipped)
- RESTful API with JSON responses
- Simple web interface for order management
- In-memory storage (data persists during runtime only)
- Comprehensive test coverage

## Repository Structure

```
order-management-system/
├── backend/                  # Backend Python package
│   ├── app.py               # Flask application with API routes
│   ├── order_tracker.py     # Core business logic for order management
│   ├── in_memory_storage.py # In-memory storage implementation
│   ├── decorators.py        # Custom decorators (JSON validation, etc.)
│   └── tests/               # Test suite
│       ├── test_api.py      # API endpoint tests
│       └── test_order_tracker.py  # Business logic tests
├── frontend/                 # Static frontend files
│   ├── index.html           # Main HTML page
│   ├── css/                 # Stylesheets
│   └── js/                  # JavaScript files
├── docs/                     # Documentation
├── pyproject.toml           # Project dependencies and metadata
├── pytest.ini               # Pytest configuration
└── README.md                # This file
```

## Architecture

The system follows a layered architecture:

1. **Presentation Layer** (`app.py`): Flask routes handling HTTP requests/responses
2. **Business Logic Layer** (`order_tracker.py`): Core order management logic
3. **Data Access Layer** (`in_memory_storage.py`): Storage abstraction

This separation allows for easy replacement of the storage backend (e.g., database) without changing business logic.


## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd order-management-system
```

2. Install dependencies using `uv` (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -e .
```

## Running the Application

Start the Flask development server:

```bash
uv run python -m backend.app
```

The application will be available at `http://localhost:5000`

- Frontend UI: `http://localhost:5000/`
- API Base URL: `http://localhost:5000/api/`

## Running Tests

Run the full test suite:

```bash
uv run pytest
```

Run with coverage report:

```bash
uv run pytest --cov=backend --cov-report=html
```

## API Overview

### Base URL
`http://localhost:5000`

### Endpoints

#### Create Order
```http
POST /api/orders
Content-Type: application/json

{
  "order_id": "ORD-001",
  "item_name": "Laptop",
  "quantity": 2,
  "customer_id": "CUST-123",
  "status": "pending"  // optional, defaults to "pending"
}
```

**Response**: `201 Created`
```json
{
  "order_id": "ORD-001",
  "item_name": "Laptop",
  "quantity": 2,
  "customer_id": "CUST-123",
  "status": "pending"
}
```

#### Get Order by ID
```http
GET /api/orders/{order_id}
```

**Response**: `200 OK`
```json
{
  "order_id": "ORD-001",
  "item_name": "Laptop",
  "quantity": 2,
  "customer_id": "CUST-123",
  "status": "pending"
}
```

#### List All Orders
```http
GET /api/orders
```

**Optional Query Parameters**:
- `status`: Filter by order status (e.g., `?status=pending`)

**Response**: `200 OK`
```json
[
  {
    "order_id": "ORD-001",
    "item_name": "Laptop",
    "quantity": 2,
    "customer_id": "CUST-123",
    "status": "pending"
  },
  {
    "order_id": "ORD-002",
    "item_name": "Mouse",
    "quantity": 5,
    "customer_id": "CUST-456",
    "status": "shipped"
  }
]
```

#### Update Order Status
```http
PUT /api/orders/{order_id}/status
Content-Type: application/json

{
  "new_status": "processing"
}
```

**Valid statuses**: `pending`, `processing`, `shipped`

**Response**: `200 OK`
```json
{
  "order_id": "ORD-001",
  "item_name": "Laptop",
  "quantity": 2,
  "customer_id": "CUST-123",
  "status": "processing"
}
```

#### Delete Order
```http
DELETE /api/orders/{order_id}
```

**Response**: `204 No Content`

### Sample curl Commands

**Create an order:**
```bash
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "ORD-001",
    "item_name": "Laptop",
    "quantity": 2,
    "customer_id": "CUST-123"
  }'
```

**Get an order:**
```bash
curl http://localhost:5000/api/orders/ORD-001
```

**List all orders:**
```bash
curl http://localhost:5000/api/orders
```

**List orders by status:**
```bash
curl http://localhost:5000/api/orders?status=pending
```

**Update order status:**
```bash
curl -X PUT http://localhost:5000/api/orders/ORD-001/status \
  -H "Content-Type: application/json" \
  -d '{"new_status": "processing"}'
```

**Delete an order:**
```bash
curl -X DELETE http://localhost:5000/api/orders/ORD-001
```

## Error Responses

The API returns appropriate HTTP status codes and JSON error messages:

- `400 Bad Request`: Missing required fields or invalid data
- `404 Not Found`: Order does not exist

Example error response:
```json
{
  "error": "Order with ID 'ORD-001' already exists."
}
```

## Project Reflection

- Because the frontend forms only allowed three statuses, I limited the acceptable statuses when creating and updating orders to those available in the frontend. This is fine, given the size/scope of the project, but could be enhanced if the statuses were more centrally controlled so you wouldn't have to update them in several places.
- Adding in the DELETE functionality was straightforward and allowed me to use TDD for an entire feature, which was great. By contrast, adding in the API endpoint logic, because the tests were already there, didn't give me the "full experience" of red, green, refactor. So, having something implemented from scratch was a nice addition to the project.
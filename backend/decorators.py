from functools import wraps
from flask import request, abort


def json_required(f):
    """Decorator to ensure that the request contains JSON data, returns 415 error if not."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            abort(415, description="Content-Type must be application/json")
        return f(*args, **kwargs)

    return decorated_function

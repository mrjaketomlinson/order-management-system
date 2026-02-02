from functools import wraps
from flask import request, abort


def json_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            abort(415, description="Content-Type must be application/json")
        return f(*args, **kwargs)

    return decorated_function

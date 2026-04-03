import os
from functools import wraps

import jwt
from flask import jsonify, request


def require_bearer_jwt(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "missing_bearer_token"}), 401

        token = auth.split(" ", 1)[1].strip()
        try:
            jwt.decode(token, os.getenv("SECRET_KEY", "dev-change-me"), algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return jsonify({"error": "invalid_token"}), 401

        return fn(*args, **kwargs)

    return wrapper

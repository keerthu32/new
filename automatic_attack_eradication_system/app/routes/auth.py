import datetime as dt
import os

import jwt
from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash

from app.models.user import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.post("/token")
def token():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid_credentials"}), 401

    payload = {
        "sub": user.username,
        "admin": bool(user.is_admin),
        "exp": dt.datetime.utcnow() + dt.timedelta(minutes=int(os.getenv("JWT_EXPIRES_MINUTES", "60"))),
    }
    token = jwt.encode(payload, os.getenv("SECRET_KEY", "dev-change-me"), algorithm="HS256")
    return jsonify({"token": token})

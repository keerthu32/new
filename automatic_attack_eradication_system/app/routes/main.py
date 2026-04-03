from flask import Blueprint, jsonify

bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    return jsonify({"service": "automatic-attack-eradication-system", "status": "ok"})


@bp.get("/health")
def health():
    return jsonify({"status": "healthy"})

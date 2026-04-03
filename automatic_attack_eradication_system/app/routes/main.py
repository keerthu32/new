from flask import Blueprint, jsonify

bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    return {
        "name": "Automatic Attack Eradication System",
        "status": "running",
        "message": "Service is up. Use /health for health checks and /auth/token + /api/ingest for telemetry.",
        "endpoints": {
            "health": "/health",
            "token": "/auth/token",
            "ingest": "/api/ingest",
            "attacks": "/api/attacks",
        },
    }


@bp.get("/health")
def health():
    return jsonify({"status": "healthy"})

import json
from flask import Blueprint, current_app, jsonify, request

from app import db
from app.models.attack_log import AttackLog
from app.services.attack_detector import AttackDetector
from app.services.incident_response import IncidentResponse
from app.utils.auth import require_bearer_jwt

bp = Blueprint("api", __name__, url_prefix="/api")

detector = AttackDetector()
responder = IncidentResponse()


@bp.post("/ingest")
@require_bearer_jwt
def ingest():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "missing_payload"}), 400

    result = detector.analyze_traffic(payload)
    if not result["is_attack"]:
        return jsonify({"status": "clean", "score": result["score"]})

    log = AttackLog(
        source_ip=result.get("source_ip"),
        target_ip=result.get("target_ip"),
        attack_type=result["attack_type"],
        severity=result["severity"],
        score=result["score"],
        payload_excerpt=(payload.get("payload", "")[:300] if isinstance(payload, dict) else ""),
        details_json=json.dumps(result.get("details", {})),
    )
    db.session.add(log)
    db.session.commit()

    actions = responder.auto_respond(log)
    current_app.logger.warning("attack_detected id=%s type=%s severity=%s", log.id, log.attack_type, log.severity)
    return jsonify({"status": "attack_detected", "attack_id": log.id, "analysis": result, "actions": actions})


@bp.get("/attacks")
@require_bearer_jwt
def attacks():
    rows = AttackLog.query.order_by(AttackLog.created_at.desc()).limit(100).all()
    return jsonify({"attacks": [r.to_dict() for r in rows]})

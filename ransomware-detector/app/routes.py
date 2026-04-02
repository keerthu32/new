from __future__ import annotations

from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, render_template

from .detector import RansomwareDetector
from .monitor import LocalSystemMonitor

bp = Blueprint("main", __name__)

_detector: RansomwareDetector | None = None


def get_detector() -> RansomwareDetector:
    global _detector
    if _detector is None:
        _detector = RansomwareDetector(current_app.config["MODEL_RANDOM_STATE"])
    return _detector


@bp.get("/")
def index():
    return render_template("index.html")


@bp.get("/api/scan")
def run_scan():
    monitor = LocalSystemMonitor(
        max_files=current_app.config["MAX_FILES_PER_SCAN"],
        entropy_threshold=current_app.config["ENTROPY_THRESHOLD"],
    )
    summary = monitor.scan(current_app.config["SCAN_ROOT"])
    prediction = get_detector().predict(summary)
    prediction["scanned_at_utc"] = datetime.now(timezone.utc).isoformat()
    prediction["scan_root"] = current_app.config["SCAN_ROOT"]

    return jsonify(prediction)

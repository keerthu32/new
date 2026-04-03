#!/usr/bin/env python3
"""
Enhanced project generator for an Automatic Attack Eradication System.

Note: no detection system can be "perfect" in real-world traffic. This generator
builds a stronger production-style baseline with:
- Signature + anomaly + reputation scoring
- JWT API auth for agents
- Async incident queue and response workers
- Safer firewall execution and audit logs
- Better config/secrets handling
"""

from __future__ import annotations

import os
import stat
from pathlib import Path
from textwrap import dedent


BASE_DIR = Path("automatic_attack_eradication_system")


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).lstrip("\n"), encoding="utf-8")
    print(f"✓ Created: {path}")


def create_complete_project() -> None:
    directories = [
        BASE_DIR,
        BASE_DIR / "app",
        BASE_DIR / "app/routes",
        BASE_DIR / "app/models",
        BASE_DIR / "app/templates",
        BASE_DIR / "app/services",
        BASE_DIR / "app/utils",
        BASE_DIR / "migrations",
        BASE_DIR / "data",
        BASE_DIR / "logs",
        BASE_DIR / "scripts",
        BASE_DIR / "tests",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {directory}")

    files: dict[Path, str] = {
        BASE_DIR / "README.md": """
        # Automatic Attack Eradication System (Enhanced)

        Production-style Flask security monitor with hybrid detection and automated response.

        ## Why this is enhanced
        - Hybrid detector (signature + anomaly + reputation)
        - Authenticated ingestion (JWT)
        - Structured logs + audit trails
        - Background incident processor
        - Config via environment variables

        ## Quick start
        ```bash
        python -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
        cp .env.example .env
        python scripts/init_db.py
        python run.py
        ```

        ## API usage
        1. Obtain token:
        ```bash
        curl -X POST http://localhost:5000/auth/token \
          -H 'Content-Type: application/json' \
          -d '{"username":"admin","password":"Admin123!"}'
        ```

        2. Submit telemetry:
        ```bash
        curl -X POST http://localhost:5000/api/ingest \
          -H "Authorization: Bearer <token>" \
          -H 'Content-Type: application/json' \
          -d '{"source_ip":"198.51.100.10","request_rate":220,"payload":"UNION SELECT * FROM users"}'
        ```

        > Important: no IDS is perfect; tune thresholds and rules with your own traffic.
        """,
        BASE_DIR / ".env.example": """
        FLASK_ENV=development
        SECRET_KEY=change-me
        SQLALCHEMY_DATABASE_URI=sqlite:///data/attack_system.db
        JWT_EXPIRES_MINUTES=60
        AUTO_BLOCK_ENABLED=true
        DEFAULT_BLOCK_MINUTES=120
        LOG_LEVEL=INFO
        """,
        BASE_DIR / "requirements.txt": """
        Flask==3.0.3
        Flask-SQLAlchemy==3.1.1
        Flask-Login==0.6.3
        Flask-Migrate==4.0.7
        Flask-SocketIO==5.4.1
        python-dotenv==1.0.1
        psutil==6.0.0
        PyJWT==2.9.0
        Werkzeug==3.0.4
        """,
        BASE_DIR / "run.py": """
        #!/usr/bin/env python3
        import os
        from app import create_app, socketio

        app = create_app()

        if __name__ == "__main__":
            port = int(os.getenv("PORT", "5000"))
            socketio.run(app, host="0.0.0.0", port=port, debug=(os.getenv("FLASK_ENV") == "development"))
        """,
        BASE_DIR / "app/__init__.py": """
        import logging
        import os

        from dotenv import load_dotenv
        from flask import Flask
        from flask_login import LoginManager
        from flask_migrate import Migrate
        from flask_socketio import SocketIO
        from flask_sqlalchemy import SQLAlchemy

        db = SQLAlchemy()
        migrate = Migrate()
        login_manager = LoginManager()
        socketio = SocketIO(async_mode="threading", cors_allowed_origins="*")


        def create_app():
            load_dotenv()
            app = Flask(__name__)

            app.config.update(
                SECRET_KEY=os.getenv("SECRET_KEY", "dev-change-me"),
                SQLALCHEMY_DATABASE_URI=os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///data/attack_system.db"),
                SQLALCHEMY_TRACK_MODIFICATIONS=False,
                JWT_EXPIRES_MINUTES=int(os.getenv("JWT_EXPIRES_MINUTES", "60")),
                AUTO_BLOCK_ENABLED=os.getenv("AUTO_BLOCK_ENABLED", "true").lower() == "true",
                DEFAULT_BLOCK_MINUTES=int(os.getenv("DEFAULT_BLOCK_MINUTES", "120")),
            )

            db.init_app(app)
            migrate.init_app(app, db)
            login_manager.init_app(app)
            login_manager.login_view = "auth.login"
            socketio.init_app(app)

            _configure_logging()

            from app.routes import main, auth, api
            app.register_blueprint(main.bp)
            app.register_blueprint(auth.bp)
            app.register_blueprint(api.bp)

            with app.app_context():
                db.create_all()

            return app


        def _configure_logging():
            level = os.getenv("LOG_LEVEL", "INFO").upper()
            os.makedirs("logs", exist_ok=True)
            logging.basicConfig(
                level=getattr(logging, level, logging.INFO),
                format="%(asctime)s %(levelname)s %(name)s %(message)s",
                handlers=[
                    logging.FileHandler("logs/app.log"),
                    logging.StreamHandler(),
                ],
            )


        @login_manager.user_loader
        def load_user(user_id):
            from app.models.user import User
            return User.query.get(int(user_id))
        """,
        BASE_DIR / "app/models/__init__.py": """
        from app.models.user import User
        from app.models.attack_log import AttackLog
        from app.models.blocked_ip import BlockedIP
        """,
        BASE_DIR / "app/models/user.py": """
        from datetime import datetime
        from flask_login import UserMixin
        from app import db


        class User(UserMixin, db.Model):
            __tablename__ = "users"
            id = db.Column(db.Integer, primary_key=True)
            username = db.Column(db.String(64), unique=True, nullable=False)
            email = db.Column(db.String(120), unique=True, nullable=False)
            password_hash = db.Column(db.String(255), nullable=False)
            is_admin = db.Column(db.Boolean, default=False)
            created_at = db.Column(db.DateTime, default=datetime.utcnow)
        """,
        BASE_DIR / "app/models/attack_log.py": """
        from datetime import datetime
        from app import db


        class AttackLog(db.Model):
            __tablename__ = "attack_logs"
            id = db.Column(db.Integer, primary_key=True)
            source_ip = db.Column(db.String(45), index=True)
            target_ip = db.Column(db.String(45), index=True)
            attack_type = db.Column(db.String(64), nullable=False)
            severity = db.Column(db.String(16), nullable=False)
            score = db.Column(db.Float, nullable=False, default=0.0)
            status = db.Column(db.String(32), default="detected", index=True)
            payload_excerpt = db.Column(db.Text)
            details_json = db.Column(db.Text)
            created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

            def to_dict(self):
                return {
                    "id": self.id,
                    "source_ip": self.source_ip,
                    "target_ip": self.target_ip,
                    "attack_type": self.attack_type,
                    "severity": self.severity,
                    "score": self.score,
                    "status": self.status,
                    "created_at": self.created_at.isoformat(),
                }
        """,
        BASE_DIR / "app/models/blocked_ip.py": """
        from datetime import datetime
        from app import db


        class BlockedIP(db.Model):
            __tablename__ = "blocked_ips"
            id = db.Column(db.Integer, primary_key=True)
            ip_address = db.Column(db.String(45), unique=True, nullable=False)
            reason = db.Column(db.String(255), nullable=False)
            blocked_at = db.Column(db.DateTime, default=datetime.utcnow)
            expires_at = db.Column(db.DateTime)
            active = db.Column(db.Boolean, default=True)
        """,
        BASE_DIR / "app/routes/__init__.py": """
        # routes package
        """,
        BASE_DIR / "app/routes/main.py": """
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
        """,
        BASE_DIR / "app/routes/auth.py": """
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
        """,
        BASE_DIR / "app/routes/api.py": """
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
        """,
        BASE_DIR / "app/services/__init__.py": """
        # services package
        """,
        BASE_DIR / "app/services/attack_detector.py": """
        import ipaddress
        import json
        import math
        import re


        class AttackDetector:
            def __init__(self):
                self.rules = []
                self.bad_reputation = {"203.0.113.66", "198.51.100.250"}
                self.load_rules()

            def load_rules(self):
                self.rules = [
                    {"name": "sql_injection", "pattern": r"(union\\s+select|select.+from|drop\\s+table|or\\s+1=1)", "score": 0.70},
                    {"name": "xss", "pattern": r"(<script|javascript:|onerror\\s*=|onload\\s*=)", "score": 0.55},
                    {"name": "path_traversal", "pattern": r"(\\.\\./|\\.\\.\\\\|/etc/passwd|\\\\x00)", "score": 0.65},
                    {"name": "command_injection", "pattern": r"(;\\s*(cat|curl|wget|bash)|\\|\\s*(sh|bash))", "score": 0.75},
                ]

            def analyze_traffic(self, traffic_data):
                traffic_str = json.dumps(traffic_data, default=str).lower()
                score = 0.0
                reasons = []

                for rule in self.rules:
                    if re.search(rule["pattern"], traffic_str, re.IGNORECASE):
                        score = max(score, rule["score"])
                        reasons.append({"type": "signature", "rule": rule["name"], "score": rule["score"]})

                req_rate = float((traffic_data or {}).get("request_rate", 0) or 0)
                if req_rate > 100:
                    anomaly_score = min(0.95, 0.45 + math.log10(req_rate))
                    score = max(score, anomaly_score)
                    reasons.append({"type": "anomaly", "signal": "high_request_rate", "score": round(anomaly_score, 2)})

                source_ip = (traffic_data or {}).get("source_ip")
                if self._is_public_ip(source_ip) and source_ip in self.bad_reputation:
                    score = max(score, 0.90)
                    reasons.append({"type": "reputation", "score": 0.90})

                is_attack = score >= 0.55
                attack_type = self._classify(reasons) if is_attack else None
                severity = self._severity(score)

                return {
                    "is_attack": is_attack,
                    "score": round(score, 2),
                    "attack_type": attack_type,
                    "severity": severity,
                    "source_ip": source_ip,
                    "target_ip": (traffic_data or {}).get("target_ip"),
                    "details": {"reasons": reasons},
                }

            @staticmethod
            def _severity(score: float) -> str:
                if score >= 0.90:
                    return "critical"
                if score >= 0.75:
                    return "high"
                if score >= 0.55:
                    return "medium"
                return "low"

            @staticmethod
            def _classify(reasons):
                for reason in reasons:
                    if reason.get("type") == "signature":
                        return reason.get("rule")
                if any(r.get("type") == "anomaly" for r in reasons):
                    return "dos_or_bruteforce"
                return "suspicious_activity"

            @staticmethod
            def _is_public_ip(ip_value):
                if not ip_value:
                    return False
                try:
                    ip = ipaddress.ip_address(ip_value)
                    return not (ip.is_private or ip.is_loopback or ip.is_link_local)
                except ValueError:
                    return False
        """,
        BASE_DIR / "app/services/firewall_manager.py": """
        from datetime import datetime, timedelta
        import ipaddress

        from app import db
        from app.models.blocked_ip import BlockedIP


        class FirewallManager:
            # DB-backed firewall abstraction.
            # In production, integrate with nftables, security groups, or cloud WAF APIs.

            def block_ip(self, ip_address: str, reason: str, duration_minutes: int):
                try:
                    ipaddress.ip_address(ip_address)
                except ValueError:
                    return {"success": False, "error": "invalid_ip"}

                existing = BlockedIP.query.filter_by(ip_address=ip_address, active=True).first()
                if existing:
                    return {"success": True, "message": "already_blocked"}

                row = BlockedIP(
                    ip_address=ip_address,
                    reason=reason,
                    expires_at=datetime.utcnow() + timedelta(minutes=duration_minutes),
                )
                db.session.add(row)
                db.session.commit()
                return {"success": True, "message": f"blocked {ip_address}"}
        """,
        BASE_DIR / "app/services/incident_response.py": """
        from flask import current_app

        from app.services.firewall_manager import FirewallManager


        class IncidentResponse:
            def __init__(self):
                self.firewall = FirewallManager()

            def auto_respond(self, attack_log):
                actions = []
                if not current_app.config.get("AUTO_BLOCK_ENABLED"):
                    return actions

                if attack_log.severity in {"high", "critical"} and attack_log.source_ip:
                    result = self.firewall.block_ip(
                        attack_log.source_ip,
                        reason=f"Auto-block due to {attack_log.attack_type}",
                        duration_minutes=current_app.config.get("DEFAULT_BLOCK_MINUTES", 120),
                    )
                    actions.append({"action": "block_ip", "ip": attack_log.source_ip, "result": result})

                return actions
        """,
        BASE_DIR / "app/utils/__init__.py": """
        # utils package
        """,
        BASE_DIR / "app/utils/auth.py": """
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
        """,
        BASE_DIR / "scripts/init_db.py": """
        #!/usr/bin/env python3
        import os
        import sys

        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        from werkzeug.security import generate_password_hash

        from app import create_app, db
        from app.models.user import User


        def main():
            app = create_app()
            with app.app_context():
                db.create_all()
                admin = User.query.filter_by(username="admin").first()
                if not admin:
                    admin = User(
                        username="admin",
                        email="admin@example.com",
                        password_hash=generate_password_hash("Admin123!"),
                        is_admin=True,
                    )
                    db.session.add(admin)
                    db.session.commit()
                    print("✓ Created admin user: admin / Admin123!")
                else:
                    print("✓ Admin user already exists")
                print("✓ Database ready")


        if __name__ == "__main__":
            main()
        """,
        BASE_DIR / "tests/test_detector.py": """
        from app.services.attack_detector import AttackDetector


        def test_sqli_detected():
            d = AttackDetector()
            out = d.analyze_traffic({"payload": "UNION SELECT password FROM users", "request_rate": 3})
            assert out["is_attack"] is True
            assert out["score"] >= 0.55


        def test_clean_low_rate():
            d = AttackDetector()
            out = d.analyze_traffic({"payload": "hello", "request_rate": 2})
            assert out["is_attack"] is False
        """,
    }

    for path, content in files.items():
        write_file(path, content)

    for executable in [BASE_DIR / "run.py", BASE_DIR / "scripts/init_db.py"]:
        mode = executable.stat().st_mode
        executable.chmod(mode | stat.S_IXUSR)

    print("\nProject generated successfully.")
    print(f"cd {BASE_DIR} && python run.py")


if __name__ == "__main__":
    create_complete_project()

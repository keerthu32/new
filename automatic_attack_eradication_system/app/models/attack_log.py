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

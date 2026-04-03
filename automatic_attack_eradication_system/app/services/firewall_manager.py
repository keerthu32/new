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

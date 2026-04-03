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

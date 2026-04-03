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
            {"name": "sql_injection", "pattern": r"(union\s+select|select.+from|drop\s+table|or\s+1=1)", "score": 0.70},
            {"name": "xss", "pattern": r"(<script|javascript:|onerror\s*=|onload\s*=)", "score": 0.55},
            {"name": "path_traversal", "pattern": r"(\.\./|\.\.\\|/etc/passwd|\\x00)", "score": 0.65},
            {"name": "command_injection", "pattern": r"(;\s*(cat|curl|wget|bash)|\|\s*(sh|bash))", "score": 0.75},
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

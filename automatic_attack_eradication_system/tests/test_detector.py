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

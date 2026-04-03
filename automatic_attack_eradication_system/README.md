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
curl -X POST http://localhost:5000/auth/token           -H 'Content-Type: application/json'           -d '{"username":"admin","password":"Admin123!"}'
```

2. Submit telemetry:
```bash
curl -X POST http://localhost:5000/api/ingest           -H "Authorization: Bearer <token>"           -H 'Content-Type: application/json'           -d '{"source_ip":"198.51.100.10","request_rate":220,"payload":"UNION SELECT * FROM users"}'
```

> Important: no IDS is perfect; tune thresholds and rules with your own traffic.

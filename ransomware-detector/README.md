# Ransomware Detector (Flask)

A high-level Flask application that demonstrates **local ransomware signal detection** with:

- Local file-system scan (extensions, ransom-note names, entropy checks)
- ML-based risk scoring using a **Random Forest** model
- Dashboard view and risk trend chart
- JSON API endpoint for automation

## Project structure

```text
ransomware-detector/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── monitor.py
│   ├── detector.py
│   └── config.py
├── templates/
│   └── index.html
├── static/
│   └── chart.js
├── run.py
├── requirements.txt
└── README.md
```

## Important note

This project is a **defensive demo**. It does not replace enterprise EDR/AV tools. It provides heuristic + ML signals for educational and prototype use.

## Setup

```bash
cd ransomware-detector
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Then open: `http://127.0.0.1:5000`

## API

### `GET /api/scan`

Returns current scan findings and model risk score:

```json
{
  "risk_probability": 0.14,
  "risk_label": "low",
  "model": {
    "algorithm": "RandomForestClassifier",
    "accuracy": 0.98
  },
  "scan": {
    "files_scanned": 1500,
    "suspicious_extensions": 2,
    "suspicious_notes": 0,
    "high_entropy_files": 8,
    "avg_entropy": 5.31
  },
  "scanned_at_utc": "2026-04-02T00:00:00+00:00",
  "scan_root": "/home/your-user"
}
```

## Tuning

Edit `app/config.py`:

- `SCAN_ROOT` -> which local path to scan
- `MAX_FILES_PER_SCAN` -> cap for performance
- `ENTROPY_THRESHOLD` -> sensitivity for encrypted-like files

## How Random Forest accuracy is shown

At startup, the app trains a Random Forest on synthetic benign/malicious behavior features:

1. suspicious extension count
2. suspicious note count
3. high entropy file count
4. average entropy

It performs a train/test split and exposes test `accuracy` in both API and dashboard.

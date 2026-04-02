from pathlib import Path


class Config:
    SECRET_KEY = "ransomware-detector-dev"
    SCAN_ROOT = str(Path.home())
    MAX_FILES_PER_SCAN = 1500
    ENTROPY_THRESHOLD = 7.2
    MODEL_RANDOM_STATE = 42

from __future__ import annotations

import math
import os
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

SUSPICIOUS_EXTENSIONS = {
    ".locked",
    ".encrypted",
    ".crypt",
    ".crypto",
    ".enc",
    ".wncry",
}

SUSPICIOUS_FILENAMES = {
    "readme_for_decrypt.txt",
    "decrypt_instructions.txt",
    "how_to_restore_files.txt",
    "restore_files.txt",
}


@dataclass
class ScanSummary:
    files_scanned: int
    suspicious_extensions: int
    suspicious_notes: int
    high_entropy_files: int
    avg_entropy: float


class LocalSystemMonitor:
    """Performs lightweight local scans for ransomware indicators."""

    def __init__(self, max_files: int, entropy_threshold: float) -> None:
        self.max_files = max_files
        self.entropy_threshold = entropy_threshold

    def scan(self, root_path: str) -> ScanSummary:
        files_scanned = 0
        suspicious_extensions = 0
        suspicious_notes = 0
        high_entropy_files = 0
        entropy_sum = 0.0

        root = Path(root_path).expanduser()
        for base, _, files in os.walk(root):
            if files_scanned >= self.max_files:
                break

            base_path = Path(base)
            for file_name in files:
                if files_scanned >= self.max_files:
                    break

                file_path = base_path / file_name
                if self._should_skip(file_path):
                    continue

                files_scanned += 1
                lower_name = file_name.lower()
                ext = file_path.suffix.lower()

                if ext in SUSPICIOUS_EXTENSIONS:
                    suspicious_extensions += 1
                if lower_name in SUSPICIOUS_FILENAMES:
                    suspicious_notes += 1

                entropy = self._file_entropy(file_path)
                entropy_sum += entropy
                if entropy >= self.entropy_threshold:
                    high_entropy_files += 1

        avg_entropy = entropy_sum / files_scanned if files_scanned else 0.0
        return ScanSummary(
            files_scanned=files_scanned,
            suspicious_extensions=suspicious_extensions,
            suspicious_notes=suspicious_notes,
            high_entropy_files=high_entropy_files,
            avg_entropy=round(avg_entropy, 4),
        )

    @staticmethod
    def _should_skip(path: Path) -> bool:
        if not path.exists() or not path.is_file():
            return True
        try:
            return path.stat().st_size == 0 or path.stat().st_size > 5_000_000
        except OSError:
            return True

    @staticmethod
    def _file_entropy(path: Path) -> float:
        try:
            data = path.read_bytes()[:4096]
        except OSError:
            return 0.0

        if not data:
            return 0.0

        counts = Counter(data)
        size = len(data)
        return -sum((count / size) * math.log2(count / size) for count in counts.values())

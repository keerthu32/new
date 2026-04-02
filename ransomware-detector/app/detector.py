from __future__ import annotations

from dataclasses import asdict
from typing import Any

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from .monitor import ScanSummary


class RansomwareDetector:
    """Wraps a RandomForest model with generated behavioral training data."""

    def __init__(self, random_state: int = 42) -> None:
        self.random_state = random_state
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=8,
            random_state=random_state,
            class_weight="balanced",
        )
        self.accuracy = 0.0
        self._train()

    def _train(self) -> None:
        rng = np.random.default_rng(self.random_state)

        benign = np.column_stack(
            [
                rng.poisson(0.2, 1200),
                rng.poisson(0.1, 1200),
                rng.poisson(2, 1200),
                rng.normal(4.5, 0.8, 1200),
            ]
        )
        malicious = np.column_stack(
            [
                rng.poisson(8, 1200),
                rng.poisson(2, 1200),
                rng.poisson(50, 1200),
                rng.normal(7.7, 0.4, 1200),
            ]
        )

        X = np.vstack([benign, malicious])
        y = np.hstack([np.zeros(len(benign), dtype=int), np.ones(len(malicious), dtype=int)])

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=self.random_state,
            stratify=y,
        )
        self.model.fit(X_train, y_train)

        preds = self.model.predict(X_test)
        self.accuracy = float(accuracy_score(y_test, preds))

    def predict(self, summary: ScanSummary) -> dict[str, Any]:
        features = np.array(
            [
                [
                    summary.suspicious_extensions,
                    summary.suspicious_notes,
                    summary.high_entropy_files,
                    summary.avg_entropy,
                ]
            ]
        )

        risk_probability = float(self.model.predict_proba(features)[0][1])
        label = "high" if risk_probability >= 0.75 else "medium" if risk_probability >= 0.35 else "low"

        return {
            "risk_probability": round(risk_probability, 4),
            "risk_label": label,
            "model": {
                "algorithm": "RandomForestClassifier",
                "accuracy": round(self.accuracy, 4),
            },
            "scan": asdict(summary),
        }

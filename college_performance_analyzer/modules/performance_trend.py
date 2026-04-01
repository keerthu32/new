from __future__ import annotations

import numpy as np


class PerformanceTrendAnalysis:
    # Classify student trends.

    def __init__(self, data_entry_module):
        self.data_entry = data_entry_module

    def classify_trend(self, marks: list[float]) -> str:
        if len(marks) < 3:
            return "Insufficient Data"

        arr = np.array(marks, dtype=float)
        avg = float(arr.mean())
        std = float(arr.std())
        slope = np.polyfit(range(len(arr)), arr, 1)[0]

        if avg >= 85 and std <= 5:
            return "Stable Topper"
        if slope >= 2 and avg >= 60:
            return "Improving"
        if slope <= -2:
            return "Deproving"
        if avg < 50 and std <= 7:
            return "Stable Low Performer"
        return "Irregular Performer"

    def analyze_student(self, student_id: str) -> dict:
        data = self.data_entry.student_data
        subset = data[data["student_id"].astype(str).str.strip() == str(student_id).strip()].copy()
        if subset.empty:
            return {"student_id": student_id, "trend": "No Data", "average_marks": 0.0}

        subset["semester"] = subset["semester"].astype(int)
        by_sem = subset.groupby("semester", as_index=False)["marks"].mean().sort_values("semester")
        marks = by_sem["marks"].tolist()
        trend = self.classify_trend(marks)
        return {
            "student_id": student_id,
            "student_name": subset.iloc[0]["student_name"],
            "trend": trend,
            "semester_marks": marks,
            "average_marks": round(float(np.mean(marks)), 2),
        }

    def analyze_all_students(self) -> list[dict]:
        ids = self.data_entry.student_data["student_id"].astype(str).unique().tolist()
        return [self.analyze_student(sid) for sid in ids]

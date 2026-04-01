from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class ReportGenerator:
    # Generate student/class/subject/trend reports.

    def __init__(self, data_entry_module, trend_module, difficulty_module, reports_dir: str | Path = "reports"):
        self.data_entry = data_entry_module
        self.trend_module = trend_module
        self.difficulty_module = difficulty_module
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _save_report(self, payload: dict, file_name: str) -> str:
        out = self.reports_dir / file_name
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return str(out)

    def generate_student_report(self, student_id: str, save: bool = False) -> dict:
        trend = self.trend_module.analyze_student(student_id)
        df = self.data_entry.student_data
        records = df[df["student_id"].astype(str).str.strip() == str(student_id).strip()]
        payload = {
            "generated_at": datetime.now().isoformat(),
            "student": trend,
            "records": records.to_dict("records"),
        }
        if save:
            payload["file"] = self._save_report(payload, f"student_{student_id}_report.json")
        return payload

    def generate_class_report(self, save: bool = False) -> dict:
        df = self.data_entry.student_data
        trends = self.trend_module.analyze_all_students()
        subjects = self.difficulty_module.analyze_subject_difficulty()
        payload = {
            "generated_at": datetime.now().isoformat(),
            "overview": {
                "total_students": int(df["student_id"].nunique()) if not df.empty else 0,
                "total_records": int(len(df)),
                "avg_marks": round(float(df["marks"].mean()), 2) if not df.empty else 0,
            },
            "trend_summary": trends,
            "subject_difficulty": subjects,
        }
        if save:
            payload["file"] = self._save_report(payload, "class_report.json")
        return payload

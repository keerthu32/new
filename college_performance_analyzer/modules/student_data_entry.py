from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
import pandas as pd


@dataclass
class ValidationResult:
    success: bool
    message: str


class StudentDataEntry:
    # Manage college student records with semester-wise academic data.

    required_fields = [
        "student_id",
        "student_name",
        "department",
        "year",
        "semester",
        "subject",
        "marks",
        "attendance",
        "internal_score",
        "exam_date",
    ]

    def __init__(self, data_file: str | Path = "data/college_student_records.csv"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.student_data = self._load_data()

    def _load_data(self) -> pd.DataFrame:
        if self.data_file.exists():
            df = pd.read_csv(self.data_file)
        else:
            df = pd.DataFrame(columns=self._columns())
        for col in self._columns():
            if col not in df.columns:
                df[col] = ""
        return df[self._columns()]

    def _columns(self) -> list[str]:
        return [
            "student_id",
            "student_name",
            "department",
            "year",
            "semester",
            "subject",
            "marks",
            "attendance",
            "internal_score",
            "exam_type",
            "exam_date",
            "remarks",
            "timestamp",
        ]

    def _save(self) -> None:
        self.student_data.to_csv(self.data_file, index=False)

    def _clean(self, value: Any) -> str:
        return "" if value is None else str(value).strip()

    def validate_record(self, record: dict[str, Any]) -> ValidationResult:
        for field in self.required_fields:
            if self._clean(record.get(field, "")) == "":
                return ValidationResult(False, f"Missing required field: {field}")

        try:
            marks = float(record["marks"])
            attendance = float(record["attendance"])
            internal = float(record["internal_score"])
            year = int(record["year"])
            semester = int(record["semester"])
        except Exception:
            return ValidationResult(False, "Marks/attendance/internal/year/semester must be numeric")

        if not (0 <= marks <= 100 and 0 <= attendance <= 100 and 0 <= internal <= 100):
            return ValidationResult(False, "Marks, attendance, and internal score must be within 0-100")
        if not (1 <= semester <= 8):
            return ValidationResult(False, "Semester must be between 1 and 8")
        if not (1 <= year <= 4):
            return ValidationResult(False, "Year must be between 1 and 4")

        try:
            datetime.strptime(self._clean(record["exam_date"]), "%Y-%m-%d")
        except Exception:
            return ValidationResult(False, "exam_date must be in YYYY-MM-DD format")

        return ValidationResult(True, "Valid")

    def add_student_record(self, record: dict[str, Any]) -> tuple[bool, str]:
        valid = self.validate_record(record)
        if not valid.success:
            return False, valid.message

        cleaned = {
            "student_id": self._clean(record["student_id"]),
            "student_name": self._clean(record["student_name"]),
            "department": self._clean(record["department"]),
            "year": int(record["year"]),
            "semester": int(record["semester"]),
            "subject": self._clean(record["subject"]),
            "marks": float(record["marks"]),
            "attendance": float(record["attendance"]),
            "internal_score": float(record["internal_score"]),
            "exam_type": self._clean(record.get("exam_type", "Regular")) or "Regular",
            "exam_date": self._clean(record["exam_date"]),
            "remarks": self._clean(record.get("remarks", "")),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        self.student_data = pd.concat([self.student_data, pd.DataFrame([cleaned])], ignore_index=True)
        self._save()
        return True, "Student semester record added successfully"

    def update_record(self, student_id: str, subject: str, semester: int, updates: dict[str, Any]) -> tuple[bool, str]:
        mask = (
            (self.student_data["student_id"].astype(str).str.strip() == str(student_id).strip())
            & (self.student_data["subject"].astype(str).str.strip().str.lower() == str(subject).strip().lower())
            & (self.student_data["semester"].astype(int) == int(semester))
        )
        if not mask.any():
            return False, "Record not found"

        for key, value in updates.items():
            if key in self.student_data.columns and value is not None and value != "":
                self.student_data.loc[mask, key] = value
        self.student_data.loc[mask, "timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save()
        return True, "Record updated"

    def import_records(self, file_path: str | Path) -> dict[str, Any]:
        file_path = Path(file_path)
        if file_path.suffix.lower() == ".csv":
            imported = pd.read_csv(file_path)
        elif file_path.suffix.lower() in {".xlsx", ".xls"}:
            imported = pd.read_excel(file_path)
        else:
            return {"success": False, "message": "Unsupported file format", "successful": 0, "failed": 0}

        success, failed = 0, 0
        for row in imported.to_dict("records"):
            ok, _ = self.add_student_record(row)
            if ok:
                success += 1
            else:
                failed += 1
        return {
            "success": success > 0,
            "message": f"Import completed. Added {success}, failed {failed}",
            "successful": success,
            "failed": failed,
        }

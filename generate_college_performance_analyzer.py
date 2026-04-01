"""Project generator for College Performance Analyzer.

Run:
    python generate_college_performance_analyzer.py

This script creates the following structure with starter content:
college_performance_analyzer/
├── app.py
├── modules/
│   ├── student_data_entry.py
│   ├── performance_trend.py
│   ├── subject_difficulty.py
│   └── report_generator.py
├── templates/
├── static/
├── data/
├── reports/
├── uploads/
└── requirements.txt
"""

from __future__ import annotations

from pathlib import Path
import textwrap


PROJECT_ROOT = Path("college_performance_analyzer")


def build_files() -> dict[str, str]:
    return {
        "requirements.txt": textwrap.dedent(
            """
            Flask==3.1.0
            pandas==2.2.3
            numpy==2.2.2
            openpyxl==3.1.5
            """
        ).strip()
        + "\n",
        "app.py": textwrap.dedent(
            """
            from __future__ import annotations

            from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
            from pathlib import Path
            import pandas as pd

            from modules.student_data_entry import StudentDataEntry
            from modules.performance_trend import PerformanceTrendAnalysis
            from modules.subject_difficulty import SubjectDifficultyAnalysis
            from modules.report_generator import ReportGenerator

            app = Flask(__name__)
            app.secret_key = "college-analyzer-secret-key"
            app.config["UPLOAD_FOLDER"] = "uploads"
            app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

            DATA_FILE = Path("data") / "college_student_records.csv"
            entry_module = StudentDataEntry(data_file=DATA_FILE)
            trend_module = PerformanceTrendAnalysis(entry_module)
            difficulty_module = SubjectDifficultyAnalysis(entry_module)
            report_module = ReportGenerator(entry_module, trend_module, difficulty_module)


            @app.route("/")
            def home():
                records = entry_module.student_data
                total_records = len(records)
                total_students = records["student_id"].nunique() if not records.empty else 0
                semester_count = records["semester"].nunique() if not records.empty else 0
                return render_template(
                    "index.html",
                    total_records=total_records,
                    total_students=total_students,
                    semester_count=semester_count,
                )


            @app.route("/add-record", methods=["GET", "POST"])
            def add_record():
                if request.method == "POST":
                    payload = {
                        "student_id": request.form.get("student_id", ""),
                        "student_name": request.form.get("student_name", ""),
                        "department": request.form.get("department", ""),
                        "year": request.form.get("year", ""),
                        "semester": request.form.get("semester", ""),
                        "subject": request.form.get("subject", ""),
                        "marks": request.form.get("marks", ""),
                        "attendance": request.form.get("attendance", ""),
                        "internal_score": request.form.get("internal_score", ""),
                        "exam_type": request.form.get("exam_type", "Regular"),
                        "exam_date": request.form.get("exam_date", ""),
                        "remarks": request.form.get("remarks", ""),
                    }
                    ok, msg = entry_module.add_student_record(payload)
                    flash(msg, "success" if ok else "danger")
                    return redirect(url_for("add_record"))
                return render_template("add_record.html")


            @app.route("/import", methods=["GET", "POST"])
            def import_file():
                if request.method == "POST":
                    uploaded = request.files.get("file")
                    if not uploaded or not uploaded.filename:
                        flash("Please choose a CSV/XLSX file", "warning")
                        return redirect(url_for("import_file"))
                    path = Path(app.config["UPLOAD_FOLDER"]) / uploaded.filename
                    path.parent.mkdir(parents=True, exist_ok=True)
                    uploaded.save(path)
                    result = entry_module.import_records(path)
                    flash(result["message"], "success" if result["success"] else "danger")
                    return redirect(url_for("home"))
                return render_template("import.html")


            @app.route("/students")
            def students():
                return render_template(
                    "students.html", records=entry_module.student_data.to_dict("records")
                )


            @app.route("/analysis/trends")
            def trends():
                rows = trend_module.analyze_all_students()
                return render_template("trends.html", rows=rows)


            @app.route("/analysis/subjects")
            def subjects():
                rows = difficulty_module.analyze_subject_difficulty()
                return render_template("subjects.html", rows=rows)


            @app.route("/reports/student/<student_id>")
            def student_report(student_id: str):
                report = report_module.generate_student_report(student_id)
                return jsonify(report)


            @app.route("/reports/class")
            def class_report():
                report = report_module.generate_class_report()
                return jsonify(report)


            if __name__ == "__main__":
                Path("uploads").mkdir(exist_ok=True)
                Path("reports").mkdir(exist_ok=True)
                Path("data").mkdir(exist_ok=True)
                app.run(debug=True)
            """
        ).strip()
        + "\n",
        "modules/student_data_entry.py": textwrap.dedent(
            """
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
            """
        ).strip()
        + "\n",
        "modules/performance_trend.py": textwrap.dedent(
            """
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
            """
        ).strip()
        + "\n",
        "modules/subject_difficulty.py": textwrap.dedent(
            """
            from __future__ import annotations


            class SubjectDifficultyAnalysis:
                # Compute subject difficulty using class average and failure rate.

                def __init__(self, data_entry_module):
                    self.data_entry = data_entry_module

                def analyze_subject_difficulty(self, pass_mark: float = 40.0) -> list[dict]:
                    df = self.data_entry.student_data
                    if df.empty:
                        return []

                    rows = []
                    for subject, group in df.groupby("subject"):
                        avg = float(group["marks"].mean())
                        failure_rate = float((group["marks"] < pass_mark).mean() * 100)

                        if avg < 50 or failure_rate > 40:
                            level = "Hard"
                        elif avg < 65 or failure_rate > 25:
                            level = "Moderate"
                        else:
                            level = "Easy"

                        rows.append(
                            {
                                "subject": subject,
                                "average_marks": round(avg, 2),
                                "failure_rate": round(failure_rate, 2),
                                "difficulty_level": level,
                                "records_count": int(len(group)),
                            }
                        )

                    rows.sort(key=lambda x: (x["average_marks"], -x["failure_rate"]))
                    return rows
            """
        ).strip()
        + "\n",
        "modules/report_generator.py": textwrap.dedent(
            """
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
            """
        ).strip()
        + "\n",
        "templates/index.html": textwrap.dedent(
            """
            <!doctype html>
            <html>
              <head><title>College Performance Analyzer</title></head>
              <body>
                <h1>College Performance Analyzer</h1>
                <p>Total Records: {{ total_records }}</p>
                <p>Total Students: {{ total_students }}</p>
                <p>Semesters Covered: {{ semester_count }}</p>
              </body>
            </html>
            """
        ).strip()
        + "\n",
        "templates/add_record.html": "<h2>Add Record Form Placeholder</h2>\n",
        "templates/import.html": "<h2>Import CSV/XLSX Placeholder</h2>\n",
        "templates/students.html": "<h2>Students List Placeholder</h2>\n",
        "templates/trends.html": "<h2>Trend Analysis Placeholder</h2>\n",
        "templates/subjects.html": "<h2>Subject Difficulty Placeholder</h2>\n",
        "static/.gitkeep": "",
        "data/.gitkeep": "",
        "reports/.gitkeep": "",
        "uploads/.gitkeep": "",
        "modules/__init__.py": "",
    }


def write_project(base: Path, files: dict[str, str]) -> None:
    for relative, content in files.items():
        target = base / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def main() -> None:
    files = build_files()
    write_project(PROJECT_ROOT, files)
    print(f"Created project at: {PROJECT_ROOT.resolve()}")
    print(f"Generated files: {len(files)}")


if __name__ == "__main__":
    main()

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

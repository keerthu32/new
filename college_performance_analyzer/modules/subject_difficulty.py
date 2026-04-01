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

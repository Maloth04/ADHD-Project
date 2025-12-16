# importer.py
import pandas as pd
from storage_sql import init_db, add_entry
import datetime

init_db()
df = pd.read_excel("ADHD_30_Days_Sample_Data.xlsx", engine="openpyxl")
for _, r in df.iterrows():
    entry = {
        "user": r.get("Name") or "Unknown",
        "entry_date": pd.to_datetime(r.get("Date")).date() if not pd.isna(r.get("Date")) else datetime.date.today(),
        "focus": int(r.get("Focus") or 0),
        "hyperactivity": int(r.get("Hyperactivity") or 0),
        "impulsivity": int(r.get("Impulsivity") or 0),
        "sleep_hours": float(r.get("Sleep Hours") or 0),
        "distractions": int(r.get("Distractions") or 0),
        "tasks_completed": int(r.get("Tasks Completed") or 0),
        "mood": r.get("Mood") or "",
        "notes": r.get("Notes") or "",
        "cognitive_score": float(r.get("Cognitive Score") or 0),
        "advice": r.get("Advice") or ""
    }
    add_entry(entry)
print("Import complete.")

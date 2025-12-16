# logic.py
import pandas as pd
import numpy as np

def compute_cognitive_score(row):
    # safe getters
    focus = float(row.get("focus") or row.get("Focus") or 0)
    hyper = float(row.get("hyperactivity") or row.get("Hyperactivity") or 0)
    imp = float(row.get("impulsivity") or row.get("Impulsivity") or 0)
    sleep = float(row.get("sleep_hours") or row.get("Sleep Hours") or 7)
    tasks = float(row.get("tasks_completed") or row.get("Tasks Completed") or 0)
    dist = float(row.get("distractions") or row.get("Distractions") or 0)
    screen = float(row.get("screen_time") or row.get("Screen Time") or 0)

    # normalize
    focus_s = focus/10.0
    tasks_s = min(tasks,10)/10.0
    sleep_s = max(0, 1 - abs(7 - sleep)/7)
    neg_hyper = (hyper/10.0 + imp/10.0)/2.0
    screen_s = min(screen/12.0,1.0)
    dist_s = min(dist/10.0,1.0)

    # weights
    w_focus = 0.40
    w_tasks = 0.20
    w_sleep = 0.15
    w_neg = 0.15
    w_screen = 0.10

    positive = w_focus*focus_s + w_tasks*tasks_s + w_sleep*sleep_s
    negative = w_neg*(neg_hyper + 0.2*dist_s) + w_screen*screen_s

    raw = positive - negative
    score = max(0.0, min(1.0, raw))
    return round(score*10,2)

def rule_based_advice(df):
    if df is None or df.empty:
        return ["No data available."]
    d = df.copy()
    for c in ["Focus","Cognitive Score","Sleep Hours","Screen Time","Hyperactivity","Impulsivity","Tasks Completed"]:
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce")
    recent = d.tail(7) if len(d)>=7 else d
    suggestions = []

    if "Focus" in recent.columns and recent["Focus"].dropna().size>0:
        avg_focus = recent["Focus"].mean()
        if avg_focus < 4:
            suggestions.append("Low recent focus — try Pomodoro (25/5) and reduce distractions.")
        elif avg_focus < 6:
            suggestions.append("Focus moderate — short breaks & prioritized task list could help.")
        else:
            suggestions.append("Focus stable — keep routine.")

    if "Sleep Hours" in recent.columns and recent["Sleep Hours"].dropna().size>0:
        if recent["Sleep Hours"].mean()<6.5:
            suggestions.append("Sleep is low — aim for 7–8 hours.")

    if "Screen Time" in recent.columns and recent["Screen Time"].dropna().size>0:
        avg_screen = recent["Screen Time"].mean()
        if avg_screen >= 8:
            suggestions.append("Very high screen time (>8h/day). Strongly reduce leisure screen time.")
        elif avg_screen >= 6:
            suggestions.append("High screen time — reduce non-essential use, use app timers.")
        elif avg_screen >= 4:
            suggestions.append("Moderate screen time — avoid screens before bed.")

    if "Tasks Completed" in recent.columns:
        if recent["Tasks Completed"].mean() < 2 and ("avg_focus" not in locals() or recent["Focus"].mean()<5):
            suggestions.append("Low productivity — break tasks into 15–20 minute chunks.")

    # mood
    if "Mood" in d.columns and d["Mood"].dropna().size>0:
        mapm = {"Good":2,"Okay":1,"Bad":0}
        mvals = d["Mood"].map(mapm).fillna(1)
        if mvals.tail(3).mean() < 1:
            suggestions.append("Recent mood is low — consider talking to someone or relaxation exercises.")

    if not suggestions:
        suggestions.append("No specific suggestions; continue tracking to build patterns.")
    # unique
    out = []
    for s in suggestions:
        if s not in out:
            out.append(s)
    return out

def generate_insights(df, days=7):
    if df is None or df.empty:
        return ["No data available."]
    d = df.copy()
    d["Date"] = pd.to_datetime(d["Date"])
    d = d.sort_values("Date")
    recent = d.tail(days) if len(d)>=days else d
    insights = []
    if "Focus" in recent.columns and recent["Focus"].dropna().size>=2:
        y = recent["Focus"].dropna()
        slope = (y.values[-1] - y.values[0]) / max(1,len(y))
        if slope>0.2:
            insights.append("Focus has improved over the period.")
        elif slope<-0.2:
            insights.append("Focus has declined recently.")
        else:
            insights.append("Focus relatively stable.")
    if "Screen Time" in recent.columns and recent["Screen Time"].dropna().size>=1:
        s = recent["Screen Time"].mean()
        if s>6:
            insights.append("Average screen time is high — consider limiting leisure screen time.")
        elif s>4:
            insights.append("Screen time moderate — avoid screens before sleep.")
    if "Sleep Hours" in recent.columns and recent["Sleep Hours"].dropna().size>=1:
        if recent["Sleep Hours"].mean() < 6.5:
            insights.append("Sleep below recommended—improving sleep may boost focus.")
    if "Tasks Completed" in recent.columns:
        if recent["Tasks Completed"].mean()>=4:
            insights.append("Productivity good; maintain routine.")
        else:
            insights.append("Productivity low; try smaller goals.")
    if not insights:
        insights.append("Not enough pattern yet — keep logging consistently.")
    return insights

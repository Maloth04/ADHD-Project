# storage_sql.py
from sqlalchemy import Column, Integer, String, Float, Date, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import date, datetime
import pandas as pd
import os

Base = declarative_base()
DB_FILE = "adhd_app.db"
ENGINE = create_engine(f"sqlite:///{DB_FILE}", echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=ENGINE)

class Entry(Base):
    __tablename__ = "entries"
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, index=True)
    entry_date = Column(Date)
    focus = Column(Integer)
    hyperactivity = Column(Integer)
    impulsivity = Column(Integer)
    sleep_hours = Column(Float)
    distractions = Column(Integer)
    tasks_completed = Column(Integer)
    mood = Column(String)
    notes = Column(String)
    cognitive_score = Column(Float)
    advice = Column(String)
    screen_time = Column(Float, default=0.0)

class Habit(Base):
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, index=True)
    date = Column(Date)
    exercise_minutes = Column(Integer, default=0)
    study_minutes = Column(Integer, default=0)
    screen_minutes = Column(Integer, default=0)
    notes = Column(String)

def init_db():
    Base.metadata.create_all(bind=ENGINE)

def _fix_date(d):
    if d is None:
        return None
    if isinstance(d, date):
        return d
    if isinstance(d, datetime):
        return d.date()
    s = str(d).strip()
    for fmt in ("%Y-%m-%d","%d-%m-%Y","%m/%d/%Y","%m/%d/%y"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            pass
    try:
        return pd.to_datetime(s).date()
    except Exception:
        return None

def add_entry(row):
    session = SessionLocal()
    e = Entry(
        user = row.get("user"),
        entry_date = _fix_date(row.get("entry_date")),
        focus = row.get("focus"),
        hyperactivity = row.get("hyperactivity"),
        impulsivity = row.get("impulsivity"),
        sleep_hours = row.get("sleep_hours"),
        distractions = row.get("distractions"),
        tasks_completed = row.get("tasks_completed"),
        mood = row.get("mood"),
        notes = row.get("notes"),
        cognitive_score = row.get("cognitive_score"),
        advice = row.get("advice"),
        screen_time = row.get("screen_time", 0.0)
    )
    session.add(e)
    session.commit()
    session.close()

def add_habit(h):
    session = SessionLocal()
    hrow = Habit(
        user = h.get("user"),
        date = _fix_date(h.get("date")),
        exercise_minutes = h.get("exercise_minutes",0),
        study_minutes = h.get("study_minutes",0),
        screen_minutes = h.get("screen_minutes",0),
        notes = h.get("notes","")
    )
    session.add(hrow)
    session.commit()
    session.close()

def query_entries(user=None, start_date=None, end_date=None):
    session = SessionLocal()
    q = session.query(Entry)
    if user:
        q = q.filter(Entry.user==user)
    if start_date:
        sd = _fix_date(start_date)
        if sd:
            q = q.filter(Entry.entry_date >= sd)
    if end_date:
        ed = _fix_date(end_date)
        if ed:
            q = q.filter(Entry.entry_date <= ed)
    rows = q.order_by(Entry.entry_date).all()
    session.close()
    data = []
    for r in rows:
        data.append({
            "Date": r.entry_date,
            "Name": r.user,
            "Focus": r.focus,
            "Hyperactivity": r.hyperactivity,
            "Impulsivity": r.impulsivity,
            "Sleep Hours": r.sleep_hours,
            "Distractions": r.distractions,
            "Tasks Completed": r.tasks_completed,
            "Mood": r.mood,
            "Notes": r.notes,
            "Cognitive Score": r.cognitive_score,
            "Advice": r.advice,
            "Screen Time": r.screen_time
        })
    return pd.DataFrame(data)

def query_habits(user=None, start_date=None, end_date=None):
    session = SessionLocal()
    q = session.query(Habit)
    if user:
        q = q.filter(Habit.user==user)
    if start_date:
        sd = _fix_date(start_date)
        if sd:
            q = q.filter(Habit.date >= sd)
    if end_date:
        ed = _fix_date(end_date)
        if ed:
            q = q.filter(Habit.date <= ed)
    rows = q.order_by(Habit.date).all()
    session.close()
    data = []
    for r in rows:
        data.append({
            "Date": r.date,
            "User": r.user,
            "Exercise Minutes": r.exercise_minutes,
            "Study Minutes": r.study_minutes,
            "Screen Minutes": r.screen_minutes,
            "Notes": r.notes
        })
    return pd.DataFrame(data)

def get_users():
    session = SessionLocal()
    users = session.query(Entry.user).distinct().all()
    session.close()
    return [u[0] for u in users if u[0] is not None]

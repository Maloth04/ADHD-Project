# viz.py
import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
from scipy.ndimage import uniform_filter1d

def _to_xlabels(df):
    x = pd.to_datetime(df["Date"])
    return x.dt.strftime("%Y-%m-%d")

def figure_focus_trend(df):
    fig = Figure(figsize=(7,4), dpi=100)
    ax = fig.subplots()
    if df is None or df.empty:
        ax.text(0.5,0.5,"No data", ha="center")
        return fig
    df = df.sort_values("Date")
    x = _to_xlabels(df)
    y = pd.to_numeric(df["Focus"], errors="coerce")
    ax.plot(x, y, marker="o", linewidth=2)
    if len(y.dropna())>=3:
        smooth = uniform_filter1d(y.fillna(method="ffill").values, size=2)
        ax.plot(x, smooth, linestyle="--", alpha=0.6)
    ax.set_title("Focus Trend")
    ax.set_xlabel("Date"); ax.set_ylabel("Focus (1-10)")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig

def figure_cognitive_trend(df):
    fig = Figure(figsize=(7,4), dpi=100)
    ax = fig.subplots()
    if df is None or df.empty:
        ax.text(0.5,0.5,"No data", ha="center")
        return fig
    df = df.sort_values("Date")
    x = _to_xlabels(df)
    y = pd.to_numeric(df["Cognitive Score"], errors="coerce")
    ax.plot(x, y, marker="o", linewidth=2, color="tab:green")
    ax.set_title("Cognitive Score Trend")
    ax.set_xlabel("Date"); ax.set_ylabel("Score")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig

def figure_sleep_trend(df):
    fig = Figure(figsize=(7,3), dpi=100)
    ax = fig.subplots()
    if df is None or df.empty:
        ax.text(0.5,0.5,"No data", ha="center")
        return fig
    df = df.sort_values("Date")
    x = _to_xlabels(df)
    y = pd.to_numeric(df["Sleep Hours"], errors="coerce")
    ax.plot(x, y, marker="s", linewidth=2, color="tab:purple")
    ax.set_title("Sleep Hours Trend")
    ax.set_xlabel("Date"); ax.set_ylabel("Hours")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig

def figure_screen_trend(df):
    fig = Figure(figsize=(7,3), dpi=100)
    ax = fig.subplots()
    if df is None or df.empty:
        ax.text(0.5,0.5,"No data", ha="center")
        return fig
    df = df.sort_values("Date")
    x = _to_xlabels(df)
    y = pd.to_numeric(df["Screen Time"], errors="coerce")
    ax.plot(x, y, marker="d", linewidth=2, color="tab:orange")
    ax.set_title("Screen Time (hrs) Trend")
    ax.set_xlabel("Date"); ax.set_ylabel("Hours")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig

def figure_mood_pie(df):
    fig = Figure(figsize=(4,3), dpi=100)
    ax = fig.subplots()
    if df is None or df.empty:
        ax.text(0.5,0.5,"No data", ha="center")
        return fig
    counts = df["Mood"].value_counts()
    ax.pie(counts, labels=counts.index.tolist(), autopct="%1.1f%%")
    ax.set_title("Mood Distribution")
    fig.tight_layout()
    return fig

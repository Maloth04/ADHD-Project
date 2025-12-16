# ml_predict.py
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib
import os

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

FEATURE_COLS = [
    "Focus", "Hyperactivity", "Impulsivity",
    "Sleep Hours", "Distractions", "Tasks Completed",
    "Screen Time", "Cognitive Score"
]
TARGET_COL = "Focus"

def train_user_model(df, user):
    df = df.copy()
    df = df.dropna(subset=FEATURE_COLS + [TARGET_COL])
    if len(df) < 5:
        return False
    X = df[FEATURE_COLS]
    y = df[TARGET_COL]
    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("model", LinearRegression())
    ])
    pipe.fit(X, y)
    path = os.path.join(MODEL_DIR, f"{user}_model.pkl")
    joblib.dump(pipe, path)
    return True

def predict_next_focus(df, user):
    model_path = os.path.join(MODEL_DIR, f"{user}_model.pkl")
    if not os.path.exists(model_path):
        trained = train_user_model(df, user)
        if not trained:
            return None
    pipe = joblib.load(model_path)
    last_row = df.iloc[-1]
    X_new = pd.DataFrame([{
        "Focus": last_row["Focus"],
        "Hyperactivity": last_row["Hyperactivity"],
        "Impulsivity": last_row["Impulsivity"],
        "Sleep Hours": last_row["Sleep Hours"],
        "Distractions": last_row["Distractions"],
        "Tasks Completed": last_row["Tasks Completed"],
        "Screen Time": last_row.get("Screen Time", 0),
        "Cognitive Score": last_row["Cognitive Score"],
    }])
    pred = pipe.predict(X_new)[0]
    return round(float(pred),2)

# app.py (Upgraded Modern Dashboard - Style A)
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from datetime import datetime, date
import pandas as pd
import os

# Local modules (must exist)
from storage_sql import init_db, add_entry, query_entries, get_users, add_habit, query_habits
from logic import compute_cognitive_score, rule_based_advice, generate_insights
from viz import figure_focus_trend, figure_cognitive_trend, figure_mood_pie

# optional report and ml modules
try:
    from report import export_excel_for_user, export_pdf_for_user
except Exception:
    export_excel_for_user = None
    export_pdf_for_user = None

try:
    from ml_predict import predict_next_day
except Exception:
    predict_next_day = None

# matplotlib canvas
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# scheduler & notifier
from apscheduler.schedulers.background import BackgroundScheduler
try:
    from win10toast import ToastNotifier
    notifier = ToastNotifier()
except Exception:
    notifier = None

# initialize DB
init_db()

# Theme / colors
BG = "#f7fbff"
PANEL = "#ffffff"
ACCENT = "#0b63d4"
CARD = "#e9f2ff"
TXT = "#0b0b0b"
BTN = "#2b8cff"

# utilities
def safe_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default

def safe_int(v, default=0):
    try:
        return int(v)
    except Exception:
        return default

class ADHDApp:
    def __init__(self, root):
        self.root = root
        root.title("AI-Enhanced ADHD Monitor — Modern Dashboard")
        root.geometry("1200x760")
        root.configure(bg=BG)

        # top bar
        top = tk.Frame(root, bg=BG)
        top.pack(fill="x", padx=12, pady=8)

        tk.Label(top, text="User:", bg=BG, fg=TXT).pack(side="left")
        self.user_var = tk.StringVar()
        self.user_combo = ttk.Combobox(top, textvariable=self.user_var, values=get_users(), width=22)
        self.user_combo.pack(side="left", padx=8)

        # Predict button
        self.predict_btn = tk.Button(top, text="Predict Next-Day Focus", command=self.on_predict, bg="#20a39e", fg="white")
        self.predict_btn.pack(side="right", padx=6)

        # Toggle use range vs full history
        self.use_range_var = tk.BooleanVar(value=False)
        self.range_chk = tk.Checkbutton(top, text="Use Date Range", variable=self.use_range_var, bg=BG, command=self.on_toggle_range)
        self.range_chk.pack(side="right", padx=8)

        tk.Label(top, text="From:", bg=BG, fg=TXT).pack(side="left", padx=(20,2))
        self.from_date = DateEntry(top, width=12)
        self.from_date.pack(side="left", padx=4)
        tk.Label(top, text="To:", bg=BG, fg=TXT).pack(side="left", padx=(8,2))
        self.to_date = DateEntry(top, width=12)
        self.to_date.pack(side="left", padx=4)

        # theme toggle
        self.dark = False
        self.toggle_btn = tk.Button(top, text="Toggle Dark", command=self.toggle_theme, bg=BTN, fg="white")
        self.toggle_btn.pack(side="right", padx=6)

        # main
        main = tk.Frame(root, bg=BG)
        main.pack(fill="both", expand=True, padx=12, pady=(0,12))

        # left sidebar (scrollable)
        sidebar_container = tk.Frame(main, bg=BG)
        sidebar_container.pack(side="left", fill="y", padx=(0,12))

        canvas = tk.Canvas(sidebar_container, bg=BG, highlightthickness=0, width=380, height=650)
        scrollbar = tk.Scrollbar(sidebar_container, orient="vertical", command=canvas.yview)
        self.sidebar = tk.Frame(canvas, bg=PANEL)
        self.sidebar.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self.sidebar, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="y")
        scrollbar.pack(side="right", fill="y")

        # input widgets
        s_padx = 10
        tk.Label(self.sidebar, text="Add Daily Entry", bg=PANEL, fg=TXT, font=("Helvetica",14,"bold")).pack(anchor="w", padx=s_padx, pady=(14,6))
        tk.Label(self.sidebar, text="Name", bg=PANEL).pack(anchor="w", padx=s_padx)
        self.name_e = tk.Entry(self.sidebar, width=30)
        self.name_e.pack(padx=s_padx, pady=(0,8))

        tk.Label(self.sidebar, text="Date", bg=PANEL).pack(anchor="w", padx=s_padx)
        self.date_e = DateEntry(self.sidebar, width=28)
        self.date_e.pack(padx=s_padx, pady=(0,8))

        tk.Label(self.sidebar, text="Sleep Hours", bg=PANEL).pack(anchor="w", padx=s_padx)
        self.sleep_e = tk.Entry(self.sidebar, width=10)
        self.sleep_e.pack(padx=s_padx, pady=(0,8))

        tk.Label(self.sidebar, text="Screen Time (hours)", bg=PANEL).pack(anchor="w", padx=s_padx)
        self.screen_e = tk.Entry(self.sidebar, width=10)
        self.screen_e.insert(0, "0")
        self.screen_e.pack(padx=s_padx, pady=(0,8))

        tk.Label(self.sidebar, text="Distractions", bg=PANEL).pack(anchor="w", padx=s_padx)
        self.dist_e = tk.Entry(self.sidebar, width=10)
        self.dist_e.pack(padx=s_padx, pady=(0,8))

        tk.Label(self.sidebar, text="Tasks Completed", bg=PANEL).pack(anchor="w", padx=s_padx)
        self.tasks_e = tk.Entry(self.sidebar, width=10)
        self.tasks_e.pack(padx=s_padx, pady=(0,8))

        tk.Label(self.sidebar, text="Notes", bg=PANEL).pack(anchor="w", padx=s_padx)
        self.notes_e = tk.Entry(self.sidebar, width=32)
        self.notes_e.pack(padx=s_padx, pady=(0,8))

        tk.Label(self.sidebar, text="Focus (1–10)", bg=PANEL).pack(anchor="w", padx=s_padx)
        self.focus_s = tk.Scale(self.sidebar, from_=1, to=10, orient="horizontal", length=300)
        self.focus_s.set(5); self.focus_s.pack(padx=s_padx, pady=(0,8))

        tk.Label(self.sidebar, text="Hyperactivity (1–10)", bg=PANEL).pack(anchor="w", padx=s_padx)
        self.hype_s = tk.Scale(self.sidebar, from_=1, to=10, orient="horizontal", length=300)
        self.hype_s.set(5); self.hype_s.pack(padx=s_padx, pady=(0,8))

        tk.Label(self.sidebar, text="Impulsivity (1–10)", bg=PANEL).pack(anchor="w", padx=s_padx)
        self.imp_s = tk.Scale(self.sidebar, from_=1, to=10, orient="horizontal", length=300)
        self.imp_s.set(5); self.imp_s.pack(padx=s_padx, pady=(0,8))

        tk.Label(self.sidebar, text="Mood", bg=PANEL).pack(anchor="w", padx=s_padx)
        self.mood_cb = ttk.Combobox(self.sidebar, values=["Good","Okay","Bad"], width=28)
        self.mood_cb.set("Okay"); self.mood_cb.pack(padx=s_padx, pady=(0,12))

        btn_frame = tk.Frame(self.sidebar, bg=PANEL)
        btn_frame.pack(fill="x", pady=(4,12))
        tk.Button(btn_frame, text="Save Entry", bg=ACCENT, fg="white", width=12, command=self.save_entry).grid(row=0, column=0, padx=6, pady=6)
        tk.Button(btn_frame, text="Analyze", bg="#28a745", fg="white", width=12, command=self.analyze_range).grid(row=0, column=1, padx=6, pady=6)
        tk.Button(btn_frame, text="Import Excel", bg="#6A5ACD", fg="white", width=12, command=self.import_excel).grid(row=1, column=0, padx=6, pady=6)
        tk.Button(btn_frame, text="Export Excel", bg="#ff8c00", fg="white", width=12, command=self.export_excel).grid(row=1, column=1, padx=6, pady=6)
        tk.Button(btn_frame, text="Export PDF", bg="#ff5b5b", fg="white", width=26, command=self.export_pdf).grid(row=2, column=0, columnspan=2, pady=6)

        # habits mini panel
        tk.Label(self.sidebar, text="Add Habit (optional)", bg=PANEL, font=("Helvetica",11,"bold")).pack(anchor="w", padx=s_padx, pady=(6,4))
        tk.Label(self.sidebar, text="Exercise (mins)", bg=PANEL).pack(anchor="w", padx=s_padx)
        self.ex_mins = tk.Entry(self.sidebar, width=12); self.ex_mins.insert(0,"0"); self.ex_mins.pack(padx=s_padx, pady=(0,6))
        tk.Label(self.sidebar, text="Study (mins)", bg=PANEL).pack(anchor="w", padx=s_padx)
        self.st_mins = tk.Entry(self.sidebar, width=12); self.st_mins.insert(0,"0"); self.st_mins.pack(padx=s_padx, pady=(0,6))
        tk.Label(self.sidebar, text="Screen (mins)", bg=PANEL).pack(anchor="w", padx=s_padx)
        self.scr_mins = tk.Entry(self.sidebar, width=12); self.scr_mins.insert(0,"0"); self.scr_mins.pack(padx=s_padx, pady=(0,8))
        tk.Button(self.sidebar, text="Save Habit", bg="#5b8c5a", fg="white", command=self.save_habit).pack(padx=s_padx, pady=(4,12))

        # output text
        tk.Label(self.sidebar, text="System Output", bg=PANEL).pack(anchor="w", padx=s_padx)
        self.output_txt = tk.Text(self.sidebar, height=8, width=42)
        self.output_txt.pack(padx=s_padx, pady=(6,20))

        # right dashboard
        dashboard = tk.Frame(main, bg=BG)
        dashboard.pack(side="left", fill="both", expand=True)

        # cards row
        cards = tk.Frame(dashboard, bg=BG)
        cards.pack(fill="x", pady=(6,4))
        self.avg_focus_card = self._make_card(cards, "Avg Focus", "-")
        self.avg_cog_card = self._make_card(cards, "Avg Cognitive", "-")
        self.best_day_card = self._make_card(cards, "Best Day", "-")
        self.avg_sleep_card = self._make_card(cards, "Avg Sleep", "-")
        self.avg_screen_card = self._make_card(cards, "Avg Screen (hrs)", "-")

        # charts and insights
        lower = tk.Frame(dashboard, bg=BG)
        lower.pack(fill="both", expand=True, pady=(8,6))

        # left charts
        charts = tk.Frame(lower, bg=PANEL)
        charts.pack(side="left", fill="both", expand=True, padx=(6,4))

        self.canvas_holder = tk.Frame(charts, bg=PANEL)
        self.canvas_holder.pack(fill="both", expand=True, padx=8, pady=8)

        # right insights
        right_panel = tk.Frame(lower, bg=BG, width=320)
        right_panel.pack(side="left", fill="y", padx=(6,12))
        tk.Label(right_panel, text="Insights", bg=BG, font=("Helvetica",14,"bold")).pack(anchor="nw", pady=(8,6))
        self.insights_box = tk.Text(right_panel, width=36, height=18)
        self.insights_box.pack(padx=6, pady=4)
        tk.Button(right_panel, text="Refresh Insights", bg="#6A5ACD", fg="white", command=self.refresh_insights).pack(pady=6)
        tk.Label(right_panel, text="Habits (recent)", bg=BG, font=("Helvetica",12,"bold")).pack(anchor="nw", pady=(8,4))
        self.habits_box = tk.Text(right_panel, width=36, height=8)
        self.habits_box.pack(padx=6, pady=4)

        # scheduler
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        # initial
        self.refresh_user_list()
        self.refresh_dashboard()

    def _make_card(self, parent, title, value):
        f = tk.Frame(parent, bg=CARD, padx=10, pady=8)
        f.pack(side="left", padx=8, pady=4)
        tk.Label(f, text=title, bg=CARD, fg=TXT, font=("Helvetica",10)).pack(anchor="w")
        lbl = tk.Label(f, text=value, bg=CARD, fg=ACCENT, font=("Helvetica",14,"bold"))
        lbl.pack(anchor="w")
        return lbl

    def toggle_theme(self):
        self.dark = not self.dark
        if self.dark:
            self.root.configure(bg="#1f2428")
        else:
            self.root.configure(bg=BG)

    def refresh_user_list(self):
        users = get_users()
        self.user_combo["values"] = users
        if not self.user_var.get() and users:
            self.user_var.set(users[0])

    def build_row_from_inputs(self):
        row = {}
        row["user"] = self.name_e.get().strip() or "Unknown"
        row["entry_date"] = self.date_e.get_date()
        row["focus"] = int(self.focus_s.get())
        row["hyperactivity"] = int(self.hype_s.get())
        row["impulsivity"] = int(self.imp_s.get())
        row["sleep_hours"] = safe_float(self.sleep_e.get(), 7.0)
        row["distractions"] = safe_int(self.dist_e.get(), 0)
        row["tasks_completed"] = safe_int(self.tasks_e.get(), 0)
        row["mood"] = self.mood_cb.get()
        row["notes"] = self.notes_e.get()
        row["screen_time"] = safe_float(self.screen_e.get(), 0.0)
        row["cognitive_score"] = compute_cognitive_score(row)
        row["advice"] = ""
        return row

    def save_entry(self):
        try:
            row = self.build_row_from_inputs()
            add_entry(row)
            self.output_txt.insert("end", f"Saved: {row['user']} {row['entry_date']} → Cog: {row['cognitive_score']}\n")
            self.refresh_user_list()
            self.refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Save error", str(e))

    def save_habit(self):
        try:
            h = {
                "user": self.name_e.get().strip() or self.user_var.get() or "Unknown",
                "date": self.date_e.get_date(),
                "exercise_minutes": safe_int(self.ex_mins.get(), 0),
                "study_minutes": safe_int(self.st_mins.get(), 0),
                "screen_minutes": safe_int(self.scr_mins.get(), 0),
                "notes": ""
            }
            add_habit(h)
            self.output_txt.insert("end", f"Habit saved: {h['user']} {h['date']}\n")
            self.refresh_habits()
        except Exception as e:
            messagebox.showerror("Habit save error", str(e))

    def on_toggle_range(self):
        # if unchecked, ignore dates (full-history)
        self.refresh_dashboard()

    def analyze_range(self):
        # analyze (shows suggestions) using either range or full history
        if self.user_var.get():
            if self.use_range_var.get():
                df = query_entries(user=self.user_var.get(), start_date=self.from_date.get_date(), end_date=self.to_date.get_date())
            else:
                df = query_entries(user=self.user_var.get())
        else:
            df = None
        adv = rule_based_advice(df)
        self.output_txt.insert("end", "Suggestions:\n")
        for a in adv:
            self.output_txt.insert("end", "- " + a + "\n")
        self.refresh_insights()
        self.refresh_dashboard()

    def import_excel(self):
        p = filedialog.askopenfilename(title="Select Excel to import", filetypes=[("Excel","*.xlsx *.xls")])
        if not p:
            return
        try:
            df = pd.read_excel(p, engine="openpyxl")
            for _, r in df.iterrows():
                entry = {
                    "user": r.get("Name") or "Unknown",
                    "entry_date": pd.to_datetime(r.get("Date")).date() if not pd.isna(r.get("Date")) else datetime.today().date(),
                    "focus": int(r.get("Focus") or 0),
                    "hyperactivity": int(r.get("Hyperactivity") or 0),
                    "impulsivity": int(r.get("Impulsivity") or 0),
                    "sleep_hours": float(r.get("Sleep Hours") or 0),
                    "distractions": int(r.get("Distractions") or 0),
                    "tasks_completed": int(r.get("Tasks Completed") or 0),
                    "mood": r.get("Mood") or "",
                    "notes": r.get("Notes") or "",
                    "cognitive_score": float(r.get("Cognitive Score") or 0),
                    "advice": r.get("Advice") or "",
                    "screen_time": float(r.get("Screen Time") or 0.0)
                }
                add_entry(entry)
            messagebox.showinfo("Imported", "Excel imported into database.")
            self.refresh_user_list()
            self.refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Import error", str(e))

    def export_excel(self):
        if export_excel_for_user is None:
            messagebox.showwarning("Export", "Export function not available (report.py missing).")
            return
        out = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel","*.xlsx")], initialfile=f"ADHD_export_{datetime.now().strftime('%Y%m%d')}.xlsx")
        if out:
            export_excel_for_user(self.user_var.get() or None, start_date=None, end_date=None, out_path=out)
            messagebox.showinfo("Exported", f"Excel exported to:\n{out}")

    def export_pdf(self):
        if export_pdf_for_user is None:
            messagebox.showwarning("Export", "PDF export not available (report.py missing).")
            return
        out = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF","*.pdf")], initialfile=f"ADHD_report_{self.user_var.get() or 'report'}_{datetime.now().strftime('%Y%m%d')}.pdf")
        if out:
            export_pdf_for_user(self.user_var.get() or None, start_date=None, end_date=None, out_path=out)
            messagebox.showinfo("Exported", f"PDF exported to:\n{out}")

    def on_predict(self):
        if predict_next_day is None:
            messagebox.showinfo("Predict",
    "Prediction will be enabled after sufficient data is collected.")
            return
        user = self.user_var.get() or self.name_e.get().strip()
        if not user:
            messagebox.showwarning("Predict", "Select or enter a user first.")
            return
        try:
            pred = predict_next_day(user)
            if pred is None:
                self.output_txt.insert("end", "No trained model available or not enough data. Train model for this user first.\n")
            else:
                self.output_txt.insert("end", f"Predicted next-day focus for {user}: {pred}\n")
        except Exception as e:
            messagebox.showerror("Prediction error", str(e))

    def refresh_dashboard(self):
        user = self.user_var.get() or None
        if user:
            if self.use_range_var.get():
                df = query_entries(user=user, start_date=self.from_date.get_date(), end_date=self.to_date.get_date())
            else:
                df = query_entries(user=user)
        else:
            df = None

        # update cards and graphs
        if df is None or df.empty:
            self.avg_focus_card.config(text="-")
            self.avg_cog_card.config(text="-")
            self.best_day_card.config(text="-")
            self.avg_sleep_card.config(text="-")
            self.avg_screen_card.config(text="-")
            for w in self.canvas_holder.winfo_children(): w.destroy()
            return

        # ensure numeric
        df_num = df.copy()
        df_num["Focus"] = pd.to_numeric(df_num["Focus"], errors="coerce")
        df_num["Cognitive Score"] = pd.to_numeric(df_num["Cognitive Score"], errors="coerce")
        df_num["Sleep Hours"] = pd.to_numeric(df_num["Sleep Hours"], errors="coerce")
        df_num["Screen Time"] = pd.to_numeric(df_num["Screen Time"], errors="coerce")

        # cards
        avg_focus = df_num["Focus"].mean()
        avg_cog = df_num["Cognitive Score"].mean()
        avg_sleep = df_num["Sleep Hours"].mean()
        avg_screen = df_num["Screen Time"].mean()
        self.avg_focus_card.config(text=f"{avg_focus:.2f}" if pd.notna(avg_focus) else "-")
        self.avg_cog_card.config(text=f"{avg_cog:.2f}" if pd.notna(avg_cog) else "-")
        self.avg_sleep_card.config(text=f"{avg_sleep:.2f}h" if pd.notna(avg_sleep) else "-")
        self.avg_screen_card.config(text=f"{avg_screen:.2f}h" if pd.notna(avg_screen) else "-")
        if not df_num["Cognitive Score"].dropna().empty:
            idx = df_num["Cognitive Score"].idxmax()
            best = df_num.loc[idx]
            self.best_day_card.config(text=f"{best['Date']} ({best['Cognitive Score']})")
        else:
            self.best_day_card.config(text="-")

        # draw charts (focus by default)
        fig = figure_focus_trend(df)
        for w in self.canvas_holder.winfo_children(): w.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_holder)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # refresh right panels
        self.refresh_insights()
        self.refresh_habits()

    def refresh_insights(self):
        user = self.user_var.get() or None
        if user:
            df = query_entries(user=user)  # full history
        else:
            df = None
        ins = generate_insights(df, days=7)
        self.insights_box.delete("1.0", "end")
        for i in ins:
            self.insights_box.insert("end", "- " + i + "\n")

    def refresh_habits(self):
        user = self.user_var.get() or self.name_e.get().strip()
        if not user:
            self.habits_box.delete("1.0", "end"); return
        df = query_habits(user=user)
        self.habits_box.delete("1.0", "end")
        if df is None or df.empty:
            self.habits_box.insert("end", "No habits recorded.\n")
            return
        for _, r in df.tail(7).iterrows():
            self.habits_box.insert("end", f"{r['Date']}: Ex {r['Exercise Minutes']}m, Study {r['Study Minutes']}m, Screen {r['Screen Minutes']}m\n")

# run
def main():
    root = tk.Tk()
    app = ADHDApp(root) 
    root.mainloop()
if __name__ == "__main__":
    main()

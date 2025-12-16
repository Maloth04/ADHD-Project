# report.py
import pandas as pd
from fpdf import FPDF
import os
from storage_sql import query_entries

def export_excel_for_user(user=None, start_date=None, end_date=None, out_path="export.xlsx"):
    df = query_entries(user=user, start_date=start_date, end_date=end_date)
    df.to_excel(out_path, index=False)
    return out_path

def export_pdf_for_user(user=None, start_date=None, end_date=None, out_path="report.pdf"):
    df = query_entries(user=user, start_date=start_date, end_date=end_date)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0,10, f"ADHD Report - {user or 'All users'}", ln=True)
    pdf.ln(4)
    # table header
    cols = ["Date","Name","Focus","Cognitive Score","Sleep Hours","Screen Time","Mood","Notes"]
    for c in cols:
        pdf.set_font("Arial","B",9)
        pdf.cell(28,8,str(c),border=1)
    pdf.ln()
    pdf.set_font("Arial","",9)
    for _, r in df.iterrows():
        pdf.cell(28,8,str(r.get("Date","")),border=1)
        pdf.cell(28,8,str(r.get("Name","")),border=1)
        pdf.cell(28,8,str(r.get("Focus","")),border=1)
        pdf.cell(28,8,str(r.get("Cognitive Score","")),border=1)
        pdf.cell(28,8,str(r.get("Sleep Hours","")),border=1)
        pdf.cell(28,8,str(r.get("Screen Time","")),border=1)
        pdf.cell(28,8,str(r.get("Mood","")),border=1)
        pdf.cell(28,8,str((r.get("Notes",""))[:15]),border=1)
        pdf.ln()
    pdf.output(out_path)
    return out_path

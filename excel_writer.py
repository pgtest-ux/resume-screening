# excel_writer.py

from pathlib import Path
from typing import Dict
from datetime import datetime

from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Alignment, Border, Side, Font, PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo


BASE_COLUMNS = [
    "Candidate Name",
    "Email",
    "Graduation College",
    "Graduation Year"
]


# ======================================================
# INITIALIZATION
# ======================================================

def init_excel_if_missing(excel_path: Path, schema: dict) -> None:
    if excel_path.exists():
        return

    wb = Workbook()
    ws = wb.active
    ws.title = "Screening"

    skill_names = [s["name"] for s in schema.get("skills", [])]
    soft_names = [s["name"] for s in schema.get("soft_skills", [])]

    header = (
        BASE_COLUMNS
        + skill_names
        + soft_names
        + ["Overall Score", "Match %", "Comments", "Last Updated"]
    )

    ws.append(header)

    format_static_sheet(ws)
    create_or_update_table(ws)

    wb.save(excel_path)


# ======================================================
# UPSERT LOGIC (FAST)
# ======================================================

def upsert_candidate_row(excel_path: Path, score_result: Dict) -> None:
    wb = load_workbook(excel_path)
    ws = wb.active

    headers = [cell.value for cell in ws[1]]
    header_index = {name: i + 1 for i, name in enumerate(headers)}  # 1-based

    email = score_result.get("candidate_email", "")
    target_row = find_candidate_row(ws, header_index["Email"], email)

    if not target_row:
        target_row = ws.max_row + 1

    # Write base fields
    ws.cell(target_row, header_index["Candidate Name"], score_result.get("candidate_name", ""))
    ws.cell(target_row, header_index["Email"], email)
    ws.cell(target_row, header_index["Graduation College"], score_result.get("grad_college", ""))
    ws.cell(target_row, header_index["Graduation Year"], score_result.get("grad_year", ""))

    # Skill scores
    for skill, value in score_result.get("scores", {}).items():
        if skill in header_index:
            ws.cell(target_row, header_index[skill], value)

    overall_score = score_result.get("overall_score", 0)
    match_percent = round(score_result.get("match_percent", 0.0) * 100, 1)

    ws.cell(target_row, header_index["Overall Score"], overall_score)
    ws.cell(target_row, header_index["Match %"], match_percent)
    ws.cell(target_row, header_index["Comments"], score_result.get("comments", ""))
    ws.cell(
        target_row,
        header_index["Last Updated"],
        score_result.get("processed_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )

    # Color code scores
    apply_score_formatting(ws, target_row, header_index)

    # Resize table only (fast)
    create_or_update_table(ws)

    wb.save(excel_path)


# ======================================================
# DUPLICATE DETECTION
# ======================================================

def find_candidate_row(ws: Worksheet, email_column: int, email: str):
    for row in range(2, ws.max_row + 1):
        if ws.cell(row, email_column).value == email:
            return row
    return None


# ======================================================
# SCORE COLORING
# ======================================================

def apply_score_formatting(ws: Worksheet, row: int, header_index: Dict):
    score_cell = ws.cell(row, header_index["Overall Score"])
    percent_cell = ws.cell(row, header_index["Match %"])

    score = score_cell.value
    percent = percent_cell.value

    if score is not None:
        score_cell.fill = get_score_fill(score)

    if percent is not None:
        percent_cell.fill = get_score_fill(percent)


def get_score_fill(value):
    if value >= 80:
        return PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")  # Green
    elif value >= 60:
        return PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")  # Yellow
    else:
        return PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")  # Red


# ======================================================
# STATIC FORMATTING (RUN ONLY ONCE)
# ======================================================

def format_static_sheet(ws: Worksheet):
    # Style header
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="top")
        cell.border = Border(
            top=Side(style="thin"),
            bottom=Side(style="thin"),
            left=Side(style="thin"),
            right=Side(style="thin"),
        )

    # Freeze Row 1 and Column 2
    ws.freeze_panes = "C2"

    # Top align entire sheet
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrapText=True)


# ======================================================
# TABLE MANAGEMENT (FAST)
# ======================================================

def create_or_update_table(ws: Worksheet):
    if ws.max_row < 1:
        return

    last_row = ws.max_row
    last_col = ws.max_column
    table_ref = f"A1:{ws.cell(row=last_row, column=last_col).coordinate}"

    if ws.tables:
        table = list(ws.tables.values())[0]
        table.ref = table_ref
    else:
        table = Table(displayName="ScreeningTable", ref=table_ref)
        style = TableStyleInfo(
            name="TableStyleMedium2",
            showRowStripes=True,
        )
        table.tableStyleInfo = style
        ws.add_table(table)

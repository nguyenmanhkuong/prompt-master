#!/usr/bin/env python3
"""
BANKING FINANCIAL ANALYSIS DASHBOARD
Ngân hàng TMCP Phát triển Việt Nam (VDB)
Xuất Excel multi-sheet dashboard
"""

import json
import openpyxl
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side, numbers
)
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.series import SeriesLabel
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule, FormulaRule
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.chart.label import DataLabelList
import os

# ─── Load data ────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "../data/banking_mockdata.json")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

bank = data["bank_info"]
bench = data["benchmark"]
bs = data["balance_sheet"]
inc = data["income_statement"]
rat = data["ratios"]
cf = data["cash_flow"]
cam = data["camels"]
wks = data["weaknesses"]
rc_sum = data["root_causes_summary"]
perm = data["permissions"]

YEARS = ["2023", "2024", "2025"]

# ─── Style helpers ────────────────────────────────────────────────────────────
def hex_fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def thin_border():
    side = Side(style="thin", color="CCCCCC")
    return Border(left=side, right=side, top=side, bottom=side)

def bold_border():
    side = Side(style="medium", color="999999")
    return Border(left=side, right=side, top=side, bottom=side)

FONT_TITLE   = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
FONT_HEADER  = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
FONT_SUB     = Font(name="Calibri", size=12, bold=True, color="1a237e")
FONT_BOLD    = Font(name="Calibri", size=10, bold=True)
FONT_NORMAL  = Font(name="Calibri", size=10)
FONT_RED     = Font(name="Calibri", size=10, bold=True, color="C62828")
FONT_GREEN   = Font(name="Calibri", size=10, bold=True, color="2E7D32")
FONT_AMBER   = Font(name="Calibri", size=10, bold=True, color="E65100")

FILL_TITLE   = hex_fill("1a237e")
FILL_HEADER  = hex_fill("283593")
FILL_ALT     = hex_fill("EEF2FF")
FILL_RED     = hex_fill("FFEBEE")
FILL_AMBER   = hex_fill("FFF8E1")
FILL_GREEN   = hex_fill("E8F5E9")
FILL_WHITE   = hex_fill("FFFFFF")

ALIGN_CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
ALIGN_LEFT   = Alignment(horizontal="left",   vertical="center", wrap_text=True)
ALIGN_RIGHT  = Alignment(horizontal="right",  vertical="center")

def style_cell(cell, font=None, fill=None, alignment=None, border=None, number_format=None):
    if font:       cell.font = font
    if fill:       cell.fill = fill
    if alignment:  cell.alignment = alignment
    if border:     cell.border = border
    if number_format: cell.number_format = number_format

def write_header(ws, row, cols, values, fills=None, fonts=None, alignments=None):
    for i, (col, val) in enumerate(zip(cols, values)):
        c = ws.cell(row=row, column=col, value=val)
        style_cell(c,
                   font=fonts[i] if fonts else FONT_HEADER,
                   fill=fills[i] if fills else FILL_HEADER,
                   alignment=alignments[i] if alignments else ALIGN_CENTER,
                   border=bold_border())

def set_col_widths(ws, widths_dict):
    for col_letter, width in widths_dict.items():
        ws.column_dimensions[col_letter].width = width

def ratio_status(value, warn_low, warn_high=None, is_upper=True):
    """Return (status_color, status_text)"""
    if is_upper:
        if value <= warn_low:
            return "🔴 CRITICAL", FILL_RED, FONT_RED
        elif value <= (warn_low + (warn_high - warn_low)*0.3 if warn_high else warn_low * 1.15):
            return "🟡 WARNING", FILL_AMBER, FONT_AMBER
        else:
            return "🟢 OK", FILL_GREEN, FONT_GREEN
    else:
        if value >= warn_high:
            return "🔴 CRITICAL", FILL_RED, FONT_RED
        elif value >= warn_low:
            return "🟡 WARNING", FILL_AMBER, FONT_AMBER
        else:
            return "🟢 OK", FILL_GREEN, FONT_GREEN

def write_metric_row(ws, row, label, values, status_values=None,
                     benchmarks=None, fmt="#,##0.0", benchmark_fmt="#,##0.0"):
    ws.cell(row=row, column=1, value=label).font = FONT_BOLD
    ws.cell(row=row, column=1).fill = FILL_WHITE
    ws.cell(row=row, column=1).border = thin_border()
    ws.cell(row=row, column=1).alignment = ALIGN_LEFT

    for i, val in enumerate(values):
        col = i + 2
        c = ws.cell(row=row, column=col, value=val)
        c.number_format = fmt
        c.border = thin_border()
        c.alignment = ALIGN_RIGHT
        if status_values and status_values[i]:
            status, fill, font = status_values[i]
            c.fill = fill
            c.font = font

    if benchmarks:
        bc = ws.cell(row=row, column=len(values)+2, value=benchmarks)
        bc.number_format = benchmark_fmt
        bc.border = thin_border()
        bc.alignment = ALIGN_RIGHT
        bc.font = Font(name="Calibri", size=9, italic=True, color="666666")


# ═══════════════════════════════════════════════════════════════════════════════
wb = openpyxl.Workbook()
wb.remove(wb.active)  # remove default sheet

# ═══════════════════════════════════════════════════════════════════════════════
# SHEET 1 — Dashboard Tổng quan
# ═══════════════════════════════════════════════════════════════════════════════
ws1 = wb.create_sheet("📋 Tổng quan")
ws1.sheet_view.showGridLines = False
ws1.row_dimensions[1].height = 50
ws1.row_dimensions[2].height = 20

# Title bar
ws1.merge_cells("A1:M1")
c = ws1["A1"]
c.value = f"  🏦 {bank['name']} ({bank['short_name']})  |  BÁO CÁO TÀI CHÍNH CHUYÊN SÂU  |  {bank['report_quarter']}/{bank['report_year']}"
c.font = FONT_TITLE
c.fill = FILL_TITLE
c.alignment = ALIGN_LEFT

# Sub-header
ws1.merge_cells("A2:M2")
c = ws1["A2"]
c.value = f"  📅 Ngày cập nhật: {bank['report_date']}   |   👤 {bank['prepared_by']}   |   🔍 Kiểm toán: {bank['auditor']}   |   {bank['version']}"
c.font = Font(name="Calibri", size=9, italic=True, color="CCCCCC")
c.fill = hex_fill("0d1b4a")
c.alignment = ALIGN_LEFT

# CAMELS summary row — labels in row 3, scores in row 4
ws1.row_dimensions[3].height = 22
ws1.row_dimensions[4].height = 32

cam_labels = ["C", "A", "M", "E", "L", "S", "Tổng"]
cam_full_labels = ["Capital", "Asset", "Management", "Earnings", "Liquidity", "Sensitivity"]
cam_scores = [cam["2025"]["C"], cam["2025"]["A"], cam["2025"]["M"],
              cam["2025"]["E"], cam["2025"]["L"], cam["2025"]["S"]]
cam_total = sum(cam_scores)
cam_avg = cam_total / 6

for i, (lbl, s) in enumerate(zip(cam_labels, cam_scores + [cam_avg])):
    col = i + 2
    # Label row
    c = ws1.cell(row=3, column=col, value=lbl)
    c.font = FONT_HEADER
    c.fill = FILL_HEADER
    c.alignment = ALIGN_CENTER
    c.border = bold_border()
    # Score row
    c2 = ws1.cell(row=4, column=col, value=round(s, 2) if isinstance(s, float) else s)
    c2.font = Font(name="Calibri", size=20, bold=True, color="FFFFFF")
    c2.fill = hex_fill("C62828") if s <= 2 else (hex_fill("E65100") if s <= 3 else hex_fill("2E7D32"))
    c2.alignment = ALIGN_CENTER
    c2.border = bold_border()

# Full label row under scores
for i, fl in enumerate(cam_full_labels):
    col = i + 2
    c = ws1.cell(row=5, column=col, value=fl)
    c.font = Font(name="Calibri", size=8, color="777777")
    c.alignment = ALIGN_CENTER
ws1.row_dimensions[5].height = 14

# KPI Cards row — starts at row 6 (after CAMELS rows 3-5)
ws1.row_dimensions[6].height = 16
ws1.row_dimensions[7].height = 48
ws1.row_dimensions[8].height = 22
ws1.row_dimensions[9].height = 18

kpi_labels = ["CAR", "NPL Ratio", "LCR", "NIM", "ROE", "LDR"]
kpi_values_raw = [rat["2025"]["CAR"], rat["2025"]["NPL_Ratio"], rat["2025"]["LCR"],
                   rat["2025"]["NIM"], rat["2025"]["ROE"], rat["2025"]["LDR"]]
kpi_benchmarks = [bench["CAR_minimum"], bench["NPL_floor_warning"], bench["LCR_minimum"],
                   bench["NIM_avg_industry"], bench["ROE_avg_industry"], bench["LDR_maximum"]]
kpi_is_upper = [False, False, False, False, False, True]
kpi_fmts = ["0.0\"%\"", "0.0\"%\"", "0\"%\"", "0.00\"%\"", "0.0\"%\"", "0.0\"%\""]
kpi_yoy = [
    rat["2025"]["CAR"] - rat["2024"]["CAR"],
    rat["2025"]["NPL_Ratio"] - rat["2024"]["NPL_Ratio"],
    rat["2025"]["LCR"] - rat["2024"]["LCR"],
    rat["2025"]["NIM"] - rat["2024"]["NIM"],
    rat["2025"]["ROE"] - rat["2024"]["ROE"],
    rat["2025"]["LDR"] - rat["2024"]["LDR"],
]
kpi_colors = [
    "C62828" if rat["2025"]["CAR"] < bench["CAR_warning"] else ("E65100" if rat["2025"]["CAR"] < bench["CAR_minimum"] * 1.2 else "2E7D32"),
    "C62828" if rat["2025"]["NPL_Ratio"] >= bench["NPL_floor_danger"] else ("E65100" if rat["2025"]["NPL_Ratio"] >= bench["NPL_floor_warning"] else "2E7D32"),
    "C62828" if rat["2025"]["LCR"] < bench["LCR_minimum"] * 1.1 else ("E65100" if rat["2025"]["LCR"] < bench["LCR_minimum"] * 1.2 else "2E7D32"),
    "C62828" if rat["2025"]["NIM"] < 3.0 else ("E65100" if rat["2025"]["NIM"] < bench["NIM_avg_industry"] else "2E7D32"),
    "C62828" if rat["2025"]["ROE"] < 5 else ("E65100" if rat["2025"]["ROE"] < bench["ROE_avg_industry"] else "2E7D32"),
    "C62828" if rat["2025"]["LDR"] > bench["LDR_maximum"] else ("E65100" if rat["2025"]["LDR"] > bench["LDR_warning"] else "2E7D32"),
]

col = 1
for i in range(6):
    ws1.merge_cells(start_row=7, start_column=col, end_row=7, end_column=col+1)
    ws1.merge_cells(start_row=8, start_column=col, end_row=8, end_column=col+1)
    ws1.merge_cells(start_row=9, start_column=col, end_row=9, end_column=col+1)

    # Label
    lc = ws1.cell(row=7, column=col, value=kpi_labels[i])
    lc.font = Font(name="Calibri", size=9, bold=True, color="666666")
    lc.alignment = ALIGN_CENTER

    # Value
    vc = ws1.cell(row=8, column=col, value=kpi_values_raw[i])
    vc.number_format = kpi_fmts[i]
    vc.font = Font(name="Calibri", size=22, bold=True, color=kpi_colors[i])
    vc.alignment = ALIGN_CENTER

    # YoY
    yoy = kpi_yoy[i]
    yoy_val = kpi_values_raw[i]
    if kpi_is_upper[i]:
        yoy_color = "2E7D32" if yoy < 0 else ("E65100" if yoy < (kpi_benchmarks[i] - yoy_val) * 0.3 else "C62828")
    else:
        yoy_color = "2E7D32" if yoy > 0 else ("E65100" if abs(yoy) < abs(kpi_values_raw[i] - kpi_benchmarks[i]) * 0.3 else "C62828")

    yc = ws1.cell(row=9, column=col, value=f"{'↑' if yoy > 0 else '↓' if yoy < 0 else '→'} {abs(yoy):.1f} YoY")
    yc.font = Font(name="Calibri", size=8, bold=True, color=yoy_color)
    yc.alignment = ALIGN_CENTER

    for r in [7, 8, 9]:
        ws1.cell(row=r, column=col).fill = hex_fill("F8F9FA")
        ws1.cell(row=r, column=col).border = thin_border()
        ws1.cell(row=r, column=col+1).fill = hex_fill("F8F9FA")
        ws1.cell(row=r, column=col+1).border = thin_border()
    col += 2

# Spacer
ws1.row_dimensions[10].height = 10

# Alert section
ws1.merge_cells("A11:M11")
c = ws1["A11"]
c.value = "  ⚠️  CẢNH BÁO & ĐIỂM YẾU CỐT LÕI"
c.font = FONT_HEADER
c.fill = hex_fill("B71C1C")
c.alignment = ALIGN_LEFT

ws1.row_dimensions[12].height = 28
ws1.merge_cells("A12:B12")
ws1["A12"].value = "ID"
ws1["A12"].font = FONT_HEADER; ws1["A12"].fill = FILL_HEADER; ws1["A12"].alignment = ALIGN_CENTER
ws1.merge_cells("C12:F12")
ws1["C12"].value = "Điểm yếu"
ws1["C12"].font = FONT_HEADER; ws1["C12"].fill = FILL_HEADER; ws1["C12"].alignment = ALIGN_CENTER
ws1.merge_cells("G12:J12")
ws1["G12"].value = "Root Cause"
ws1["G12"].font = FONT_HEADER; ws1["G12"].fill = FILL_HEADER; ws1["G12"].alignment = ALIGN_CENTER
ws1.merge_cells("K12:L12")
ws1["K12"].value = "Mức độ"
ws1["K12"].font = FONT_HEADER; ws1["K12"].fill = FILL_HEADER; ws1["K12"].alignment = ALIGN_CENTER
ws1.merge_cells("M12:M12")
ws1["M12"].value = "Quick Win"
ws1["M12"].font = FONT_HEADER; ws1["M12"].fill = FILL_HEADER; ws1["M12"].alignment = ALIGN_CENTER

severity_fills = {"CRITICAL": hex_fill("FFCDD2"), "HIGH": hex_fill("FFE0B2"), "MEDIUM": hex_fill("FFF9C4")}
severity_fonts = {"CRITICAL": FONT_RED, "HIGH": FONT_AMBER, "FONT_YELLOW": Font(name="Calibri", size=10, bold=True, color="F57F17")}

for i, wk in enumerate(wks):
    row = 13 + i
    ws1.row_dimensions[row].height = 36

    ws1.merge_cells(f"A{row}:B{row}")
    c = ws1.cell(row=row, column=1, value=wk["id"])
    c.font = FONT_BOLD; c.fill = severity_fills.get(wk["severity"], FILL_AMBER)
    c.alignment = ALIGN_CENTER; c.border = thin_border()

    ws1.merge_cells(f"C{row}:F{row}")
    c = ws1.cell(row=row, column=3, value=wk["title"])
    c.font = FONT_BOLD; c.fill = severity_fills.get(wk["severity"], FILL_AMBER)
    c.alignment = ALIGN_LEFT; c.border = thin_border()

    ws1.merge_cells(f"G{row}:J{row}")
    c = ws1.cell(row=row, column=7, value=wk["root_cause"][:120] + "..." if len(wk["root_cause"]) > 120 else wk["root_cause"])
    c.font = FONT_NORMAL; c.fill = FILL_WHITE; c.alignment = ALIGN_LEFT; c.border = thin_border()

    ws1.merge_cells(f"K{row}:L{row}")
    c = ws1.cell(row=row, column=11, value=wk["severity"])
    c.font = severity_fonts.get(wk["severity"], FONT_AMBER)
    c.fill = severity_fills.get(wk["severity"], FILL_AMBER)
    c.alignment = ALIGN_CENTER; c.border = thin_border()

    ws1.merge_cells(f"M{row}:M{row}")
    c = ws1.cell(row=row, column=13, value=wk["quick_win"][:60] + "..." if len(wk["quick_win"]) > 60 else wk["quick_win"])
    c.font = Font(name="Calibri", size=9, italic=True, color="1a237e")
    c.fill = hex_fill("E8EAF6"); c.alignment = ALIGN_LEFT; c.border = thin_border()

# Financial summary table
start_row = 13 + len(wks) + 2
ws1.merge_cells(f"A{start_row}:M{start_row}")
c = ws1[f"A{start_row}"]
c.value = "  📈 CHỈ SỐ TÀI CHÍNH CHỦ YẾU (Đơn vị: Tỷ VND)"
c.font = FONT_HEADER; c.fill = FILL_HEADER; c.alignment = ALIGN_LEFT

row = start_row + 1
fs_headers = ["Chỉ số", "2023", "2024", "2025", "YoY Δ", "Benchmark", "Trạng thái"]
fs_widths  = [35, 12, 12, 12, 10, 14, 14]
for i, (h, w) in enumerate(zip(fs_headers, fs_widths)):
    c = ws1.cell(row=row, column=i+1, value=h)
    c.font = FONT_HEADER; c.fill = hex_fill("3949AB"); c.alignment = ALIGN_CENTER; c.border = bold_border()

financial_rows = [
    ("Tổng tài sản", bs["2023"]["total_assets"], bs["2024"]["total_assets"], bs["2025"]["total_assets"], "total_assets", "B"),
    ("Dư nợ cho vay gross", bs["2023"]["loans_to_customers_gross"], bs["2024"]["loans_to_customers_gross"], bs["2025"]["loans_to_customers_gross"], "loans_gross", "B"),
    ("Tiền gửi khách hàng", bs["2023"]["customer_deposits"], bs["2024"]["customer_deposits"], bs["2025"]["customer_deposits"], "deposits", "B"),
    ("Vốn chủ sở hữu", bs["2023"]["total_equity"], bs["2024"]["total_equity"], bs["2025"]["total_equity"], "equity", "B"),
    ("Thu nhập lãi thuần", inc["2023"]["net_interest_income"], inc["2024"]["net_interest_income"], inc["2025"]["net_interest_income"], "NII", "B"),
    ("Tổng thu nhập", inc["2023"]["total_income"], inc["2024"]["total_income"], inc["2025"]["total_income"], "total_income", "B"),
    ("Lợi nhuận sau thuế", inc["2023"]["profit_after_tax"], inc["2024"]["profit_after_tax"], inc["2025"]["profit_after_tax"], "PAT", "B"),
]

for j, (label, v23, v24, v25, key, _) in enumerate(financial_rows):
    r = row + 1 + j
    ws1.row_dimensions[r].height = 18
    c = ws1.cell(row=r, column=1, value=label)
    c.font = FONT_NORMAL; c.fill = FILL_ALT if j % 2 == 0 else FILL_WHITE
    c.alignment = ALIGN_LEFT; c.border = thin_border()

    for yr_idx, val in enumerate([v23, v24, v25]):
        c = ws1.cell(row=r, column=2+yr_idx, value=val)
        c.number_format = "#,##0"
        c.font = FONT_NORMAL
        c.fill = FILL_ALT if j % 2 == 0 else FILL_WHITE
        c.alignment = ALIGN_RIGHT; c.border = thin_border()

    yoy_delta = v25 - v24
    c = ws1.cell(row=r, column=5, value=yoy_delta)
    c.number_format = "#,##0"
    c.font = Font(name="Calibri", size=10, bold=True, color="2E7D32" if yoy_delta > 0 else "C62828")
    c.fill = FILL_ALT if j % 2 == 0 else FILL_WHITE
    c.alignment = ALIGN_RIGHT; c.border = thin_border()

    c = ws1.cell(row=r, column=6, value="-")
    c.font = FONT_NORMAL; c.fill = FILL_ALT if j % 2 == 0 else FILL_WHITE
    c.alignment = ALIGN_CENTER; c.border = thin_border()

    c = ws1.cell(row=r, column=7, value="—")
    c.font = FONT_NORMAL; c.fill = FILL_ALT if j % 2 == 0 else FILL_WHITE
    c.alignment = ALIGN_CENTER; c.border = thin_border()

set_col_widths(ws1, {"A": 38, "B": 14, "C": 14, "D": 14, "E": 12, "F": 16, "G": 16,
                     "H": 12, "I": 12, "J": 12, "K": 12, "L": 12, "M": 30})


# ═══════════════════════════════════════════════════════════════════════════════
# SHEET 2 — CAMELS Scorecard
# ═══════════════════════════════════════════════════════════════════════════════
ws2 = wb.create_sheet("📊 CAMELS Scorecard")
ws2.sheet_view.showGridLines = False

ws2.merge_cells("A1:I1")
c = ws2["A1"]
c.value = f"  📊 CAMELS SCORECARD  |  {bank['name']}  |  2023 – 2025"
c.font = FONT_TITLE; c.fill = FILL_TITLE; c.alignment = ALIGN_LEFT

# Headers
cam_headers2 = ["Thành phần", "Trọng số", "2023", "2024", "2025", "Δ 2023→2025", "Benchmark", "Trạng thái 2025", "Ghi chú"]
for i, h in enumerate(cam_headers2):
    c = ws2.cell(row=2, column=i+1, value=h)
    c.font = FONT_HEADER; c.fill = FILL_HEADER; c.alignment = ALIGN_CENTER; c.border = bold_border()

cam_data = [
    ("C — Capital Adequacy", 0.20, cam["2023"]["C"], cam["2024"]["C"], cam["2025"]["C"],
     "CAR: 11.8% → 10.3%  |  Tier1: 9.5% → 8.1%", "CAR ≥ 8%", "Sát ngưỡng, rủi ro cao"),
    ("A — Asset Quality",     0.25, cam["2023"]["A"], cam["2024"]["A"], cam["2025"]["A"],
     "NPL: 3.0% → 4.1%  |  Coverage: 68% → 58.5%", "NPL < 3%", "NPL vượt ngưỡng cảnh báo"),
    ("M — Management",       0.15, cam["2023"]["M"], cam["2024"]["M"], cam["2025"]["M"],
     "Cost/Income: 45.8% → 52.9%", "Cost/Income < 45%", "Chi phí tăng nhanh"),
    ("E — Earnings",         0.15, cam["2023"]["E"], cam["2024"]["E"], cam["2025"]["E"],
     "ROE: 14.5% → 0%  |  NIM: 3.53% → 2.95%", "ROE > 10%", "Lợi nhuận suy giảm nghiêm trọng"),
    ("L — Liquidity",        0.15, cam["2023"]["L"], cam["2024"]["L"], cam["2025"]["L"],
     "LCR: 125 → 108  |  LDR: 79% → 84.5%", "LCR ≥ 100%", "Thanh khoản giảm sát floor"),
    ("S — Sensitivity",       0.10, cam["2023"]["S"], cam["2024"]["S"], cam["2025"]["S"],
     "FX exposure tăng, VAR chưa được báo cáo", "VAR trong limit", "Cần theo dõi FX rủi ro"),
]

cam_score_fills = {1: hex_fill("B71C1C"), 2: hex_fill("FF8A65"),
                   3: hex_fill("FFE082"), 4: hex_fill("A5D6A7"), 5: hex_fill("2E7D32")}
cam_score_fonts = {1: Font(name="Calibri", size=13, bold=True, color="FFFFFF"),
                   2: Font(name="Calibri", size=13, bold=True, color="FFFFFF"),
                   3: Font(name="Calibri", size=13, bold=True, color="333333"),
                   4: Font(name="Calibri", size=13, bold=True, color="FFFFFF"),
                   5: Font(name="Calibri", size=13, bold=True, color="FFFFFF")}

total_2023 = sum(row[2] * row[1] for row in cam_data)
total_2024 = sum(row[3] * row[1] for row in cam_data)
total_2025 = sum(row[4] * row[1] for row in cam_data)

for i, row_data in enumerate(cam_data):
    r = 3 + i
    ws2.row_dimensions[r].height = 22

    c = ws2.cell(row=r, column=1, value=row_data[0])
    c.font = FONT_BOLD; c.fill = FILL_ALT if i % 2 == 0 else FILL_WHITE
    c.alignment = ALIGN_LEFT; c.border = thin_border()

    c = ws2.cell(row=r, column=2, value=f"{row_data[1]*100:.0f}%")
    c.font = FONT_NORMAL; c.fill = FILL_ALT if i % 2 == 0 else FILL_WHITE
    c.alignment = ALIGN_CENTER; c.border = thin_border()

    for yr_idx, score in enumerate([row_data[2], row_data[3], row_data[4]]):
        col = 3 + yr_idx
        c = ws2.cell(row=r, column=col, value=score)
        c.font = cam_score_fonts.get(score, FONT_NORMAL)
        c.fill = cam_score_fills.get(score, FILL_WHITE)
        c.alignment = ALIGN_CENTER; c.border = thin_border()

    c = ws2.cell(row=r, column=6, value=row_data[4] - row_data[2])
    c.font = Font(name="Calibri", size=10, bold=True, color="C62828")
    c.fill = FILL_ALT if i % 2 == 0 else FILL_WHITE
    c.alignment = ALIGN_CENTER; c.border = thin_border()

    c = ws2.cell(row=r, column=7, value=row_data[5])
    c.font = Font(name="Calibri", size=9, italic=True, color="555555")
    c.fill = FILL_ALT if i % 2 == 0 else FILL_WHITE
    c.alignment = ALIGN_LEFT; c.border = thin_border()

    c = ws2.cell(row=r, column=8, value=row_data[6])
    c.font = FONT_RED if row_data[4] <= 2 else (FONT_AMBER if row_data[4] <= 3 else FONT_GREEN)
    c.fill = FILL_RED if row_data[4] <= 2 else (FILL_AMBER if row_data[4] <= 3 else FILL_GREEN)
    c.alignment = ALIGN_CENTER; c.border = thin_border()

    c = ws2.cell(row=r, column=9, value=row_data[7])
    c.font = FONT_NORMAL; c.fill = FILL_ALT if i % 2 == 0 else FILL_WHITE
    c.alignment = ALIGN_LEFT; c.border = thin_border()

# Total row
r_total = 3 + len(cam_data)
ws2.row_dimensions[r_total].height = 24
total_fills = {1: FILL_RED, 2: FILL_AMBER}
total_fonts = {1: FONT_RED, 2: FONT_AMBER, 3: Font(name="Calibri", size=12, bold=True, color="E65100")}

for col, val, font, fill in [
    (1, "TỔNG ĐIỂM CAMELS", FONT_BOLD, hex_fill("1a237e")),
    (2, "100%", FONT_BOLD, hex_fill("1a237e")),
    (3, round(total_2023, 2), total_fonts.get(int(round(total_2023))), total_fills.get(int(round(total_2023)), FILL_WHITE)),
    (4, round(total_2024, 2), total_fonts.get(int(round(total_2024))), total_fills.get(int(round(total_2024)), FILL_WHITE)),
    (5, round(total_2025, 2), total_fonts.get(int(round(total_2025))), total_fills.get(int(round(total_2025)), FILL_WHITE)),
    (6, round(total_2025 - total_2023, 2), FONT_RED, hex_fill("FFEBEE")),
    (7, "≤ 2.0: Nguy hiểm  |  2.1-3.0: Cảnh báo  |  3.1-4.0: Tốt", Font(name="Calibri", size=9, italic=True), hex_fill("E8EAF6")),
    (8, "⚠️ CAMELS giảm liên tục", FONT_RED, FILL_RED),
    (9, "Cần can thiệp khẩn cấp", FONT_RED, FILL_RED),
]:
    c = ws2.cell(row=r_total, column=col, value=val)
    c.font = font; c.fill = fill; c.alignment = ALIGN_CENTER; c.border = bold_border()

# Scale legend
r_legend = r_total + 2
ws2.merge_cells(f"A{r_legend}:I{r_legend}")
c = ws2[f"A{r_legend}"]
c.value = "  THANG ĐIỂM CAMELS"
c.font = FONT_HEADER; c.fill = hex_fill("37474F"); c.alignment = ALIGN_LEFT

legend_data = [(1, "🔴 Nguy hiểm — Cần can thiệp ngay", "FFCDD2"),
                (2, "🟠 Cảnh báo — Giám sát chặt", "FFE0B2"),
                (3, "🟡 Trung bình — Cần cải thiện", "FFF9C4"),
                (4, "🟢 Khá — Hoạt động tốt", "C8E6C9"),
                (5, "🟢 Tốt — Lành mạnh", "A5D6A7")]
for idx, (score, desc, clr) in enumerate(legend_data):
    r = r_legend + 1 + idx
    ws2.cell(row=r, column=1, value=score).font = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
    ws2.cell(row=r, column=1).fill = hex_fill(clr); ws2.cell(row=r, column=1).alignment = ALIGN_CENTER
    ws2.merge_cells(f"B{r}:I{r}")
    c = ws2.cell(row=r, column=2, value=desc)
    c.font = FONT_NORMAL; c.fill = hex_fill(clr); c.alignment = ALIGN_LEFT

set_col_widths(ws2, {"A": 28, "B": 10, "C": 10, "D": 10, "E": 10, "F": 14, "G": 38, "H": 20, "I": 28})


# ═══════════════════════════════════════════════════════════════════════════════
# SHEET 3 — Bảng Cân đối Kế toán
# ═══════════════════════════════════════════════════════════════════════════════
ws3 = wb.create_sheet("💰 Bảng CĐKT")
ws3.sheet_view.showGridLines = False

ws3.merge_cells("A1:H1")
c = ws3["A1"]
c.value = f"  💰 BẢNG CÂN ĐỐI KẾ TOÁN  |  {bank['name']}  |  Đơn vị: Tỷ VND  |  2023–2025"
c.font = FONT_TITLE; c.fill = FILL_TITLE; c.alignment = ALIGN_LEFT

bs_headers = ["Khoản mục", "2023", "% Tổng TS", "2024", "% Tổng TS", "2025", "% Tổng TS", "Δ 2024→2025"]
for i, h in enumerate(bs_headers):
    c = ws3.cell(row=2, column=i+1, value=h)
    c.font = FONT_HEADER; c.fill = FILL_HEADER; c.alignment = ALIGN_CENTER; c.border = bold_border()

bs_items = [
    ("TÀI SẢN", None, True, None),
    ("  Tiền mặt và vàng", bs["2023"]["cash_and_gold"], False, bs["2025"]["cash_and_gold"]),
    ("  Dự trữ tại NHNN", bs["2023"]["balances_at_central_bank"], False, bs["2025"]["balances_at_central_bank"]),
    ("  Tiền gửi tại các TCTD khác", bs["2023"]["balances_at_other_banks"], False, bs["2025"]["balances_at_other_banks"]),
    ("  Cho vay khách hàng (gross)", bs["2023"]["loans_to_customers_gross"], False, bs["2025"]["loans_to_customers_gross"]),
    ("  (Trừ) Dự phòng rủi ro", bs["2023"]["loan_loss_provision"], False, bs["2025"]["loan_loss_provision"]),
    ("  Cho vay khách hàng (net)", bs["2023"]["loans_to_customers_net"], False, bs["2025"]["loans_to_customers_net"]),
    ("  Chứng khoán đầu tư", bs["2023"]["investment_securities"], False, bs["2025"]["investment_securities"]),
    ("  Tài sản cố định", bs["2023"]["fixed_assets"], False, bs["2025"]["fixed_assets"]),
    ("  Tài sản khác", bs["2023"]["other_assets"], False, bs["2025"]["other_assets"]),
    ("  TỔNG TÀI SẢN", bs["2023"]["total_assets"], True, bs["2025"]["total_assets"]),
    ("NGUỒN VỐN", None, True, None),
    ("  Vay từ các TCTD khác", bs["2023"]["liabilities_to_banks"], False, bs["2025"]["liabilities_to_banks"]),
    ("  Tiền gửi khách hàng", bs["2023"]["customer_deposits"], False, bs["2025"]["customer_deposits"]),
    ("  Phát hành giấy tờ có giá", bs["2023"]["debt_securities_issued"], False, bs["2025"]["debt_securities_issued"]),
    ("  Các khoản vay khác", bs["2023"]["other_borrowings"], False, bs["2025"]["other_borrowings"]),
    ("  Nợ phải trả khác", bs["2023"]["other_liabilities"], False, bs["2025"]["other_liabilities"]),
    ("  TỔNG NỢ PHẢI TRẢ", bs["2023"]["total_liabilities"], True, bs["2025"]["total_liabilities"]),
    ("VỐN CHỦ SỞ HỮU", None, True, None),
    ("  Vốn điều lệ", bs["2023"]["share_capital"], False, bs["2025"]["share_capital"]),
    ("  Thặng dư vốn cổ phần", bs["2023"]["share_premium"], False, bs["2025"]["share_premium"]),
    ("  Lợi nhuận giữ lại", bs["2023"]["retained_earnings"], False, bs["2025"]["retained_earnings"]),
    ("  TỔNG VỐN CHỦ SỞ HỮU", bs["2023"]["total_equity"], True, bs["2025"]["total_equity"]),
    ("  TỔNG NGUỒN VỐN", bs["2023"]["total_assets"], True, bs["2025"]["total_assets"]),
]

for i, item in enumerate(bs_items):
    r = 3 + i
    ws3.row_dimensions[r].height = 18
    label, v23, is_total, v25 = item

    if is_total and v23 is None:
        c = ws3.cell(row=r, column=1, value=label)
        c.font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        c.fill = hex_fill("1a237e"); c.alignment = ALIGN_LEFT; c.border = bold_border()
        for col in range(2, 9):
            ws3.cell(row=r, column=col).fill = hex_fill("1a237e")
            ws3.cell(row=r, column=col).border = bold_border()
        continue

    is_bold_row = "TỔNG" in label
    c = ws3.cell(row=r, column=1, value=label)
    c.font = Font(name="Calibri", size=10, bold=is_bold_row)
    c.fill = hex_fill("EEF2FF") if is_bold_row else (FILL_ALT if i % 2 == 0 else FILL_WHITE)
    c.alignment = ALIGN_LEFT; c.border = thin_border()

    vals_3yr = [bs["2023"], bs["2024"], bs["2025"]]
    for yr_idx, yr_data in enumerate(vals_3yr):
        val = yr_data.get(label.strip().lower().replace(" ", "_").replace("(", "").replace(")", "").replace("(", "").replace(")", "").replace(",", "").replace("(", "").replace(")", "").replace("__", "_")[:40], None)
        if val is None:
            key_map = {
                "tiền mặt và vàng": "cash_and_gold",
                "dự trữ tại nhnn": "balances_at_central_bank",
                "tiền gửi tại các tctd khác": "balances_at_other_banks",
                "cho vay khách hàng (gross)": "loans_to_customers_gross",
                "(trừ) dự phòng rủi ro": "loan_loss_provision",
                "cho vay khách hàng (net)": "loans_to_customers_net",
                "chứng khoán đầu tư": "investment_securities",
                "tài sản cố định": "fixed_assets",
                "tài sản khác": "other_assets",
                "tổng tài sản": "total_assets",
                "vay từ các tctd khác": "liabilities_to_banks",
                "tiền gửi khách hàng": "customer_deposits",
                "phát hành giấy tờ có giá": "debt_securities_issued",
                "các khoản vay khác": "other_borrowings",
                "nợ phải trả khác": "other_liabilities",
                "tổng nợ phải trả": "total_liabilities",
                "vốn điều lệ": "share_capital",
                "thặng dư vốn cổ phần": "share_premium",
                "lợi nhuận giữ lại": "retained_earnings",
                "tổng vốn chủ sở hữu": "total_equity",
                "tổng nguồn vốn": "total_assets",
            }
            search_label = label.strip().lower()
            val = yr_data.get(key_map.get(search_label), 0)

        col_val = 2 + yr_idx * 2
        col_pct = 3 + yr_idx * 2

        cv = ws3.cell(row=r, column=col_val, value=val)
        cv.number_format = "#,##0"
        cv.font = Font(name="Calibri", size=10, bold=is_bold_row)
        cv.fill = hex_fill("EEF2FF") if is_bold_row else (FILL_ALT if i % 2 == 0 else FILL_WHITE)
        cv.alignment = ALIGN_RIGHT; cv.border = thin_border()

        pct = (val / yr_data["total_assets"]) * 100 if yr_data["total_assets"] > 0 and val else 0
        cp = ws3.cell(row=r, column=col_pct, value=pct / 100 if val else 0)
        cp.number_format = "0.0%"
        cp.font = Font(name="Calibri", size=9, bold=is_bold_row)
        cp.fill = hex_fill("EEF2FF") if is_bold_row else (FILL_ALT if i % 2 == 0 else FILL_WHITE)
        cp.alignment = ALIGN_RIGHT; cp.border = thin_border()

    # YoY change in col 8
    v24 = bs["2024"].get(key_map.get(label.strip().lower(), ""), 0)
    yoy = v25 - v24
    cy = ws3.cell(row=r, column=8, value=yoy)
    cy.number_format = "#,##0"
    cy.font = Font(name="Calibri", size=10, bold=is_bold_row,
                   color="2E7D32" if yoy > 0 else "C62828")
    cy.fill = hex_fill("EEF2FF") if is_bold_row else (FILL_ALT if i % 2 == 0 else FILL_WHITE)
    cy.alignment = ALIGN_RIGHT; cy.border = thin_border()

set_col_widths(ws3, {"A": 38, "B": 14, "C": 10, "D": 14, "E": 10, "F": 14, "G": 10, "H": 14})


# ═══════════════════════════════════════════════════════════════════════════════
# SHEET 4 — Báo cáo KQKD
# ═══════════════════════════════════════════════════════════════════════════════
ws4 = wb.create_sheet("📉 Báo cáo KQKD")
ws4.sheet_view.showGridLines = False

ws4.merge_cells("A1:I1")
c = ws4["A1"]
c.value = f"  📉 BÁO CÁO KẾT QUẢ KINH DOANH  |  {bank['name']}  |  Đơn vị: Tỷ VND  |  2023–2025"
c.font = FONT_TITLE; c.fill = FILL_TITLE; c.alignment = ALIGN_LEFT

inc_headers = ["Khoản mục", "2023", "% Thu nhập", "2024", "% Thu nhập", "2025", "% Thu nhập", "Δ 2024→2025", "Ghi chú"]
for i, h in enumerate(inc_headers):
    c = ws4.cell(row=2, column=i+1, value=h)
    c.font = FONT_HEADER; c.fill = FILL_HEADER; c.alignment = ALIGN_CENTER; c.border = bold_border()

inc_items = [
    ("Thu nhập lãi thuần", "net_interest_income", True),
    ("Thu nhập phí", "fee_income", False),
    ("Lãi từ kinh doanh ngoại hối", "fx_trading_gain", False),
    ("Lãi từ chứng khoán đầu tư", "investment_securities_gain", False),
    ("Thu nhập khác", "other_income", False),
    ("TỔNG THU NHẬP", "total_income", True),
    ("Chi phí trích lập dự phòng", "credit_loss_expense", False),
    ("Chi phí nhân sự", "staff_cost", False),
    ("Chi phí hoạt động khác", "other_operating_expense", False),
    ("TỔNG CHI PHÍ HOẠT ĐỘNG", "total_operating_expense", True),
    ("LỢI NHUẬN TRƯỚC THUẾ", "profit_before_tax", True),
    ("Thuế thu nhập", "tax_expense", False),
    ("LỢI NHUẬN SAU THUẾ", "profit_after_tax", True),
]

note_map = {
    "net_interest_income": "NIM giảm: 3.53% → 2.95%",
    "fee_income": "Thu nhập phí tăng 23.8% trong 2 năm",
    "profit_after_tax": "⚠️ Lợi nhuận 2025 về sát 0",
    "credit_loss_expense": "⚠️ Tăng 74% so với 2023",
    "total_operating_expense": "⚠️ Cost/Income: 45.8% → 52.9%",
}

for i, (label, key, is_bold) in enumerate(inc_items):
    r = 3 + i
    ws4.row_dimensions[r].height = 18

    c = ws4.cell(row=r, column=1, value=label)
    c.font = Font(name="Calibri", size=10, bold=is_bold, color="FFFFFF" if is_bold else "333333")
    c.fill = hex_fill("1a237e") if is_bold else (FILL_ALT if i % 2 == 0 else FILL_WHITE)
    c.alignment = ALIGN_LEFT; c.border = thin_border()

    for yr_idx, yr_key in enumerate(["2023", "2024", "2025"]):
        val = inc[yr_key].get(key, 0)
        total_inc = inc[yr_key]["total_income"]

        col_val = 2 + yr_idx * 2
        col_pct = 3 + yr_idx * 2

        cv = ws4.cell(row=r, column=col_val, value=val)
        cv.number_format = "#,##0"
        cv.font = Font(name="Calibri", size=10, bold=is_bold)
        cv.fill = hex_fill("1a237e") if is_bold else (FILL_ALT if i % 2 == 0 else FILL_WHITE)
        cv.alignment = ALIGN_RIGHT; cv.border = thin_border()

        pct_val = val / total_inc if total_inc > 0 else 0
        cp = ws4.cell(row=r, column=col_pct, value=pct_val)
        cp.number_format = "0.0%"
        cp.font = Font(name="Calibri", size=9)
        cp.fill = hex_fill("1a237e") if is_bold else (FILL_ALT if i % 2 == 0 else FILL_WHITE)
        cp.alignment = ALIGN_RIGHT; cp.border = thin_border()

    # YoY
    yoy = inc["2025"].get(key, 0) - inc["2024"].get(key, 0)
    cy = ws4.cell(row=r, column=8, value=yoy)
    cy.number_format = "#,##0"
    yoy_color = "2E7D32" if yoy > 0 else "C62828"
    if key in ["credit_loss_expense", "staff_cost", "other_operating_expense"]:
        yoy_color = "2E7D32" if yoy < 0 else "C62828"
    cy.font = Font(name="Calibri", size=10, bold=is_bold, color=yoy_color)
    cy.fill = hex_fill("1a237e") if is_bold else (FILL_ALT if i % 2 == 0 else FILL_WHITE)
    cy.alignment = ALIGN_RIGHT; cy.border = thin_border()

    # Note
    note = note_map.get(key, "")
    cn = ws4.cell(row=r, column=9, value=note)
    cn.font = Font(name="Calibri", size=9, italic=True,
                   color="C62828" if "⚠" in note else "555555")
    cn.fill = hex_fill("1a237e") if is_bold else (FILL_ALT if i % 2 == 0 else FILL_WHITE)
    cn.alignment = ALIGN_LEFT; cn.border = thin_border()

# Dupont analysis
r_dupont = 3 + len(inc_items) + 2
ws4.merge_cells(f"A{r_dupont}:I{r_dupont}")
c = ws4[f"A{r_dupont}"]
c.value = "  📐 PHÂN TÍCH DUPONT"
c.font = FONT_HEADER; c.fill = hex_fill("37474F"); c.alignment = ALIGN_LEFT

dup_headers = ["Chỉ số", "2023", "2024", "2025", "Δ 2024→2025"]
for i, h in enumerate(dup_headers):
    c = ws4.cell(row=r_dupont+1, column=i+1, value=h)
    c.font = FONT_HEADER; c.fill = hex_fill("455A64"); c.alignment = ALIGN_CENTER; c.border = bold_border()

dup_data = [
    ("ROE (%)", [rat[y]["ROE"] for y in YEARS]),
    ("ROA (%)", [rat[y]["ROA"] for y in YEARS]),
    ("NIM (%)", [rat[y]["NIM"] for y in YEARS]),
    ("Cost-to-Income (%)", [rat[y]["Cost_to_Income"] for y in YEARS]),
    ("EPS (VND)", [inc[y]["eps"] for y in YEARS]),
    ("Tăng trưởng dư nợ (%)", [rat[y]["Growth_Loans"] for y in YEARS]),
    ("Tăng trưởng tiền gửi (%)", [rat[y]["Growth_Deposits"] for y in YEARS]),
]

for i, (label, vals) in enumerate(dup_data):
    r = r_dupont + 2 + i
    ws4.row_dimensions[r].height = 18
    c = ws4.cell(row=r, column=1, value=label)
    c.font = FONT_BOLD; c.fill = FILL_ALT if i % 2 == 0 else FILL_WHITE
    c.alignment = ALIGN_LEFT; c.border = thin_border()

    for j, v in enumerate(vals):
        cv = ws4.cell(row=r, column=2+j, value=v)
        cv.number_format = "0.00" if "%" in label else "#,##0"
        cv.font = FONT_NORMAL; cv.fill = FILL_ALT if i % 2 == 0 else FILL_WHITE
        cv.alignment = ALIGN_RIGHT; cv.border = thin_border()

        if "%" in label:
            # Color by trend
            if j == 2:  # 2025
                is_bad = (v < rat["2024"][label.replace(" (%)", "").lower().replace(" ", "_")] if label.lower().replace(" ", "_").replace("(", "").replace(")", "") not in ["cost-to-income (%)"] else v > rat["2024"]["cost_to_income"])
                cv.font = Font(name="Calibri", size=10, bold=True,
                               color="C62828" if is_bad else "2E7D32")

    yoy = vals[2] - vals[1]
    cy = ws4.cell(row=r, column=5, value=yoy)
    cy.number_format = "0.00" if "%" in label else "#,##0"
    cy.font = Font(name="Calibri", size=10, bold=True,
                   color="C62828" if (yoy < 0 if "%" in label and "cost" not in label.lower() else yoy > 0) else "2E7D32")
    cy.fill = FILL_ALT if i % 2 == 0 else FILL_WHITE
    cy.alignment = ALIGN_RIGHT; cy.border = thin_border()

set_col_widths(ws4, {"A": 35, "B": 13, "C": 11, "D": 13, "E": 11, "F": 13, "G": 11, "H": 13, "I": 30})


# ═══════════════════════════════════════════════════════════════════════════════
# SHEET 5 — Thanh khoản & Vốn
# ═══════════════════════════════════════════════════════════════════════════════
ws5 = wb.create_sheet("💵 Thanh khoản & Vốn")
ws5.sheet_view.showGridLines = False

ws5.merge_cells("A1:J1")
c = ws5["A1"]
c.value = f"  💵 THANH KHOẢN & VỐN  |  {bank['name']}  |  2023–2025"
c.font = FONT_TITLE; c.fill = FILL_TITLE; c.alignment = ALIGN_LEFT

liq_headers = ["Chỉ số", "2023", "2024", "2025", "Floor NHNN", "Trạng thái", "Xu hướng", "Rủi ro", "Hành động"]
for i, h in enumerate(liq_headers):
    c = ws5.cell(row=2, column=i+1, value=h)
    c.font = FONT_HEADER; c.fill = FILL_HEADER; c.alignment = ALIGN_CENTER; c.border = bold_border()

liq_items = [
    ("LCR (%)", [rat[y]["LCR"] for y in YEARS], 100, False,
     "Sát ngưỡng 100%", "↓ Giảm 17 điểm trong 2 năm",
     "Thiếu HQLA, phụ thuộc thị trường liên ngân hàng",
     "Phát hành kỳ phiếu 12 tháng"),
    ("NSFR (%)", [rat[y]["NSFR"] for y in YEARS], 100, False,
     "Trong phạm vi nhưng giảm dần", "↓ Giảm 6 điểm",
     "Cơ cấu nguồn vốn nghiêng ngắn hạn",
     "Tăng huy động dài hạn 18-24 tháng"),
    ("LDR (%)", [rat[y]["LDR"] for y in YEARS], 85, True,
     "⚠️ Vượt ngưỡng 80%", "↑ Tăng 5.4 điểm",
     "Cho vay tăng nhanh hơn huy động",
     "Giảm cho vay ngắn hạn DN"),
    ("CAR (%)", [rat[y]["CAR"] for y in YEARS], 8.0, False,
     "⚠️ Sát floor 8%", "↓ Giảm 1.5 điểm",
     "RWA tăng nhanh, lợi nhuận giữ lại thấp",
     "Phát hành Tier 2 + rights issue"),
    ("Tier 1 Ratio (%)", [rat[y]["Tier1_Ratio"] for y in YEARS], 6.0, False,
     "Sát ngưỡng", "↓ Giảm 1.4 điểm",
     "Phản ánh áp lực vốn cấp 1",
     "Tăng vốn cấp 1 từ lợi nhuận giữ lại"),
    ("Tăng trưởng RWA (%)", None, None, False,
     "Tăng nhanh", "↑ RWA tăng trung bình 14%/năm",
     "Mở rộng tín dụng tổng tài sản rủi ro cao",
     "Tối ưu hóa RWA, chuyển sang tài sản rủi ro thấp"),
]

status_fills = [(lambda v, fl, iu: hex_fill("FFCDD2") if (v < fl if not iu else v > fl) else (hex_fill("FFE0B2") if (v < fl*1.1 if not iu else v > fl*0.9) else hex_fill("C8E6C9"))) for _ in liq_items]

for i, item in enumerate(liq_items):
    r = 3 + i
    ws5.row_dimensions[r].height = 22
    label, vals, floor, is_upper, status_text, trend, risk, action = item

    c = ws5.cell(row=r, column=1, value=label)
    c.font = FONT_BOLD; c.fill = FILL_ALT if i % 2 == 0 else FILL_WHITE
    c.alignment = ALIGN_LEFT; c.border = thin_border()

    for j, yr in enumerate(YEARS):
        v = vals[j] if vals else 0
        col = 2 + j
        cv = ws5.cell(row=r, column=col, value=v)
        cv.number_format = "0.0%" if "%" in label else "#,##0"
        if "%" in label:
            cv.value = v / 100

        # Determine status color
        if floor and vals:
            is_bad = v/100 < floor if not is_upper else v/100 > floor
            is_warn = (v/100 < floor*1.1 if not is_upper else v/100 > floor*0.9) and not is_bad
            fill = FILL_RED if is_bad else (FILL_AMBER if is_warn else FILL_GREEN)
            font = FONT_RED if is_bad else (FONT_AMBER if is_warn else FONT_GREEN)
        else:
            fill = FILL_ALT if i % 2 == 0 else FILL_WHITE
            font = FONT_NORMAL
        cv.fill = fill; cv.font = font
        cv.alignment = ALIGN_RIGHT; cv.border = thin_border()

    c = ws5.cell(row=r, column=5, value=floor / 100 if floor else None)
    c.number_format = "0.0%" if floor else ""
    c.font = Font(name="Calibri", size=9, italic=True, color="666666")
    c.fill = FILL_ALT if i % 2 == 0 else FILL_WHITE
    c.alignment = ALIGN_CENTER; c.border = thin_border()

    cv = vals[2] if vals else 0
    is_bad = cv/100 < floor if not is_upper else cv/100 > floor
    is_warn = (cv/100 < floor*1.1 if not is_upper else cv/100 > floor*0.9) and not is_bad
    st_fill = FILL_RED if is_bad else (FILL_AMBER if is_warn else FILL_GREEN)
    st_font = FONT_RED if is_bad else (FONT_AMBER if is_warn else FONT_GREEN)

    for col_idx, text in enumerate([status_text, trend, risk, action]):
        col = 6 + col_idx
        c = ws5.cell(row=r, column=col, value=text)
        c.font = Font(name="Calibri", size=9, color="C62828" if "⚠" in text else ("333333" if col_idx < 3 else "1a237e"))
        c.fill = st_fill if col_idx < 3 else (FILL_ALT if i % 2 == 0 else FILL_WHITE)
        c.alignment = ALIGN_LEFT; c.border = thin_border()

# Cash flow section
r_cf = 3 + len(liq_items) + 2
ws5.merge_cells(f"A{r_cf}:J{r_cf}")
c = ws5[f"A{r_cf}"]
c.value = "  💰 LƯU CHUYỂN TIỀN TỆ"
c.font = FONT_HEADER; c.fill = hex_fill("37474F"); c.alignment = ALIGN_LEFT

cf_headers = ["Hoạt động", "2023", "2024", "2025"]
for i, h in enumerate(cf_headers):
    c = ws5.cell(row=r_cf+1, column=i+1, value=h)
    c.font = FONT_HEADER; c.fill = hex_fill("455A64"); c.alignment = ALIGN_CENTER; c.border = bold_border()

cf_items = [
    ("Operating CF", [cf[y]["operating_cf"] for y in YEARS], "Tiền từ hoạt động kinh doanh cốt lõi"),
    ("Investing CF", [cf[y]["investing_cf"] for y in YEARS], "Tiền cho đầu tư tài sản"),
    ("Financing CF", [cf[y]["financing_cf"] for y in YEARS], "Tiền từ huy động vốn, trả nợ, cổ tức"),
    ("Net Cash Change", [cf[y]["net_cash_change"] for y in YEARS], "Thay đổi tiền ròng"),
]

for i, (label, vals, desc) in enumerate(cf_items):
    r = r_cf + 2 + i
    ws5.row_dimensions[r].height = 18
    is_total = "Net" in label
    c = ws5.cell(row=r, column=1, value=f"{label} — {desc}")
    c.font = Font(name="Calibri", size=10, bold=is_total)
    c.fill = hex_fill("EEF2FF") if is_total else (FILL_ALT if i % 2 == 0 else FILL_WHITE)
    c.alignment = ALIGN_LEFT; c.border = thin_border()

    for j, v in enumerate(vals):
        cv = ws5.cell(row=r, column=2+j, value=v)
        cv.number_format = "#,##0"
        cv.font = Font(name="Calibri", size=10, bold=is_total,
                       color="2E7D32" if v > 0 else "C62828")
        cv.fill = hex_fill("EEF2FF") if is_total else (FILL_ALT if i % 2 == 0 else FILL_WHITE)
        cv.alignment = ALIGN_RIGHT; cv.border = thin_border()

# Off-balance
r_obs = r_cf + 2 + len(cf_items) + 2
ws5.merge_cells(f"A{r_obs}:J{r_obs}")
c = ws5[f"A{r_obs}"]
c.value = "  📋 CAM KẾT NGOẠI BẢNG"
c.font = FONT_HEADER; c.fill = hex_fill("37474F"); c.alignment = ALIGN_LEFT

obs_data = [
    ("Cam kết ngoại bảng (Tỷ VND)", [bs[y]["off_balance_sheet_commitments"] for y in YEARS]),
]
for i, (label, vals) in enumerate(obs_data):
    r = r_obs + 1 + i
    c = ws5.cell(row=r, column=1, value=label)
    c.font = FONT_BOLD; c.fill = FILL_ALT; c.alignment = ALIGN_LEFT; c.border = thin_border()
    for j, v in enumerate(vals):
        cv = ws5.cell(row=r, column=2+j, value=v)
        cv.number_format = "#,##0"; cv.font = FONT_NORMAL
        cv.fill = FILL_ALT; cv.alignment = ALIGN_RIGHT; cv.border = thin_border()

set_col_widths(ws5, {"A": 38, "B": 13, "C": 13, "D": 13, "E": 12, "F": 22, "G": 25, "H": 35, "I": 30, "J": 30})


# ═══════════════════════════════════════════════════════════════════════════════
# SHEET 6 — Điểm Yếu & Rủi ro
# ═══════════════════════════════════════════════════════════════════════════════
ws6 = wb.create_sheet("⚠️ Điểm Yếu & Rủi ro")
ws6.sheet_view.showGridLines = False

ws6.merge_cells("A1:I1")
c = ws6["A1"]
c.value = f"  ⚠️ ĐIỂM YẾU CỐT LÕI & MA TRẬN RỦI RO  |  {bank['name']}  |  Q4/2025"
c.font = FONT_TITLE; c.fill = hex_fill("B71C1C"); c.alignment = ALIGN_LEFT

# Matrix header
ws6.row_dimensions[2].height = 22
ws6.merge_cells("A3:I3")
c = ws6["A3"]
c.value = "  MA TRẬN RỦI RO × TÁC ĐỘNG"
c.font = FONT_HEADER; c.fill = hex_fill("37474F"); c.alignment = ALIGN_LEFT

r = 4
ws6.cell(row=r, column=1, value="").fill = hex_fill("ECEFF1"); ws6.cell(row=r, column=1).border = bold_border()
c = ws6.cell(row=r, column=2, value="Tác động thấp")
c.font = FONT_HEADER; c.fill = hex_fill("455A64"); c.alignment = ALIGN_CENTER; c.border = bold_border()
ws6.merge_cells(f"C{r}:E{r}")
c = ws6.cell(row=r, column=3, value="Tác động TRUNG BÌNH")
c.font = FONT_HEADER; c.fill = hex_fill("455A64"); c.alignment = ALIGN_CENTER; c.border = bold_border()
ws6.merge_cells(f"F{r}:I{r}")
c = ws6.cell(row=r, column=6, value="Tác động CAO")
c.font = FONT_HEADER; c.fill = hex_fill("C62828"); c.alignment = ALIGN_CENTER; c.border = bold_border()

ws6.cell(row=3, column=1, value="Rủi ro thấp").font = FONT_HEADER
ws6.cell(row=3, column=1).fill = hex_fill("455A64"); ws6.cell(row=3, column=1).alignment = ALIGN_CENTER

# Severity colors
sev_colors = {"CRITICAL": "FFCDD2", "HIGH": "FFE0B2", "MEDIUM": "FFF9C4"}
sev_text = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡"}

for i, wk in enumerate(wks):
    r = 5 + i
    ws6.row_dimensions[r].height = 28
    sev = wk["severity"]

    ws6.cell(row=r, column=1, value=wk["id"]).font = FONT_BOLD
    ws6.cell(row=r, column=1).fill = hex_fill(sev_colors.get(sev, "EEEEEE"))
    ws6.cell(row=r, column=1).alignment = ALIGN_CENTER; ws6.cell(row=r, column=1).border = thin_border()

    ws6.merge_cells(f"B{r}:I{r}")
    c = ws6.cell(row=r, column=2, value=f"{sev_text.get(sev,'🔵')} {wk['title']}  |  📊 {', '.join(wk['metrics'][:2])}")
    c.font = Font(name="Calibri", size=11, bold=True)
    c.fill = hex_fill(sev_colors.get(sev, "EEEEEE"))
    c.alignment = ALIGN_LEFT; c.border = thin_border()

# Detailed weakness table
r_detail = 5 + len(wks) + 2
ws6.merge_cells(f"A{r_detail}:I{r_detail}")
c = ws6[f"A{r_detail}"]
c.value = "  CHI TIẾT ĐIỂM YẾU — ROOT CAUSE ANALYSIS"
c.font = FONT_HEADER; c.fill = FILL_HEADER; c.alignment = ALIGN_LEFT

detail_headers = ["ID", "Điểm yếu", "Mức độ", "Dấu hiệu", "Root Cause (5-Why)", "Giải pháp chiến lược", "Giải pháp chính sách", "Giải pháp vận hành", "Quick Win"]
for i, h in enumerate(detail_headers):
    c = ws6.cell(row=r_detail+1, column=i+1, value=h)
    c.font = FONT_HEADER; c.fill = hex_fill("3949AB"); c.alignment = ALIGN_CENTER; c.border = bold_border()

for i, wk in enumerate(wks):
    r = r_detail + 2 + i
    ws6.row_dimensions[r].height = 80
    sev = wk["severity"]
    row_fill = hex_fill(sev_colors.get(sev, "EEEEEE"))

    for col, val, font, fill in [
        (1, wk["id"], FONT_BOLD, row_fill),
        (2, wk["title"], FONT_BOLD, row_fill),
        (3, sev, Font(name="Calibri", size=10, bold=True, color="C62828"), row_fill),
        (4, "\n".join(wk["metrics"]), Font(name="Calibri", size=9), FILL_WHITE),
        (5, wk["root_cause"], Font(name="Calibri", size=9, italic=True), hex_fill("FFF3E0")),
        (6, wk["strategic"], Font(name="Calibri", size=9), FILL_WHITE),
        (7, wk["policy"], Font(name="Calibri", size=9), FILL_WHITE),
        (8, wk["operational"], Font(name="Calibri", size=9), FILL_WHITE),
        (9, wk["quick_win"], Font(name="Calibri", size=9, bold=True, color="1a237e"), hex_fill("E8EAF6")),
    ]:
        c = ws6.cell(row=r, column=col, value=val)
        c.font = font; c.fill = fill
        c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        c.border = thin_border()

set_col_widths(ws6, {"A": 8, "B": 30, "C": 12, "D": 28, "E": 45, "F": 30, "G": 30, "H": 30, "I": 30})


# ═══════════════════════════════════════════════════════════════════════════════
# SHEET 7 — Root Cause Analysis
# ═══════════════════════════════════════════════════════════════════════════════
ws7 = wb.create_sheet("🔍 Root Cause Analysis")
ws7.sheet_view.showGridLines = False

ws7.merge_cells("A1:H1")
c = ws7["A1"]
c.value = f"  🔍 ROOT CAUSE ANALYSIS  |  {bank['name']}  |  Q4/2025"
c.font = FONT_TITLE; c.fill = FILL_TITLE; c.alignment = ALIGN_LEFT

# Themes
r = 3
ws7.merge_cells(f"A{r}:H{r}")
c = ws7[f"A{r}"]
c.value = "  🎯 CÁC NGuyên nhân GỐC RỄ CHÍNH (Cross-cutting Themes)"
c.font = FONT_HEADER; c.fill = hex_fill("37474F"); c.alignment = ALIGN_LEFT

rc_headers = ["Chủ đề", "Điểm yếu liên quan", "Mô tả vấn đề", "Giải pháp đề xuất"]
for i, h in enumerate(rc_headers):
    c = ws7.cell(row=r+1, column=i+1, value=h)
    c.font = FONT_HEADER; c.fill = hex_fill("455A64"); c.alignment = ALIGN_CENTER; c.border = bold_border()

for i, rc in enumerate(rc_sum):
    r = r + 2 + i
    ws7.row_dimensions[r].height = 60
    for col, val, fill, font in [
        (1, rc["theme"], hex_fill("E8EAF6"), Font(name="Calibri", size=11, bold=True)),
        (2, ", ".join(rc["affected_weaknesses"]), FILL_AMBER, Font(name="Calibri", size=10, bold=True, color="E65100")),
        (3, rc["description"], FILL_WHITE, Font(name="Calibri", size=10)),
        (4, rc["fix"], hex_fill("E8F5E9"), Font(name="Calibri", size=10, bold=True, color="2E7D32")),
    ]:
        c = ws7.cell(row=r, column=col, value=val)
        c.font = font; c.fill = fill
        c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        c.border = thin_border()

# 5-Why chains for each weakness
r = r + 3
ws7.merge_cells(f"A{r}:H{r}")
c = ws7[f"A{r}"]
c.value = "  🔄 CHUỖI 5-WHY CHO TỪNG ĐIỂM YẾU"
c.font = FONT_HEADER; c.fill = FILL_HEADER; c.alignment = ALIGN_LEFT

why5_data = [
    ("W001 — NPL Ratio cao", [
        "Why 1: Tại sao NPL tăng?", "Khách hàng không trả được nợ do suy thoái ngành BĐS & XNK",
        "Why 2: Tại sao ngành suy thoái?", "Biến động tỷ giá, lãi suất tăng, cầu nội địa yếu",
        "Why 3: Tại sao bank vẫn cho vay ngành này?", "Phân tích ngành yếu, phụ thuộc tài sản đảm bảo (collateral-based lending)",
        "Why 4: Tại sao phân tích ngành yếu?", "Hệ thống rating nội bộ chưa tinh vi, áp lực KPI tăng trưởng dư nợ",
        "Why 5: Tại sao KPI thiên lệch?", "Mô hình đánh giá hiệu suất chỉ trọng tăng trưởng, chưa có RAROC",
    ], "C62828"),
    ("W002 — CAR sát ngưỡng", [
        "Why 1: Tại sao CAR giảm?", "RWA tăng nhanh hơn vốn tự có",
        "Why 2: Tại sao RWA tăng nhanh?", "Tăng trưởng tín dụng 12.3%/năm, chuyển sang tài sản rủi ro cao",
        "Why 3: Tại sao cho vay rủi ro cao?", "Lợi nhuận ngắn hạn, KPI thiên lệch về tăng trưởng",
        "Why 4: Tại sao lợi nhuận giữ lại thấp?", "Lợi nhuận 2025 về sát 0, cổ tức trả bằng tiền mặt cao 2023-2024",
        "Why 5: Tại sao lợi nhuận thấp?", "Chi phí vốn tăng, NIM giảm, chi phí trích lập tăng vọt",
    ], "E65100"),
    ("W003 — Lợi nhuận suy giảm", [
        "Why 1: Tại sao lợi nhuận về sát 0?", "Chi phí hoạt động + dự phòng tăng vượt thu nhập",
        "Why 2: Tại sao chi phí tăng nhanh?", "Chi phí vốn tăng do cạnh tranh huy động, chi phí nhân sự + IT tăng",
        "Why 3: Tại sao chi phí vốn tăng?", "Phụ thuộc tiền gửi ngắn hạn, lãi suất huy động tăng theo thị trường",
        "Why 4: Tại sao phụ thuộc ngắn hạn?", "Chiến lược huy động thiên về chi phí thấp ngắn hạn, chưa quan tâm ALM",
        "Why 5: Tại sao chưa có ALM chặt?", "Hệ thống Treasury chưa đủ tinh vi, áp lực biên lãi ngắn hạn",
    ], "F57F17"),
    ("W004 — LCR giảm sát floor", [
        "Why 1: Tại sao LCR giảm?", "HQLA giảm tương đối, Net Cash Outflows tăng",
        "Why 2: Tại sao HQLA giảm?", "Tăng trưởng tín dụng dùng vốn, ít dư HQLA buffer",
        "Why 3: Tại sao outflows tăng?", "Tiền gửi ngắn hạn chiếm 65%, cam kết rút tiền cao",
        "Why 4: Tại sao huy động ngắn hạn nhiều?", "Chi phí huy động ngắn hạn rẻ hơn trong ngắn hạn",
        "Why 5: Tại sao không quan tâm ALM dài hạn?", "Mô hình kinh doanh ưu tiên biên lãi ngắn hạn, thiếu stress test thanh khoản",
    ], "F9A825"),
]

why_row = r + 1
for wk_id, whys, hdr_color in why5_data:
    ws7.merge_cells(f"A{why_row}:H{why_row}")
    c = ws7[f"A{why_row}"]
    c.value = f"  {wk_id}"
    c.font = FONT_HEADER; c.fill = hex_fill(hdr_color); c.alignment = ALIGN_LEFT

    for j, why_text in enumerate(whys):
        wr = why_row + 1 + j
        ws7.row_dimensions[wr].height = 24
        is_root = j == len(whys) - 1
        c = ws7.cell(row=wr, column=1, value=why_text.split(":")[0] if ":" in why_text else "")
        c.font = Font(name="Calibri", size=10, bold=is_root)
        c.fill = hex_fill("FFCDD2") if is_root else (FILL_ALT if j % 2 == 0 else FILL_WHITE)
        c.alignment = ALIGN_CENTER; c.border = thin_border()

        ws7.merge_cells(f"B{wr}:H{wr}")
        c = ws7.cell(row=wr, column=2, value=why_text.split(":", 1)[1].strip() if ":" in why_text else why_text)
        c.font = Font(name="Calibri", size=10, bold=is_root, color="C62828" if is_root else "333333")
        c.fill = hex_fill("FFCDD2") if is_root else (FILL_ALT if j % 2 == 0 else FILL_WHITE)
        c.alignment = ALIGN_LEFT; c.border = thin_border()

    why_row += len(whys) + 2

set_col_widths(ws7, {"A": 22, "B": 40, "C": 40, "D": 40, "E": 40, "F": 40, "G": 40, "H": 40})


# ═══════════════════════════════════════════════════════════════════════════════
# SHEET 8 — Giải pháp
# ═══════════════════════════════════════════════════════════════════════════════
ws8 = wb.create_sheet("💡 Giải pháp")
ws8.sheet_view.showGridLines = False

ws8.merge_cells("A1:G1")
c = ws8["A1"]
c.value = f"  💡 GIẢI PHÁP TỪ TỔNG QUÁT ĐẾN CHI TIẾT  |  {bank['name']}  |  Q4/2025"
c.font = FONT_TITLE; c.fill = FILL_TITLE; c.alignment = ALIGN_LEFT

sol_headers = ["Điểm yếu", "Cấp độ", "Hành động", "Mức ưu tiên", "Thời hạn", "Người phụ trách", "KPI đo lường"]
for i, h in enumerate(sol_headers):
    c = ws8.cell(row=2, column=i+1, value=h)
    c.font = FONT_HEADER; c.fill = FILL_HEADER; c.alignment = ALIGN_CENTER; c.border = bold_border()

level_colors = {
    "Chiến lược": ("1a237e", "FFFFFF"),
    "Chính sách": ("1565C0", "FFFFFF"),
    "Vận hành": ("2E7D32", "FFFFFF"),
    "Giám sát": ("6A1B9A", "FFFFFF"),
}
level_priority = {"Chiến lược": "🔴 Cao", "Chính sách": "🔴 Cao", "Vận hành": "🟠 Trung bình", "Giám sát": "🟡 Thấp"}
timeline_map = {"Chiến lược": "12-24 tháng", "Chính sách": "3-6 tháng", "Vận hành": "1-3 tháng", "Giám sát": "Ngay lập tức"}

all_solutions = []
for wk in wks:
    for level, actions in [("Chiến lược", [wk["strategic"]]),
                           ("Chính sách", [wk["policy"]]),
                           ("Vận hành", [wk["operational"]]),
                           ("Giám sát", [wk["quick_win"]])]:
        for action in actions:
            all_solutions.append((wk["title"], level, action))

for i, (wk_title, level, action) in enumerate(all_solutions):
    r = 3 + i
    ws8.row_dimensions[r].height = 30
    lc = level_colors.get(level, ("666666", "FFFFFF"))

    c = ws8.cell(row=r, column=1, value=wk_title)
    c.font = Font(name="Calibri", size=9, bold=True)
    c.fill = FILL_ALT if i % 2 == 0 else FILL_WHITE
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    c.border = thin_border()

    c = ws8.cell(row=r, column=2, value=level)
    c.font = Font(name="Calibri", size=9, bold=True, color=lc[1])
    c.fill = hex_fill(lc[0]); c.alignment = ALIGN_CENTER; c.border = thin_border()

    c = ws8.cell(row=r, column=3, value=action)
    c.font = Font(name="Calibri", size=9)
    c.fill = FILL_ALT if i % 2 == 0 else FILL_WHITE
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    c.border = thin_border()

    for col, val, fill, font in [
        (4, level_priority.get(level, "🟡 Thấp"), FILL_AMBER, FONT_AMBER),
        (5, timeline_map.get(level, "—"), FILL_ALT if i % 2 == 0 else FILL_WHITE, FONT_NORMAL),
        (6, "Ban Điều hành" if level == "Chiến lược" else ("Phòng QTRR" if level == "Chính sách" else ("Phòng Tín dụng" if level == "Vận hành" else "Tất cả")) , FILL_ALT if i % 2 == 0 else FILL_WHITE, FONT_NORMAL),
        (7, "NPL < 3.5%" if "NPL" in wk_title else ("CAR > 12%" if "CAR" in wk_title else ("NIM > 3.2%" if "NIM" in wk_title else ("LCR > 115%" if "LCR" in wk_title else ("Cost/Income < 48%")))), FILL_ALT if i % 2 == 0 else FILL_WHITE, Font(name="Calibri", size=9, bold=True, color="1a237e")),
    ]:
        c = ws8.cell(row=r, column=col, value=val)
        c.font = font; c.fill = fill
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = thin_border()

# Summary dashboard
r_summary = 3 + len(all_solutions) + 2
ws8.merge_cells(f"A{r_summary}:G{r_summary}")
c = ws8[f"A{r_summary}"]
c.value = "  📋 TÓM TẮT GIẢI PHÁP THEO CẤP ĐỘ"
c.font = FONT_HEADER; c.fill = hex_fill("37474F"); c.alignment = ALIGN_LEFT

summary_data = [
    ("Chiến lược", len([s for s in all_solutions if s[1] == "Chiến lược"]), "Tái cơ cấu dài hạn", "Ban Lãnh đạo", "12-24 tháng", "1a237e"),
    ("Chính sách", len([s for s in all_solutions if s[1] == "Chính sách"]), "Sửa đổi quy chế, giới hạn rủi ro", "Phòng QTRR + Ban Lãnh đạo", "3-6 tháng", "1565c0"),
    ("Vận hành", len([s for s in all_solutions if s[1] == "Vận hành"]), "Cải tiến quy trình, hệ thống", "Phòng Tín dụng + IT", "1-3 tháng", "2E7D32"),
    ("Giám sát", len([s for s in all_solutions if s[1] == "Giám sát"]), "Dashboard, alerts, báo cáo", "Tất cả phòng ban", "Ngay lập tức", "6A1B9A"),
]

for i, (level, count, desc, owner, timeline, color) in enumerate(summary_data):
    r = r_summary + 1 + i
    ws8.row_dimensions[r].height = 22
    for col, val, fill, font in [
        (1, f"{level} ({count} hành động)", hex_fill(color), Font(name="Calibri", size=11, bold=True, color="FFFFFF")),
        (2, desc, FILL_ALT if i % 2 == 0 else FILL_WHITE, FONT_NORMAL),
        (3, owner, FILL_ALT if i % 2 == 0 else FILL_WHITE, FONT_NORMAL),
        (4, timeline, FILL_ALT if i % 2 == 0 else FILL_WHITE, Font(name="Calibri", size=10, bold=True, color=color)),
        (5, "—", FILL_ALT if i % 2 == 0 else FILL_WHITE, FONT_NORMAL),
        (6, "—", FILL_ALT if i % 2 == 0 else FILL_WHITE, FONT_NORMAL),
        (7, "—", FILL_ALT if i % 2 == 0 else FILL_WHITE, FONT_NORMAL),
    ]:
        c = ws8.cell(row=r, column=col, value=val)
        c.font = font; c.fill = fill
        c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        c.border = thin_border()

set_col_widths(ws8, {"A": 32, "B": 14, "C": 50, "D": 14, "E": 16, "F": 20, "G": 20})


# ═══════════════════════════════════════════════════════════════════════════════
# SHEET 9 — Phân quyền Dashboard
# ═══════════════════════════════════════════════════════════════════════════════
ws9 = wb.create_sheet("👥 Phân quyền")
ws9.sheet_view.showGridLines = False

ws9.merge_cells("A1:J1")
c = ws9["A1"]
c.value = f"  👥 PHÂN QUYỀN DASHBOARD  |  {bank['name']}  |  RBAC Configuration"
c.font = FONT_TITLE; c.fill = FILL_TITLE; c.alignment = ALIGN_LEFT

perm_headers = ["Vai trò", "Mã", "Xem toàn bộ", "Cập nhật số liệu", "Chỉnh sửa", "Export", "Quản lý user", "Bình luận", "Phạm vi dữ liệu", "Ghi chú"]
for i, h in enumerate(perm_headers):
    c = ws9.cell(row=2, column=i+1, value=h)
    c.font = FONT_HEADER; c.fill = FILL_HEADER; c.alignment = ALIGN_CENTER; c.border = bold_border()

role_colors = {
    "executive": ("1a237e", "FFFFFF"),
    "finance": ("1565c0", "FFFFFF"),
    "risk": ("c62828", "FFFFFF"),
    "audit": ("6a1b9a", "FFFFFF"),
    "accounting": ("2e7d32", "FFFFFF"),
    "credit": ("e65100", "FFFFFF"),
    "marketing": ("00838f", "FFFFFF"),
    "branch": ("455a64", "FFFFFF"),
}

roles_order = ["executive", "finance", "risk", "audit", "accounting", "credit", "marketing", "branch"]

perm_matrix = [
    ("executive", "Ban Lãnh đạo", True, True, True, True, True, True, "Toàn bộ", "Full access — Admin"),
    ("finance", "Phòng Tài chính", True, True, True, True, False, True, "Toàn bộ", "Cập nhật Bảng CDKT, KQKD"),
    ("risk", "Phòng QTRR", True, True, True, True, False, True, "Toàn bộ", "Cập nhật NPL, CAR, LCR"),
    ("audit", "Phòng Kiểm toán Nội bộ", True, False, False, True, False, True, "Toàn bộ", "Read-only + export"),
    ("accounting", "Phòng Kế toán", False, True, False, True, False, False, "Bảng CDKT, KQKD", "Chỉ cập nhật phần mình"),
    ("credit", "Phòng Tín dụng", False, True, False, True, False, False, "Chất lượng TS, NPL", "Chỉ cập nhật phần mình"),
    ("marketing", "Phòng KH & Marketing", False, False, False, False, False, False, "Dashboard tổng hợp", "Read-only, không export"),
    ("branch", "Chi nhánh", False, False, False, False, False, False, "Dashboard chi nhánh", "Chỉ xem dữ liệu chi nhánh mình"),
]

for i, (role_key, role_name, view_all, update, edit, export, manage, comment, scope, note) in enumerate(perm_matrix):
    r = 3 + i
    ws9.row_dimensions[r].height = 24
    rc = role_colors.get(role_key, ("666666", "FFFFFF"))

    for col, val, fill, font in [
        (1, role_name, hex_fill(rc[0]), Font(name="Calibri", size=10, bold=True, color=rc[1])),
        (2, role_key, hex_fill(rc[0]), Font(name="Calibri", size=9, color=rc[1])),
        (3, "✅" if view_all else "❌", FILL_GREEN if view_all else FILL_RED, Font(name="Calibri", size=12, bold=True)),
        (4, "✅" if update else "❌", FILL_GREEN if update else FILL_RED, Font(name="Calibri", size=12, bold=True)),
        (5, "✅" if edit else "❌", FILL_GREEN if edit else FILL_RED, Font(name="Calibri", size=12, bold=True)),
        (6, "✅" if export else "❌", FILL_GREEN if export else FILL_RED, Font(name="Calibri", size=12, bold=True)),
        (7, "✅" if manage else "❌", FILL_GREEN if manage else FILL_RED, Font(name="Calibri", size=12, bold=True)),
        (8, "✅" if comment else "❌", FILL_GREEN if comment else FILL_RED, Font(name="Calibri", size=12, bold=True)),
        (9, scope, FILL_ALT if i % 2 == 0 else FILL_WHITE, Font(name="Calibri", size=9, italic=True)),
        (10, note, FILL_ALT if i % 2 == 0 else FILL_WHITE, Font(name="Calibri", size=9)),
    ]:
        c = ws9.cell(row=r, column=col, value=val)
        c.font = font; c.fill = fill
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = thin_border()

# Audit trail note
r_note = 3 + len(perm_matrix) + 2
ws9.merge_cells(f"A{r_note}:J{r_note}")
c = ws9[f"A{r_note}"]
c.value = "  📋 GHI CHÚ VỀ PHÂN QUYỀN"
c.font = FONT_HEADER; c.fill = hex_fill("37474F"); c.alignment = ALIGN_LEFT

notes = [
    "1. Audit Trail: Tất cả hành động xem, cập nhật, chỉnh sửa đều được ghi log. Lưu trữ 365 ngày.",
    "2. Row-Level Security: Chi nhánh chỉ xem dữ liệu chi nhánh mình. Phòng ban chỉ xem dữ liệu phòng mình (trừ Executive/Risk/Audit).",
    "3. Data Classification: Bảng CDKT, KQKD → Restricted (Tài chính + Lãnh đạo). NPL, CAR, LCR → Confidential (QTRR + Lãnh đạo). Dashboard tổng hợp → Internal (Tất cả).",
    "4. Để thêm người dùng: Thêm vào sheet 'Users' với cấu trúc: [Họ tên] | [Phòng ban] | [Vai trò] | [Ngày gán] | [Người gán] | [Trạng thái]",
    "5. Phê duyệt thay đổi quyền: Cần xác nhận từ Trưởng phòng HC-NS và Ban Lãnh đạo. Ghi log lý do thay đổi.",
]
for i, note in enumerate(notes):
    r = r_note + 1 + i
    ws9.row_dimensions[r].height = 20
    c = ws9.cell(row=r, column=1, value=note)
    c.font = Font(name="Calibri", size=9)
    c.fill = FILL_ALT if i % 2 == 0 else FILL_WHITE
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ws9.merge_cells(f"A{r}:J{r}")
    c.border = thin_border()

set_col_widths(ws9, {"A": 22, "B": 12, "C": 12, "D": 14, "E": 12, "F": 10, "G": 12, "H": 12, "I": 22, "J": 30})

# ─── Save ────────────────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "../output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"VDB_Financial_Analysis_{bank['report_quarter']}_{bank['report_year']}.xlsx")
wb.save(OUTPUT_FILE)
print(f"✅ Excel dashboard saved: {OUTPUT_FILE}")

#!/usr/bin/env python3
"""
BANKING FINANCIAL ANALYSIS — Landing Page HTML
Ngân hàng TMCP Phát triển Việt Nam (VDB)
"""

import json, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "../data/banking_mockdata.json")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

bank = data["bank_info"]
bench = data["benchmark"]
rat = data["ratios"]
wks = data["weaknesses"]
cam = data["camels"]
perm = data["permissions"]

YEARS = ["2023", "2024", "2025"]
cam_total_2025 = sum(cam["2025"].values()) / 6

sev_colors = {"CRITICAL": "#C62828", "HIGH": "#E65100", "MEDIUM": "#F9A825"}
sev_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡"}

def sc(v, warn, danger, is_upper=False):
    if is_upper:
        return "#C62828" if v > danger else ("#E65100" if v > warn else "#2E7D32")
    return "#C62828" if v < danger else ("#E65100" if v < warn else "#2E7D32")

def st(v, warn, danger, is_upper=False):
    if is_upper:
        return "🔴 Nguy hiểm" if v > danger else ("🟡 Cảnh báo" if v > warn else "🟢 Tốt")
    return "🔴 Nguy hiểm" if v < danger else ("🟡 Cảnh báo" if v < warn else "🟢 Tốt")

def bg_fill(v, warn, danger, is_upper=False):
    color = sc(v, warn, danger, is_upper)
    return "#FFEBEE" if color == "#C62828" else ("#FFF8E1" if color == "#E65100" else "#E8F5E9")

# ─── KPI data ─────────────────────────────────────────────────────────────────
kpis = [
    {"label": "CAR", "v23": rat["2023"]["CAR"], "v24": rat["2024"]["CAR"], "v25": rat["2025"]["CAR"],
     "floor": bench["CAR_minimum"], "warning": bench["CAR_warning"], "fmt": "0.0",
     "icon": "🏦", "is_upper": False},
    {"label": "NPL Ratio", "v23": rat["2023"]["NPL_Ratio"], "v24": rat["2024"]["NPL_Ratio"], "v25": rat["2025"]["NPL_Ratio"],
     "floor": bench["NPL_floor_warning"], "warning": bench["NPL_floor_danger"], "fmt": "0.0",
     "icon": "⚠️", "is_upper": True},
    {"label": "LCR", "v23": rat["2023"]["LCR"], "v24": rat["2024"]["LCR"], "v25": rat["2025"]["LCR"],
     "floor": bench["LCR_minimum"], "warning": bench["LCR_warning"], "fmt": "0",
     "icon": "💧", "is_upper": False},
    {"label": "NIM", "v23": rat["2023"]["NIM"], "v24": rat["2024"]["NIM"], "v25": rat["2025"]["NIM"],
     "floor": 3.0, "warning": 3.5, "fmt": "0.00",
     "icon": "📈", "is_upper": False},
    {"label": "ROE", "v23": rat["2023"]["ROE"], "v24": rat["2024"]["ROE"], "v25": rat["2025"]["ROE"],
     "floor": 5.0, "warning": bench["ROE_avg_industry"], "fmt": "0.0",
     "icon": "💰", "is_upper": False},
    {"label": "LDR", "v23": rat["2023"]["LDR"], "v24": rat["2024"]["LDR"], "v25": rat["2025"]["LDR"],
     "floor": bench["LDR_warning"], "warning": bench["LDR_maximum"], "fmt": "0.0",
     "icon": "📉", "is_upper": True},
]

# ─── Pre-compute all sections ─────────────────────────────────────────────────

# KPI Cards HTML
kpi_cards_html = ""
for k in kpis:
    color = sc(k["v25"], k["warning"], k["floor"], k["is_upper"])
    bfill = bg_fill(k["v25"], k["warning"], k["floor"], k["is_upper"])
    txt = st(k["v25"], k["warning"], k["floor"], k["is_upper"])
    fmt = k["fmt"]
    v25 = k["v25"]
    v23 = k["v23"]
    v24 = k["v24"]
    floor = k["floor"]
    warn = k["warning"]
    kpi_cards_html += f'''<div class="kpi-card">
  <div class="corner" style="border-width:40px 40px 0 0;border-color:{color} transparent transparent transparent;"></div>
  <div class="kpi-icon">{k["icon"]}</div>
  <div class="kpi-label">{k["label"]}</div>
  <div class="kpi-value" style="color:{color}">{v25:{fmt}}</div>
  <div class="kpi-trend" style="background:{bfill};color:{color}">{txt}</div>
  <div class="kpi-year">2023:{v23:{fmt}}&nbsp;|&nbsp;2024:{v24:{fmt}}</div>
  <div class="kpi-floor">Floor:{floor}&nbsp;|&nbsp;Warning:{warn}</div>
</div>'''

# Alert chips
critical_count = sum(1 for w in wks if w["severity"] == "CRITICAL")
high_count = sum(1 for w in wks if w["severity"] == "HIGH")
medium_count = sum(1 for w in wks if w["severity"] == "MEDIUM")
ok_count = sum(1 for k in kpis if sc(k["v25"], k["warning"], k["floor"], k["is_upper"]) == "#2E7D32")
alert_chips_html = (
    '<span class="alert-chip critical">🔴 Nghiêm trọng: ' + str(critical_count) + '</span>'
    '<span class="alert-chip high">🟠 Cao: ' + str(high_count) + '</span>'
    '<span class="alert-chip medium">🟡 Trung bình: ' + str(medium_count) + '</span>'
    '<span class="alert-chip ok">🟢 Tốt: ' + str(ok_count) + '/' + str(len(kpis)) + ' chỉ số</span>'
)

# Weakness cards (dashboard summary)
weakness_summary_html = ""
for w in wks:
    sev = w["severity"]
    color = sev_colors.get(sev, "#999")
    icon = sev_icon.get(sev, "🔵")
    metrics_html = "".join(
        f'<div class="metric-item"><span class="metric-label">{m.split(":",1)[0]}</span><span class="metric-value">{m.split(":",1)[1].strip() if ":" in m else m}</span></div>'
        for m in w["metrics"][:3]
    )
    weakness_summary_html += f'''<div class="weakness-card" style="border-left-color:{color}">
  <div class="weakness-header">
    <div>
      <div class="weakness-title">{icon} {w["id"]} — {w["title"]}</div>
      <div class="weakness-tags">
        <span class="tag {sev.lower()}">{sev}</span>
        <span class="tag rootcause">🔍 Root cause</span>
      </div>
    </div>
    <span class="tag {sev.lower()}">{sev}</span>
  </div>
  <div class="weakness-body">
    <div class="weakness-desc">{w["description"]}</div>
    <div class="weakness-metrics">{metrics_html}</div>
    <div class="solution-block quickwin">
      <div class="solution-label">⚡ Quick Win (30 ngày)</div>
      {w["quick_win"]}
    </div>
  </div>
</div>'''

# CAMELS mini grid
camels_mini_html = ""
for idx, letter in enumerate("CAMELS"):
    full_names = ["Capital", "Asset", "Management", "Earnings", "Liquidity", "Sensitivity"]
    name = full_names[idx]
    s = cam["2025"][letter]
    s23 = cam["2023"][letter]
    s24 = cam["2024"][letter]
    s_color = "#C62828" if s <= 2 else ("#E65100" if s <= 3 else "#2E7D32")
    trend_color = "#C62828" if s - s23 < 0 else "#2E7D32"
    trend_arrow = "↓" if s - s23 < 0 else "↑"
    camels_mini_html += f'''<div class="camels-card">
  <div class="letter" style="background:{s_color}">{letter}</div>
  <div class="name">{name}</div>
  <div class="score" style="color:{s_color}">{s}</div>
  <div class="trend" style="color:{trend_color}">{trend_arrow} {abs(s-s23):.1f} vs 2023</div>
  <div class="total">{s23} (2023) → {s24} (2024)</div>
</div>'''

# CAMELS table rows
camels_table_html = ""
for idx, letter in enumerate("CAMELS"):
    full_names = ["Capital Adequacy", "Asset Quality", "Management", "Earnings", "Liquidity", "Sensitivity"]
    weights = [0.20, 0.25, 0.15, 0.15, 0.15, 0.10]
    benchmarks = ["CAR ≥ 8% (floor)", "NPL < 3% (warning)", "Cost/Income < 45%", "ROE > 10%", "LCR ≥ 100%, LDR < 85%", "NIM > 3%"]
    indicators = ["CAR: " + str(rat["2023"]["CAR"]) + "% → " + str(rat["2025"]["CAR"]) + "%",
                 "NPL: " + str(rat["2023"]["NPL_Ratio"]) + "% → " + str(rat["2025"]["NPL_Ratio"]) + "%",
                 "Cost/Income: " + str(rat["2023"]["Cost_to_Income"]) + "% → " + str(rat["2025"]["Cost_to_Income"]) + "%",
                 "ROE: " + str(rat["2023"]["ROE"]) + "% → " + str(rat["2025"]["ROE"]) + "%",
                 "LCR: " + str(rat["2023"]["LCR"]) + " → " + str(rat["2025"]["LCR"]),
                 "NIM: " + str(rat["2023"]["NIM"]) + "% → " + str(rat["2025"]["NIM"]) + "%"]
    fn = full_names[idx]
    wgt = weights[idx]
    bm = benchmarks[idx]
    ind = indicators[idx]
    s23 = cam["2023"][letter]
    s24 = cam["2024"][letter]
    s25 = cam["2025"][letter]
    tag_class = "critical" if s25 <= 2 else ("high" if s25 <= 3 else ("medium" if s25 <= 4 else ""))
    tag_text = "Nguy hiểm" if s25 <= 2 else ("Cảnh báo" if s25 <= 3 else ("Trung bình" if s25 <= 4 else "Tốt"))
    s_color = "#C62828" if s25 <= 2 else ("#E65100" if s25 <= 3 else "#2E7D32")
    camels_table_html += f'''<tr>
  <td><strong>{letter}: {fn}</strong></td>
  <td class="center">{wgt*100:.0f}%</td>
  <td class="center" style="color:{"#C62828" if s23<=2 else "#E65100" if s23<=3 else "#2E7D32"};font-weight:700">{s23}</td>
  <td class="center" style="color:{"#C62828" if s24<=2 else "#E65100" if s24<=3 else "#2E7D32"};font-weight:700">{s24}</td>
  <td class="center" style="color:{s_color};font-weight:700;font-size:15px">{s25}</td>
  <td class="center" style="color:#C62828;font-weight:700">{s25-s23:+.1f}</td>
  <td class="center" style="font-size:11px;color:#666">{ind}</td>
  <td class="center" style="font-size:11px">{bm}</td>
  <td class="center"><span class="tag {tag_class}">{tag_text}</span></td>
</tr>'''

# Asset table rows
asset_rows_html = f'''<tr>
  <td>NPL Ratio (%)</td>
  <td class="num">{rat["2023"]["NPL_Ratio"]:.1f}</td>
  <td class="num">{rat["2024"]["NPL_Ratio"]:.1f}</td>
  <td class="num" style="color:#C62828;font-weight:700">{rat["2025"]["NPL_Ratio"]:.1f}</td>
  <td class="num">3.0%</td>
  <td><span class="tag critical">⚠️ Vượt ngưỡng</span></td>
</tr>
<tr>
  <td>NPL Coverage (%)</td>
  <td class="num">{rat["2023"]["NPL_Coverage"]:.1f}</td>
  <td class="num">{rat["2024"]["NPL_Coverage"]:.1f}</td>
  <td class="num" style="color:#E65100;font-weight:700">{rat["2025"]["NPL_Coverage"]:.1f}</td>
  <td class="num">80%</td>
  <td><span class="tag high">Dưới target</span></td>
</tr>
<tr>
  <td>Tăng trưởng dư nợ (%)</td>
  <td class="num">{rat["2023"]["Growth_Loans"]:.1f}</td>
  <td class="num">{rat["2024"]["Growth_Loans"]:.1f}</td>
  <td class="num" style="color:#1a237e;font-weight:700">{rat["2025"]["Growth_Loans"]:.1f}</td>
  <td class="num">—</td>
  <td><span class="tag strategic">Tăng nhanh</span></td>
</tr>
<tr>
  <td>Fee Income Ratio (%)</td>
  <td class="num">{rat["2023"]["Fee_Income_Ratio"]:.1f}</td>
  <td class="num">{rat["2024"]["Fee_Income_Ratio"]:.1f}</td>
  <td class="num" style="color:#2E7D32">{rat["2025"]["Fee_Income_Ratio"]:.1f}</td>
  <td class="num">—</td>
  <td><span class="tag strategic">Tăng tích cực</span></td>
</tr>'''

# Liquidity KPI cards
liq_kpi_cards = [
    ("LCR", rat["2025"]["LCR"], rat["2023"]["LCR"], rat["2024"]["LCR"], bench["LCR_minimum"], bench["LCR_warning"], False, "💧"),
    ("NSFR", rat["2025"]["NSFR"], rat["2023"]["NSFR"], rat["2024"]["NSFR"], bench["NSFR_minimum"], bench["NSFR_warning"], False, "🔄"),
    ("LDR", rat["2025"]["LDR"], rat["2023"]["LDR"], rat["2024"]["LDR"], bench["LDR_warning"], bench["LDR_maximum"], True, "📉"),
    ("CAR", rat["2025"]["CAR"], rat["2023"]["CAR"], rat["2024"]["CAR"], bench["CAR_warning"], bench["CAR_minimum"], False, "🏦"),
    ("Tier 1", rat["2025"]["Tier1_Ratio"], rat["2023"]["Tier1_Ratio"], rat["2024"]["Tier1_Ratio"], 9.0, 6.0, False, "📊"),
]
liq_kpi_html = ""
for label, v25, v23, v24, floor, warn, is_up, icon in liq_kpi_cards:
    color = sc(v25, warn, floor, is_up)
    bfill = bg_fill(v25, warn, floor, is_up)
    txt = st(v25, warn, floor, is_up)
    liq_kpi_html += f'''<div class="kpi-card">
  <div class="corner" style="border-width:40px 40px 0 0;border-color:{color} transparent transparent transparent;"></div>
  <div class="kpi-icon">{icon}</div>
  <div class="kpi-label">{label}</div>
  <div class="kpi-value" style="color:{color}">{v25}</div>
  <div class="kpi-trend" style="background:{bfill};color:{color}">{txt}</div>
  <div class="kpi-year">2023:{v23}&nbsp;|&nbsp;2024:{v24}&nbsp;|&nbsp;2025:{v25}</div>
  <div class="kpi-floor">Floor:{floor}&nbsp;|&nbsp;Warning:{warn}</div>
</div>'''

# Liquidity table rows
liq_rows_html = f'''<tr>
  <td>LCR (%)</td>
  <td class="num">{rat["2023"]["LCR"]}</td><td class="num">{rat["2024"]["LCR"]}</td>
  <td class="num" style="color:#C62828;font-weight:700">{rat["2025"]["LCR"]}</td>
  <td class="num">100</td>
  <td class="status-warn">↓ -17 điểm</td>
  <td style="font-size:12px">Sát ngưỡng, cảnh báo thanh khoản</td>
</tr>
<tr>
  <td>NSFR (%)</td>
  <td class="num">{rat["2023"]["NSFR"]}</td><td class="num">{rat["2024"]["NSFR"]}</td>
  <td class="num" style="color:#E65100;font-weight:700">{rat["2025"]["NSFR"]}</td>
  <td class="num">100</td>
  <td class="status-warn">↓ -6 điểm</td>
  <td style="font-size:12px">Cơ cấu nguồn vốn nghiêng ngắn hạn</td>
</tr>
<tr>
  <td>LDR (%)</td>
  <td class="num">{rat["2023"]["LDR"]:.1f}</td><td class="num">{rat["2024"]["LDR"]:.1f}</td>
  <td class="num" style="color:#C62828;font-weight:700">{rat["2025"]["LDR"]:.1f}</td>
  <td class="num">85</td>
  <td class="status-danger">↑ +5.4 điểm</td>
  <td style="font-size:12px">Vượt ngưỡng 80%, ALM bất cân xứng</td>
</tr>
<tr>
  <td>CAR (%)</td>
  <td class="num">{rat["2023"]["CAR"]:.1f}</td><td class="num">{rat["2024"]["CAR"]:.1f}</td>
  <td class="num" style="color:#E65100;font-weight:700">{rat["2025"]["CAR"]:.1f}</td>
  <td class="num">8.0</td>
  <td class="status-warn">↓ -1.5 điểm</td>
  <td style="font-size:12px">Khoảng cách an toàn chỉ 2.3 điểm</td>
</tr>'''

# Earnings table rows
inc = data["income_statement"]
earnings_rows_html = f'''<tr>
  <td>Thu nhập lãi thuần</td>
  <td class="num">{inc["2023"]["net_interest_income"]:,.0f}</td>
  <td class="num">{inc["2024"]["net_interest_income"]:,.0f}</td>
  <td class="num" style="font-weight:700">{inc["2025"]["net_interest_income"]:,.0f}</td>
  <td class="num" style="color:#2E7D32">{inc["2025"]["net_interest_income"]-inc["2024"]["net_interest_income"]:+,.0f}</td>
  <td style="font-size:11px">NIM: {rat["2023"]["NIM"]:.2f}% → {rat["2025"]["NIM"]:.2f}%</td>
</tr>
<tr>
  <td>Thu nhập phí</td>
  <td class="num">{inc["2023"]["fee_income"]:,.0f}</td>
  <td class="num">{inc["2024"]["fee_income"]:,.0f}</td>
  <td class="num">{inc["2025"]["fee_income"]:,.0f}</td>
  <td class="num" style="color:#2E7D32">{inc["2025"]["fee_income"]-inc["2024"]["fee_income"]:+,.0f}</td>
  <td style="font-size:11px">Tăng trưởng tích cực</td>
</tr>
<tr>
  <td>Tổng thu nhập</td>
  <td class="num">{inc["2023"]["total_income"]:,.0f}</td>
  <td class="num">{inc["2024"]["total_income"]:,.0f}</td>
  <td class="num">{inc["2025"]["total_income"]:,.0f}</td>
  <td class="num" style="color:#2E7D32">{inc["2025"]["total_income"]-inc["2024"]["total_income"]:+,.0f}</td>
  <td style="font-size:11px"></td>
</tr>
<tr>
  <td>Chi phí trích lập dự phòng</td>
  <td class="num">{inc["2023"]["credit_loss_expense"]:,.0f}</td>
  <td class="num">{inc["2024"]["credit_loss_expense"]:,.0f}</td>
  <td class="num" style="color:#C62828;font-weight:700">{inc["2025"]["credit_loss_expense"]:,.0f}</td>
  <td class="num" style="color:#C62828">{inc["2025"]["credit_loss_expense"]-inc["2024"]["credit_loss_expense"]:+,.0f}</td>
  <td style="font-size:11px">⚠️ Tăng 74% vs 2023</td>
</tr>
<tr>
  <td>Chi phí hoạt động</td>
  <td class="num">{inc["2023"]["total_operating_expense"]:,.0f}</td>
  <td class="num">{inc["2024"]["total_operating_expense"]:,.0f}</td>
  <td class="num" style="color:#C62828;font-weight:700">{inc["2025"]["total_operating_expense"]:,.0f}</td>
  <td class="num" style="color:#C62828">{inc["2025"]["total_operating_expense"]-inc["2024"]["total_operating_expense"]:+,.0f}</td>
  <td style="font-size:11px">⚠️ Cost/Income: {rat["2025"]["Cost_to_Income"]:.1f}%</td>
</tr>
<tr style="background:#FFEBEE;font-weight:700">
  <td>LỢI NHUẬN TRƯỚC THUẾ</td>
  <td class="num" style="color:#2E7D32">{inc["2023"]["profit_before_tax"]:,.0f}</td>
  <td class="num" style="color:#E65100">{inc["2024"]["profit_before_tax"]:,.0f}</td>
  <td class="num" style="color:#C62828">{inc["2025"]["profit_before_tax"]:,.0f}</td>
  <td class="num" style="color:#C62828">{inc["2025"]["profit_before_tax"]-inc["2024"]["profit_before_tax"]:+,.0f}</td>
  <td style="font-size:11px;color:#C62828">⚠️ Gần bằng 0</td>
</tr>
<tr style="background:#FFEBEE">
  <td>LỢI NHUẬN SAU THUẾ</td>
  <td class="num" style="color:#2E7D32;font-weight:700">{inc["2023"]["profit_after_tax"]:,.0f}</td>
  <td class="num" style="color:#E65100">{inc["2024"]["profit_after_tax"]:,.0f}</td>
  <td class="num" style="color:#C62828;font-weight:700">{inc["2025"]["profit_after_tax"]:,.0f}</td>
  <td class="num" style="color:#C62828">{inc["2025"]["profit_after_tax"]-inc["2024"]["profit_after_tax"]:+,.0f}</td>
  <td style="font-size:11px;color:#C62828">⚠️ Khủng hoảng thu nhập</td>
</tr>'''

# Detailed weakness cards
weakness_detail_html = ""
for w in wks:
    sev = w["severity"]
    color = sev_colors.get(sev, "#999")
    icon = sev_icon.get(sev, "🔵")
    metrics_html = "".join(
        f'<div class="metric-item"><span class="metric-label">📊 {m.split(":",1)[0]}</span><span class="metric-value">{m.split(":",1)[1].strip() if ":" in m else m}</span></div>'
        for m in w["metrics"]
    )
    weakness_detail_html += f'''<div class="weakness-card" style="border-left-color:{color};margin-bottom:20px">
  <div class="weakness-header">
    <div>
      <div class="weakness-title" style="font-size:15px">{icon} {w["id"]} — {w["title"]}</div>
      <div class="weakness-tags">
        <span class="tag {sev.lower()}">{sev}</span>
        <span class="tag rootcause">🔍 Root Cause Analysis</span>
        <span class="tag strategic">📋 {w["category"]}</span>
      </div>
    </div>
    <span class="tag {sev.lower()}" style="font-size:13px">{sev}</span>
  </div>
  <div class="weakness-body">
    <div class="weakness-desc" style="font-size:13px">{w["description"]}</div>
    <div class="weakness-metrics">{metrics_html}</div>
    <div style="background:#FFF3E0;border-radius:8px;padding:12px 14px;margin:10px 0;border-left:4px solid #E65100">
      <div style="font-size:11px;font-weight:700;text-transform:uppercase;margin-bottom:6px;opacity:0.7">🔍 Root Cause (5-Why)</div>
      <div style="font-size:12px;line-height:1.7">{w["root_cause"]}</div>
    </div>
    <div class="solution-block strategic">
      <div class="solution-label">🏛️ Giải pháp Chiến lược</div>
      {w["strategic"]}
    </div>
    <div class="solution-block policy">
      <div class="solution-label">📜 Giải pháp Chính sách</div>
      {w["policy"]}
    </div>
    <div class="solution-block ops">
      <div class="solution-label">⚙️ Giải pháp Vận hành</div>
      {w["operational"]}
    </div>
    <div class="solution-block quickwin">
      <div class="solution-label">⚡ Quick Win — Hành động ngay (30 ngày)</div>
      {w["quick_win"]}
    </div>
  </div>
</div>'''

# Permission matrix rows
roles_order = ["executive", "finance", "risk", "audit", "accounting", "credit", "marketing", "branch"]
perm_rows_html = ""
for rk in roles_order:
    rdata = perm["roles"][rk]
    view_ok = "✅" if rdata["can_view_all"] else "❌"
    upd_ok = "✅" if rdata["can_update"] else "❌"
    edit_ok = "✅" if rdata["can_edit"] else "❌"
    exp_ok = "✅" if rdata["can_export"] else "❌"
    mgmt_ok = "✅" if rdata["can_manage_users"] else "❌"
    cmt_ok = "✅" if rdata["can_comment"] else "❌"
    scope = "Toàn bộ" if rdata["can_view_all"] else (", ".join(rdata.get("view_sections", ["—"])) if isinstance(rdata.get("view_sections"), list) else rdata.get("view_sections", "—"))
    view_cls = "perm-yes" if rdata["can_view_all"] else "perm-no"
    upd_cls = "perm-yes" if rdata["can_update"] else "perm-no"
    edit_cls = "perm-yes" if rdata["can_edit"] else "perm-no"
    exp_cls = "perm-yes" if rdata["can_export"] else "perm-no"
    mgmt_cls = "perm-yes" if rdata["can_manage_users"] else "perm-no"
    cmt_cls = "perm-yes" if rdata["can_comment"] else "perm-no"
    perm_rows_html += f'''<tr>
  <td><span class="perm-role-badge" style="background:{rdata["color"]}">{rdata["label"]}</span></td>
  <td class="center"><span class="{view_cls}">{view_ok}</span></td>
  <td class="center"><span class="{upd_cls}">{upd_ok}</span></td>
  <td class="center"><span class="{edit_cls}">{edit_ok}</span></td>
  <td class="center"><span class="{exp_cls}">{exp_ok}</span></td>
  <td class="center"><span class="{mgmt_cls}">{mgmt_ok}</span></td>
  <td class="center"><span class="{cmt_cls}">{cmt_ok}</span></td>
  <td style="font-size:11px">{scope}</td>
</tr>'''

# ─── Build HTML ────────────────────────────────────────────────────────────────
camels_total_color = "#C62828" if cam_total_2025 < 2.1 else ("#E65100" if cam_total_2025 < 3.1 else "#2E7D32")
camels_badge_color = camels_total_color

html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Báo Cáo Tài Chính Chuyên Sâu — {bank["name"]}</title>
<style>
  * {{ margin:0;padding:0;box-sizing:border-box; }}
  body {{ font-family:'Segoe UI','Helvetica Neue',Arial,sans-serif; background:#F0F2F5; color:#1a1a2e; }}
  a {{ text-decoration:none; }}
  .header {{ background:linear-gradient(135deg,#1a237e 0%,#283593 60%,#1565C0 100%); color:white; position:sticky; top:0; z-index:100; box-shadow:0 2px 12px rgba(26,35,126,0.3); }}
  .header-top {{ display:flex; align-items:center; justify-content:space-between; padding:14px 24px; border-bottom:1px solid rgba(255,255,255,0.15); }}
  .header-title {{ display:flex; align-items:center; gap:12px; }}
  .header-title h1 {{ font-size:18px; font-weight:700; }}
  .header-title span {{ font-size:12px; opacity:0.8; }}
  .header-badges {{ display:flex; gap:8px; }}
  .badge {{ padding:4px 10px; border-radius:20px; font-size:11px; font-weight:600; background:rgba(255,255,255,0.15); border:1px solid rgba(255,255,255,0.3); }}
  .badge.danger {{ background:#C62828; border-color:#C62828; }}
  .badge.warning {{ background:#E65100; border-color:#E65100; }}
  .badge.ok {{ background:#2E7D32; border-color:#2E7D32; }}
  .header-meta {{ display:flex; gap:20px; padding:10px 24px; font-size:12px; opacity:0.85; flex-wrap:wrap; }}
  .header-meta span {{ display:flex; align-items:center; gap:5px; }}
  .tabs {{ display:flex; background:white; border-bottom:3px solid #E8EAF6; padding:0 24px; overflow-x:auto; }}
  .tab {{ padding:12px 20px; font-size:13px; font-weight:600; color:#5C6BC0; cursor:pointer; border-bottom:3px solid transparent; white-space:nowrap; transition:all 0.2s; display:flex; align-items:center; gap:6px; }}
  .tab:hover {{ color:#1a237e; background:#EEF2FF; }}
  .tab.active {{ color:#1a237e; border-bottom-color:#1a237e; background:#EEF2FF; }}
  .tab.admin-only {{ color:#999; }}
  .content {{ padding:24px; max-width:1400px; margin:0 auto; }}
  .tab-content {{ display:none; }}
  .tab-content.active {{ display:block; animation:fadeIn 0.3s; }}
  @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(8px); }} to {{ opacity:1; transform:translateY(0); }} }}
  .filter-bar {{ background:white; border-radius:10px; padding:14px 20px; margin-bottom:20px; display:flex; gap:12px; flex-wrap:wrap; align-items:center; box-shadow:0 1px 4px rgba(0,0,0,0.08); }}
  .filter-label {{ font-size:12px; color:#666; font-weight:600; text-transform:uppercase; }}
  select, input {{ padding:6px 12px; border:1.5px solid #E0E0E0; border-radius:6px; font-size:13px; background:white; }}
  select:focus {{ outline:none; border-color:#1a237e; }}
  .kpi-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:14px; margin-bottom:24px; }}
  .kpi-card {{ background:white; border-radius:12px; padding:18px; text-align:center; box-shadow:0 1px 4px rgba(0,0,0,0.08); transition:transform 0.2s,box-shadow 0.2s; position:relative; overflow:hidden; }}
  .kpi-card:hover {{ transform:translateY(-2px); box-shadow:0 4px 16px rgba(0,0,0,0.12); }}
  .kpi-card .corner {{ position:absolute; top:0; right:0; width:0; height:0; border-style:solid; }}
  .kpi-card .kpi-icon {{ font-size:22px; margin-bottom:6px; }}
  .kpi-card .kpi-label {{ font-size:11px; color:#777; font-weight:600; text-transform:uppercase; margin-bottom:8px; }}
  .kpi-card .kpi-value {{ font-size:28px; font-weight:800; line-height:1; margin-bottom:6px; }}
  .kpi-card .kpi-trend {{ font-size:11px; font-weight:600; padding:3px 8px; border-radius:20px; display:inline-block; }}
  .kpi-card .kpi-year {{ font-size:10px; color:#999; margin-top:4px; }}
  .kpi-card .kpi-floor {{ font-size:10px; color:#999; margin-top:2px; }}
  .alerts-bar {{ display:flex; gap:12px; margin-bottom:20px; flex-wrap:wrap; }}
  .alert-chip {{ padding:8px 16px; border-radius:20px; font-size:12px; font-weight:600; display:flex; align-items:center; gap:6px; cursor:pointer; transition:transform 0.15s; }}
  .alert-chip:hover {{ transform:scale(1.03); }}
  .alert-chip.critical {{ background:#FFEBEE; color:#C62828; border:1.5px solid #FFCDD2; }}
  .alert-chip.high {{ background:#FFF3E0; color:#E65100; border:1.5px solid #FFE0B2; }}
  .alert-chip.medium {{ background:#FFFDE7; color:#F57F17; border:1.5px solid #FFF9C4; }}
  .alert-chip.ok {{ background:#E8F5E9; color:#2E7D32; border:1.5px solid #C8E6C9; }}
  .section {{ background:white; border-radius:12px; padding:20px; margin-bottom:20px; box-shadow:0 1px 4px rgba(0,0,0,0.08); }}
  .section-header {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; padding-bottom:12px; border-bottom:2px solid #EEF2FF; }}
  .section-title {{ font-size:15px; font-weight:700; color:#1a237e; display:flex; align-items:center; gap:8px; }}
  .section-actions {{ display:flex; gap:8px; }}
  .btn {{ padding:6px 14px; border-radius:6px; font-size:12px; font-weight:600; cursor:pointer; border:none; transition:all 0.2s; display:flex; align-items:center; gap:5px; }}
  .btn-primary {{ background:#1a237e; color:white; }}
  .btn-primary:hover {{ background:#283593; }}
  .btn-outline {{ background:white; color:#1a237e; border:1.5px solid #1a237e; }}
  .btn-outline:hover {{ background:#EEF2FF; }}
  .btn-sm {{ padding:4px 10px; font-size:11px; }}
  .data-table {{ width:100%; border-collapse:collapse; font-size:13px; }}
  .data-table th {{ background:#EEF2FF; color:#1a237e; padding:10px 12px; text-align:left; font-weight:700; font-size:11px; text-transform:uppercase; border-bottom:2px solid #C5CAE9; }}
  .data-table td {{ padding:10px 12px; border-bottom:1px solid #F0F0F0; }}
  .data-table tr:hover td {{ background:#FAFAFA; }}
  .data-table .num {{ text-align:right; font-variant-numeric:tabular-nums; }}
  .data-table .center {{ text-align:center; }}
  .data-table .status-ok {{ color:#2E7D32; font-weight:700; }}
  .data-table .status-warn {{ color:#E65100; font-weight:700; }}
  .data-table .status-danger {{ color:#C62828; font-weight:700; }}
  .camels-grid {{ display:grid; grid-template-columns:repeat(6,1fr); gap:12px; margin-bottom:20px; }}
  .camels-card {{ background:white; border-radius:12px; padding:16px; text-align:center; box-shadow:0 1px 4px rgba(0,0,0,0.08); }}
  .camels-card .letter {{ font-size:28px; font-weight:900; color:white; border-radius:8px; display:inline-block; width:44px; height:44px; line-height:44px; margin-bottom:8px; }}
  .camels-card .name {{ font-size:10px; color:#777; text-transform:uppercase; margin-bottom:6px; }}
  .camels-card .score {{ font-size:36px; font-weight:900; line-height:1; margin-bottom:4px; }}
  .camels-card .trend {{ font-size:11px; font-weight:600; }}
  .camels-card .total {{ font-size:11px; color:#777; }}
  .weakness-card {{ background:white; border-radius:12px; margin-bottom:14px; overflow:hidden; border-left:5px solid; box-shadow:0 1px 4px rgba(0,0,0,0.08); }}
  .weakness-header {{ padding:14px 18px; display:flex; align-items:flex-start; justify-content:space-between; gap:12px; }}
  .weakness-title {{ font-size:14px; font-weight:700; margin-bottom:6px; }}
  .weakness-desc {{ font-size:12px; color:#555; line-height:1.6; margin-bottom:10px; }}
  .weakness-body {{ padding:0 18px 14px; }}
  .weakness-tags {{ display:flex; flex-wrap:wrap; gap:6px; margin-bottom:10px; }}
  .tag {{ padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; }}
  .tag.critical {{ background:#FFEBEE; color:#C62828; }}
  .tag.high {{ background:#FFF3E0; color:#E65100; }}
  .tag.medium {{ background:#FFFDE7; color:#F57F17; }}
  .tag.rootcause {{ background:#FFF3E0; color:#E65100; }}
  .tag.strategic {{ background:#EEF2FF; color:#1a237e; }}
  .tag.policy {{ background:#E3F2FD; color:#1565C0; }}
  .tag.ops {{ background:#E8F5E9; color:#2E7D32; }}
  .tag.quickwin {{ background:#F3E5F5; color:#6A1B9A; }}
  .weakness-metrics {{ background:#FAFAFA; border-radius:8px; padding:10px 14px; margin-bottom:10px; font-size:12px; display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:8px; }}
  .metric-item {{ display:flex; flex-direction:column; }}
  .metric-label {{ font-size:10px; color:#999; text-transform:uppercase; }}
  .metric-value {{ font-size:13px; font-weight:700; color:#1a237e; }}
  .solution-block {{ margin-top:8px; padding:10px 14px; border-radius:8px; font-size:12px; line-height:1.6; }}
  .solution-block.strategic {{ background:#EEF2FF; border-left:4px solid #1a237e; }}
  .solution-block.policy {{ background:#E3F2FD; border-left:4px solid #1565C0; }}
  .solution-block.ops {{ background:#E8F5E9; border-left:4px solid #2E7D32; }}
  .solution-block.quickwin {{ background:#F3E5F5; border-left:4px solid #6A1B9A; }}
  .solution-label {{ font-size:10px; font-weight:700; text-transform:uppercase; margin-bottom:4px; opacity:0.7; }}
  .bar-chart {{ margin-bottom:20px; }}
  .bar-row {{ display:flex; align-items:center; margin-bottom:10px; gap:10px; }}
  .bar-label {{ font-size:12px; font-weight:600; width:140px; flex-shrink:0; }}
  .bar-track {{ flex:1; background:#F0F0F0; border-radius:6px; height:24px; position:relative; overflow:hidden; }}
  .bar-fill {{ height:100%; border-radius:6px; transition:width 0.8s ease; display:flex; align-items:center; padding-left:8px; }}
  .bar-value {{ font-size:11px; font-weight:700; color:white; white-space:nowrap; }}
  .bar-benchmark {{ position:absolute; top:0; height:100%; width:2px; background:#C62828; }}
  .comment-section {{ background:white; border-radius:12px; padding:16px; margin-top:20px; }}
  .comment-input {{ display:flex; gap:10px; margin-bottom:14px; }}
  .comment-input textarea {{ flex:1; padding:10px 14px; border:1.5px solid #E0E0E0; border-radius:8px; font-size:13px; resize:vertical; min-height:60px; font-family:inherit; }}
  .comment-input textarea:focus {{ outline:none; border-color:#1a237e; }}
  .comment-list {{ max-height:300px; overflow-y:auto; }}
  .comment-item {{ padding:10px 0; border-bottom:1px solid #F0F0F0; display:flex; gap:10px; }}
  .comment-avatar {{ width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700; color:white; flex-shrink:0; }}
  .comment-body {{ flex:1; }}
  .comment-meta {{ font-size:11px; color:#999; margin-bottom:3px; }}
  .comment-meta strong {{ color:#1a237e; }}
  .comment-text {{ font-size:13px; color:#333; line-height:1.5; }}
  .perm-table .perm-yes {{ color:#2E7D32; font-weight:700; }}
  .perm-table .perm-no {{ color:#C62828; }}
  .perm-role-badge {{ padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; color:white; }}
  .role-switcher {{ background:linear-gradient(135deg,#1a237e,#1565C0); border-radius:10px; padding:12px 20px; margin-bottom:20px; display:flex; gap:10px; flex-wrap:wrap; align-items:center; }}
  .role-switcher label {{ color:white; font-size:13px; font-weight:600; }}
  .role-switcher select {{ padding:6px 12px; border-radius:6px; border:none; font-size:13px; font-weight:600; }}
  .role-note {{ color:rgba(255,255,255,0.7); font-size:11px; }}
  .export-bar {{ background:white; border-radius:10px; padding:14px 20px; margin-top:20px; display:flex; gap:10px; flex-wrap:wrap; align-items:center; box-shadow:0 1px 4px rgba(0,0,0,0.08); }}
  @media(max-width:768px){{ .camels-grid{{grid-template-columns:repeat(3,1fr);}} .kpi-grid{{grid-template-columns:repeat(2,1fr);}} .header-title h1{{font-size:14px;}} .tabs{{padding:0 12px;}} .tab{{padding:10px 12px;font-size:12px;}} .content{{padding:12px;}} }}
</style>
</head>
<body>

<div class="header">
  <div class="header-top">
    <div class="header-title">
      <div>
        <h1>🏦 {bank["name"]}</h1>
        <span>Báo Cáo Tài Chính Chuyên Sâu — Q{bank["report_quarter"]}/{bank["report_year"]}</span>
      </div>
    </div>
    <div class="header-badges">
      <span class="badge" style="background:{camels_badge_color};border-color:{camels_badge_color}">CAMELS {cam_total_2025:.1f}</span>
      <span class="badge" style="background:#C62828;border-color:#C62828">⚠️ {critical_count} Cảnh báo khẩn</span>
      <span class="badge">📅 {bank["report_date"]}</span>
    </div>
  </div>
  <div class="header-meta">
    <span>📋 Phiên bản: {bank["version"]}</span>
    <span>👤 {bank["prepared_by"]}</span>
    <span>🔍 Kiểm toán: {bank["auditor"]}</span>
    <span>👁️ Đang xem: <strong id="current-role">Ban Lãnh đạo</strong></span>
  </div>
</div>

<div class="tabs" id="tab-bar">
  <div class="tab active" data-tab="dashboard">📊 Tổng quan</div>
  <div class="tab" data-tab="camels">🎯 CAMELS</div>
  <div class="tab" data-tab="asset">💰 Chất lượng Tài sản</div>
  <div class="tab" data-tab="liquidity">💵 Thanh khoản & Vốn</div>
  <div class="tab" data-tab="earnings">📉 Thu nhập & Lợi nhuận</div>
  <div class="tab" data-tab="weaknesses">⚠️ Điểm yếu & Giải pháp</div>
  <div class="tab" data-tab="industry">🏭 So sánh ngành</div>
  <div class="tab admin-only" data-tab="permissions">👥 Phân quyền</div>
</div>

<div class="content">

<div class="role-switcher">
  <label>👤 Xem với vai trò:</label>
  <select id="role-select" onchange="switchRole(this.value)">
    <option value="executive">🏦 Ban Lãnh đạo</option>
    <option value="finance">💹 Phòng Tài chính</option>
    <option value="risk">⚠️ Phòng QTRR</option>
    <option value="audit">🔍 Phòng Kiểm toán</option>
    <option value="accounting">📋 Phòng Kế toán</option>
    <option value="credit">💳 Phòng Tín dụng</option>
    <option value="marketing">📢 Phòng Marketing</option>
    <option value="branch">🏢 Chi nhánh</option>
  </select>
  <span class="role-note">→ Thay đổi vai trò để xem phạm vi dữ liệu khác nhau</span>
</div>

<!-- TAB 1: Dashboard -->
<div class="tab-content active" id="tab-dashboard">
  <div class="alerts-bar">
    {alert_chips_html}
  </div>
  <div class="kpi-grid">
    {kpi_cards_html}
  </div>
  <div class="section">
    <div class="section-header">
      <div class="section-title">⚠️ Điểm yếu cốt lõi cần ưu tiên</div>
    </div>
    {weakness_summary_html}
  </div>
  <div class="section">
    <div class="section-header">
      <div class="section-title">📊 Điểm CAMELS 2025</div>
      <span style="font-size:12px;color:#999">Trung bình: <strong style="color:{camels_total_color}">{cam_total_2025:.2f}</strong></span>
    </div>
    <div class="camels-grid">
      {camels_mini_html}
    </div>
  </div>
</div>

<!-- TAB 2: CAMELS -->
<div class="tab-content" id="tab-camels">
  <div class="section">
    <div class="section-header">
      <div class="section-title">🎯 CAMELS Scorecard — Chi tiết 3 năm</div>
      <div class="section-actions">
        <button class="btn btn-primary btn-sm" onclick="alert('Export PDF')">📄 PDF</button>
        <button class="btn btn-outline btn-sm" onclick="alert('See Excel dashboard')">📊 Excel</button>
      </div>
    </div>
    <table class="data-table">
      <thead>
        <tr><th>Thành phần</th><th>Trọng số</th><th>2023</th><th>2024</th><th>2025</th><th>Δ 2023→2025</th><th>Chỉ số cụ thể</th><th>Benchmark</th><th>Đánh giá</th></tr>
      </thead>
      <tbody>
        {camels_table_html}
        <tr style="background:#EEF2FF;font-weight:700">
          <td>TỔNG ĐIỂM CAMELS</td>
          <td class="center">100%</td>
          <td class="center" style="color:#2E7D32;font-size:15px">{sum(cam["2023"].values())/6:.2f}</td>
          <td class="center" style="color:#E65100;font-size:15px">{sum(cam["2024"].values())/6:.2f}</td>
          <td class="center" style="color:#C62828;font-size:15px">{cam_total_2025:.2f}</td>
          <td class="center" style="color:#C62828">{cam_total_2025-sum(cam["2023"].values())/6:+.2f}</td>
          <td colspan="3" style="color:#C62828;font-size:12px">⚠️ Điểm số giảm liên tục — Cần can thiệp chiến lược toàn diện</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>

<!-- TAB 3: Asset -->
<div class="tab-content" id="tab-asset">
  <div class="section">
    <div class="section-header">
      <div class="section-title">💰 Chất lượng Tài sản & NPL</div>
    </div>
    <div class="bar-chart">
      <div class="bar-row">
        <div class="bar-label">NPL Ratio (%)</div>
        <div class="bar-track">
          <div class="bar-fill" style="width:{rat["2025"]["NPL_Ratio"]/7*100:.0f}%;background:linear-gradient(90deg,#E65100,#C62828);">
            <span class="bar-value">{rat["2025"]["NPL_Ratio"]}%</span>
          </div>
          <div class="bar-benchmark" style="left:{bench["NPL_floor_warning"]/7*100:.0f}%;background:#C62828"></div>
        </div>
      </div>
      <div class="bar-row">
        <div class="bar-label">NPL Coverage (%)</div>
        <div class="bar-track">
          <div class="bar-fill" style="width:{rat["2025"]["NPL_Coverage"]:.0f}%;background:linear-gradient(90deg,#C62828,#E65100);">
            <span class="bar-value">{rat["2025"]["NPL_Coverage"]}%</span>
          </div>
          <div class="bar-benchmark" style="left:70%;background:#2E7D32"></div>
        </div>
      </div>
      <div class="bar-row">
        <div class="bar-label">Tăng trưởng dư nợ (%)</div>
        <div class="bar-track">
          <div class="bar-fill" style="width:{rat["2025"]["Growth_Loans"]/15*100:.0f}%;background:linear-gradient(90deg,#1a237e,#1565C0);">
            <span class="bar-value">{rat["2025"]["Growth_Loans"]}%</span>
          </div>
        </div>
      </div>
    </div>
    <table class="data-table">
      <thead><tr><th>Chỉ số</th><th>2023</th><th>2024</th><th>2025</th><th>Floor</th><th>Trạng thái</th></tr></thead>
      <tbody>
        {asset_rows_html}
      </tbody>
    </table>
  </div>
</div>

<!-- TAB 4: Liquidity -->
<div class="tab-content" id="tab-liquidity">
  <div class="section">
    <div class="section-header">
      <div class="section-title">💵 Thanh khoản & Vốn</div>
    </div>
    <div class="kpi-grid">
      {liq_kpi_html}
    </div>
    <table class="data-table">
      <thead><tr><th>Chỉ số</th><th>2023</th><th>2024</th><th>2025</th><th>Floor NHNN</th><th>Xu hướng</th><th>Rủi ro</th></tr></thead>
      <tbody>
        {liq_rows_html}
      </tbody>
    </table>
  </div>
</div>

<!-- TAB 5: Earnings -->
<div class="tab-content" id="tab-earnings">
  <div class="section">
    <div class="section-header">
      <div class="section-title">📉 Thu nhập & Lợi nhuận</div>
    </div>
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="corner" style="border-width:40px 40px 0 0;border-color:#C62828 transparent transparent transparent;"></div>
        <div class="kpi-icon">💰</div><div class="kpi-label">ROE</div>
        <div class="kpi-value" style="color:#C62828">{rat["2025"]["ROE"]:.1f}%</div>
        <div class="kpi-trend" style="background:#FFEBEE;color:#C62828">🔴 Sụt giảm</div>
        <div class="kpi-year">2023:{rat["2023"]["ROE"]:.1f}% → 2024:{rat["2024"]["ROE"]:.1f}% → 2025:{rat["2025"]["ROE"]:.1f}%</div>
      </div>
      <div class="kpi-card">
        <div class="corner" style="border-width:40px 40px 0 0;border-color:#E65100 transparent transparent transparent;"></div>
        <div class="kpi-icon">📈</div><div class="kpi-label">NIM</div>
        <div class="kpi-value" style="color:#E65100">{rat["2025"]["NIM"]:.2f}%</div>
        <div class="kpi-trend" style="background:#FFF8E1;color:#E65100">🟡 Giảm liên tục</div>
        <div class="kpi-year">2023:{rat["2023"]["NIM"]:.2f}% → 2024:{rat["2024"]["NIM"]:.2f}% → 2025:{rat["2025"]["NIM"]:.2f}%</div>
      </div>
      <div class="kpi-card">
        <div class="corner" style="border-width:40px 40px 0 0;border-color:#C62828 transparent transparent transparent;"></div>
        <div class="kpi-icon">⚖️</div><div class="kpi-label">Cost/Income</div>
        <div class="kpi-value" style="color:#C62828">{rat["2025"]["Cost_to_Income"]:.1f}%</div>
        <div class="kpi-trend" style="background:#FFEBEE;color:#C62828">🔴 Vượt benchmark</div>
        <div class="kpi-year">Benchmark ngành: 45%</div>
      </div>
      <div class="kpi-card">
        <div class="corner" style="border-width:40px 40px 0 0;border-color:#C62828 transparent transparent transparent;"></div>
        <div class="kpi-icon">📊</div><div class="kpi-label">Lợi nhuận ST</div>
        <div class="kpi-value" style="color:#C62828">{inc["2025"]["profit_after_tax"]:,.0f}</div>
        <div class="kpi-trend" style="background:#FFEBEE;color:#C62828">🔴 Gần như bằng 0</div>
        <div class="kpi-year">Đơn vị: Tỷ VND</div>
      </div>
    </div>
    <table class="data-table">
      <thead><tr><th>Khoản mục (Tỷ VND)</th><th>2023</th><th>2024</th><th>2025</th><th>Δ 2024→2025</th><th>Notes</th></tr></thead>
      <tbody>
        {earnings_rows_html}
      </tbody>
    </table>
  </div>
</div>

<!-- TAB 6: Weaknesses -->
<div class="tab-content" id="tab-weaknesses">
  <div class="section">
    <div class="section-header">
      <div class="section-title">⚠️ Chi tiết điểm yếu cốt lõi & Giải pháp</div>
      <div class="section-actions">
        <span style="font-size:12px;color:#999">{len(wks)} điểm yếu được phân tích</span>
      </div>
    </div>
    {weakness_detail_html}
  </div>
</div>

<!-- TAB 7: Industry -->
<div class="tab-content" id="tab-industry">
  <div class="section">
    <div class="section-header">
      <div class="section-title">🏭 So sánh với Benchmark ngành</div>
    </div>
    <table class="data-table">
      <thead><tr><th>Chỉ số</th><th>VDB 2025</th><th>Benchmark ngành</th><th>Chênh lệch</th><th>Đánh giá</th></tr></thead>
      <tbody>
        <tr><td>NPL Ratio (%)</td><td class="num" style="color:#C62828;font-weight:700">{rat["2025"]["NPL_Ratio"]:.1f}</td><td class="num">&lt; 3.0</td><td class="num" style="color:#C62828">+{rat["2025"]["NPL_Ratio"]-3.0:.1f}</td><td><span class="tag critical">Kém hơn</span></td></tr>
        <tr><td>CAR (%)</td><td class="num" style="color:#E65100;font-weight:700">{rat["2025"]["CAR"]:.1f}</td><td class="num">&gt; 10.0</td><td class="num" style="color:#E65100">{rat["2025"]["CAR"]-10.0:+.1f}</td><td><span class="tag high">Dưới TB</span></td></tr>
        <tr><td>LCR (%)</td><td class="num" style="color:#E65100;font-weight:700">{rat["2025"]["LCR"]}</td><td class="num">&gt; 110</td><td class="num" style="color:#E65100">{rat["2025"]["LCR"]-110:+.0f}</td><td><span class="tag high">Dưới TB</span></td></tr>
        <tr><td>NIM (%)</td><td class="num" style="color:#C62828;font-weight:700">{rat["2025"]["NIM"]:.2f}</td><td class="num">3.2</td><td class="num" style="color:#C62828">{rat["2025"]["NIM"]-3.2:+.2f}</td><td><span class="tag critical">Kém hơn</span></td></tr>
        <tr><td>ROE (%)</td><td class="num" style="color:#C62828;font-weight:700">{rat["2025"]["ROE"]:.1f}</td><td class="num">&gt; 10.5</td><td class="num" style="color:#C62828">{rat["2025"]["ROE"]-10.5:+.1f}</td><td><span class="tag critical">Kém hơn</span></td></tr>
        <tr><td>Cost/Income (%)</td><td class="num" style="color:#C62828;font-weight:700">{rat["2025"]["Cost_to_Income"]:.1f}</td><td class="num">&lt; 45.0</td><td class="num" style="color:#C62828">+{rat["2025"]["Cost_to_Income"]-45.0:.1f}</td><td><span class="tag critical">Kém hơn</span></td></tr>
        <tr><td>LDR (%)</td><td class="num" style="color:#E65100;font-weight:700">{rat["2025"]["LDR"]:.1f}</td><td class="num">&lt; 80</td><td class="num" style="color:#E65100">+{rat["2025"]["LDR"]-80:.1f}</td><td><span class="tag high">Vượt ngưỡng</span></td></tr>
      </tbody>
    </table>
    <div style="margin-top:16px;padding:14px;background:#FFF3E0;border-radius:8px;font-size:12px;line-height:1.7">
      <strong style="color:#E65100">📌 Nhận xét:</strong> VDB đang yếu hơn benchmark ngành ở hầu hết các chỉ số quan trọng. Đặc biệt NIM và ROE thấp hơn rõ rệt, phản ánh khủng hoảng thu nhập nghiêm trọng. Cần can thiệp toàn diện trên cả chiến lược vốn, cơ cấu tín dụng và quản trị chi phí.
    </div>
  </div>
</div>

<!-- TAB 8: Permissions -->
<div class="tab-content" id="tab-permissions">
  <div class="section">
    <div class="section-header">
      <div class="section-title">👥 Phân Quyền Dashboard (RBAC)</div>
      <div class="section-actions">
        <span style="font-size:12px;color:#999">8 vai trò | Audit log: Bật</span>
      </div>
    </div>
    <table class="data-table perm-table">
      <thead>
        <tr><th>Vai trò</th><th>Xem toàn bộ</th><th>Cập nhật</th><th>Chỉnh sửa</th><th>Export</th><th>Quản lý user</th><th>Bình luận</th><th>Phạm vi dữ liệu</th></tr>
      </thead>
      <tbody>
        {perm_rows_html}
      </tbody>
    </table>
    <div style="margin-top:16px;padding:14px;background:#E8EAF6;border-radius:8px;font-size:12px;line-height:1.7">
      <strong style="color:#1a237e">📋 Ghi chú RBAC:</strong>
      <ul style="margin:8px 0 0 16px">
        <li>Audit Trail: Mọi hành động xem/sửa đều được ghi log (lưu 365 ngày)</li>
        <li>Row-Level Security: Chi nhánh chỉ xem dữ liệu chi nhánh mình</li>
        <li>Phân quyền thay đổi cần xác nhận từ Trưởng phòng HC-NS + Ban Lãnh đạo</li>
        <li>Bảo mật: Dữ liệu NPL, CAR, LCR chỉ hiển thị cho Phòng QTRR + Ban Lãnh đạo</li>
      </ul>
    </div>
  </div>
</div>

<!-- Comments -->
<div class="comment-section">
  <div style="font-size:14px;font-weight:700;color:#1a237e;margin-bottom:12px">💬 Bình luận & Phản hồi</div>
  <div class="comment-input">
    <textarea placeholder="Nhập bình luận của bạn..."></textarea>
    <button class="btn btn-primary" onclick="addComment()">Gửi</button>
  </div>
  <div class="comment-list">
    <div class="comment-item">
      <div class="comment-avatar" style="background:#C62828">QT</div>
      <div class="comment-body">
        <div class="comment-meta"><strong>Phòng QTRR</strong> — 2026-01-28 14:32</div>
        <div class="comment-text">CAR sát ngưỡng 8% — đề xuất họp khẩn Ban Điều hành trong tuần này. Cần phát hành Tier 2 gấp.</div>
      </div>
    </div>
    <div class="comment-item">
      <div class="comment-avatar" style="background:#1a237e">TC</div>
      <div class="comment-body">
        <div class="comment-meta"><strong>Phòng Tài chính</strong> — 2026-01-28 15:10</div>
        <div class="comment-text">Lợi nhuận Q4/2025 gần bằng 0 là do trích lập dự phòng bổ sung theo chỉ đạo NHNN. Hoạt động kinh doanh cốt lõi vẫn ổn định.</div>
      </div>
    </div>
    <div class="comment-item">
      <div class="comment-avatar" style="background:#6A1B9A">KT</div>
      <div class="comment-body">
        <div class="comment-meta"><strong>Phòng Kiểm toán</strong> — 2026-01-29 09:15</div>
        <div class="comment-text">Đề nghị bổ sung phân tích off-balance sheet commitments. Cam kết ngoại bảng tăng 35% trong 2 năm cần được giám sát chặt.</div>
      </div>
    </div>
  </div>
</div>

<!-- Export -->
<div class="export-bar">
  <span style="font-weight:600;color:#333;font-size:13px">📥 Xuất báo cáo:</span>
  <button class="btn btn-primary" onclick="alert('Export PDF')">📄 Xuất PDF</button>
  <button class="btn btn-outline" onclick="alert('Excel dashboard ready')">📊 Xuất Excel</button>
  <button class="btn btn-outline" onclick="alert('Share link copied')">🔗 Share Link</button>
  <span style="margin-left:auto;font-size:11px;color:#999">Generated by Claude Opus 4.6 | VDB Financial Analysis v1.0</span>
</div>

</div><!-- /content -->

<script>
document.querySelectorAll('.tab').forEach(tab => {{
  tab.addEventListener('click', () => {{
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
  }});
}});

function switchRole(role) {{
  const names = {{executive:"Ban Lãnh đạo",finance:"Phòng Tài chính",risk:"Phòng QTRR",audit:"Phòng Kiểm toán",accounting:"Phòng Kế toán",credit:"Phòng Tín dụng",marketing:"Phòng KH & Marketing",branch:"Chi nhánh"}};
  document.getElementById('current-role').textContent = names[role] || role;
  const adminTab = document.querySelector('[data-tab="permissions"]');
  adminTab.style.display = (role==='executive'||role==='finance'||role==='risk')?'flex':'none';
  document.querySelector('.role-switcher').style.background = (role==='executive'||role==='finance'||role==='risk')?'linear-gradient(135deg,#1a237e,#1565C0)':'linear-gradient(135deg,#455A64,#607D8B)';
}}

function addComment() {{
  const ta = document.querySelector('.comment-input textarea');
  if (!ta.value.trim()) return;
  const list = document.querySelector('.comment-list');
  const div = document.createElement('div');
  div.className = 'comment-item';
  div.innerHTML = `<div class="comment-avatar" style="background:#1a237e">BN</div><div class="comment-body"><div class="comment-meta"><strong>Ban Người dùng</strong> — ${{new Date().toLocaleString('vi-VN')}}</div><div class="comment-text">${{ta.value.trim()}}</div></div>`;
  list.prepend(div);
  ta.value = '';
}}

switchRole('executive');
</script>

</body>
</html>
"""

# ─── Save ─────────────────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "../output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"VDB_LandingPage_{bank['report_quarter']}_{bank['report_year']}.html")
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html)
print(f"✅ Landing page saved: {OUTPUT_FILE}")

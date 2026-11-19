"""
Executive PDF Report Generation using ReportLab.
Compiles comprehensive organizational financial health, Butterfly Effect simulations,
investment analyses, risk assessments, and AI strategic recommendations.
"""

from typing import Dict, Any, List, Optional
import os
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
)
import config
from utils.calculations import format_currency


def generate_financial_pdf_report(
    org_data: Dict[str, Any],
    financial_summary: Dict[str, Any],
    investment_summary: Dict[str, Any],
    savings_summary: Dict[str, Any],
    butterfly_summary: Dict[str, Any],
    risk_summary: Dict[str, Any],
    ai_recommendations: Optional[str] = None,
    output_path: Optional[str] = None,
) -> bytes:
    """
    Builds a professional executive PDF dossier.
    Returns bytes and optionally writes to output_path.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom ReportLab Styles
    navy = colors.HexColor("#0b132b")
    emerald = colors.HexColor("#10b981")
    gold = colors.HexColor("#f59e0b")
    slate = colors.HexColor("#334155")
    light_slate = colors.HexColor("#f8fafc")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=navy,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=14,
        textColor=gold,
    )
    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=navy,
        spaceBefore=14,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=slate,
    )
    bold_body = ParagraphStyle(
        "DocBodyBold",
        parent=body_style,
        fontName="Helvetica-Bold",
    )

    elements = []

    # 1. Header / Title Block
    elements.append(Paragraph(config.APP_NAME.upper(), title_style))
    elements.append(Paragraph(config.APP_SUBTITLE, subtitle_style))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=2, color=emerald, spaceAfter=12))

    # 2. Metadata Banner
    org_name = org_data.get("name", "Organisation")
    currency = org_data.get("currency", "₹")
    report_date = datetime.now().strftime("%d %B %Y, %H:%M UTC")

    meta_table_data = [
        [
            Paragraph("<b>Target Organisation:</b>", body_style),
            Paragraph(f"<b>{org_name}</b>", bold_body),
            Paragraph("<b>Report Generated:</b>", body_style),
            Paragraph(report_date, body_style),
        ],
        [
            Paragraph("<b>Industry / Type:</b>", body_style),
            Paragraph(org_data.get("org_type", "Corporate"), body_style),
            Paragraph("<b>Base Currency:</b>", body_style),
            Paragraph(f"{currency} ({config.CURRENCY_CODE})", body_style),
        ],
    ]
    meta_table = Table(meta_table_data, colWidths=[120, 150, 110, 160])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), light_slate),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 14))

    # 3. Executive Financial Overview Table
    elements.append(Paragraph("1. Executive Financial Baseline", h1_style))
    fin_data = [
        ["Financial Metric", "Reported Amount", "Health Indicator"],
        ["Total Revenue", format_currency(financial_summary.get("total_revenue", 0), currency), "Top-Line Baseline"],
        ["Operating Expenses", format_currency(financial_summary.get("total_expenses", 0), currency), "Cost Base"],
        ["Net Profit", format_currency(financial_summary.get("net_profit", 0), currency), f"Margin: {financial_summary.get('profit_margin', 0):.1f}%"],
        ["Liquid Cash Reserves", format_currency(financial_summary.get("cash_reserves", 0), currency), "Treasury Balance"],
        ["Current Liquidity Ratio", f"{financial_summary.get('current_ratio', 0):.2f}", "Benchmark ≥ 1.5x"],
        ["Debt-to-Assets Ratio", f"{financial_summary.get('debt_ratio', 0):.2f}", "Benchmark ≤ 0.5x"],
    ]
    t_fin = Table(fin_data, colWidths=[180, 180, 180])
    t_fin.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), navy),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_slate]),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(t_fin)
    elements.append(Spacer(1, 12))

    # 4. Butterfly Effect Simulation Ripple Summary
    elements.append(Paragraph("2. The Financial Butterfly Effect: Multi-Stage Ripple Analysis", h1_style))
    b_desc = (
        "Mathematical simulation of interconnected second-order consequences triggered by capital reallocations. "
        "Every small decision transmits changes across employee productivity, capacity, and bottom-line stability."
    )
    elements.append(Paragraph(b_desc, body_style))
    elements.append(Spacer(1, 6))

    ripple_deltas = butterfly_summary.get("final_5yr_deltas", {})
    if ripple_deltas:
        b_table_data = [["Financial Node", "5-Year Cumulative Delta (%)", "Transmission Mechanism"]]
        for node, delta in list(ripple_deltas.items())[:8]:
            status_text = "Favorable Expansion" if delta > 0 else "Contraction / Drag"
            if node in ["Operating Expenses", "Debt"]:
                status_text = "Favorable Reduction" if delta < 0 else "Cost Inflation"
            b_table_data.append([node, f"{delta:+.1%}", status_text])

        t_ripple = Table(b_table_data, colWidths=[180, 160, 200])
        t_ripple.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), emerald),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_slate]),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(t_ripple)
    else:
        elements.append(Paragraph("No active simulation executed prior to report generation.", body_style))

    elements.append(Spacer(1, 12))

    # 5. Investment & Savings Modules Summary
    elements.append(Paragraph("3. Capital Allocation & Savings Rationalization", h1_style))
    inv_total = investment_summary.get("total_invested", 0.0)
    inv_yield = investment_summary.get("weighted_return", 0.0)
    pot_savings = savings_summary.get("potential_total_savings", 0.0)

    alloc_data = [
        ["Capital Domain", "Assigned Value", "Key Strategic Directive"],
        ["Total Active Investments", format_currency(inv_total, currency), f"Weighted Expected Return: {inv_yield*100:.2f}% (Analytical)"],
        ["Portfolio Net Present Value (NPV)", format_currency(investment_summary.get("portfolio_npv", 0), currency), "Discount Rate: 8.0%"],
        ["Identified Expense Savings Potential", format_currency(pot_savings, currency), "Non-disruptive overhead trimming"],
    ]
    t_alloc = Table(alloc_data, colWidths=[180, 170, 190])
    t_alloc.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), navy),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(t_alloc)
    elements.append(Spacer(1, 12))

    # 6. Risk Profile
    elements.append(Paragraph("4. Enterprise Financial Risk Diagnosis", h1_style))
    risk_score = risk_summary.get("overall_risk_score", 50.0)
    risk_tier = risk_summary.get("risk_tier", "Moderate")

    risk_table_data = [
        ["Risk Dimension", "Score (0-100)", "Status Assessment"],
        ["Overall Weighted Risk Score", f"{risk_score}/100", risk_tier],
        ["Liquidity Shortfall Risk", f"{risk_summary.get('liquidity_risk', 50)}/100", "Cash buffer against short-term debt"],
        ["Debt Leverage Risk", f"{risk_summary.get('debt_risk', 50)}/100", "Solvency sensitivity"],
        ["Cash Burn / Runway Risk", f"{risk_summary.get('cash_flow_risk', 50)}/100", f"Runway: {risk_summary.get('runway_months', 0):.1f} months"],
    ]
    t_risk = Table(risk_table_data, colWidths=[180, 120, 240])
    t_risk.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e11d48")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(t_risk)
    elements.append(Spacer(1, 12))

    # 7. AI Executive Recommendations
    elements.append(Paragraph("5. AI Strategic Decision Support Briefing", h1_style))
    ai_text = ai_recommendations or (
        "Maintain conservative liquidity buffers. The Financial Butterfly Effect confirms that while "
        "cost-cutting delivers immediate margin expansion, excessive reductions in training and technology "
        "severely hamper worker productivity by Year 2, reducing long-term enterprise value."
    )
    elements.append(Paragraph(ai_text.replace("\n", "<br/>"), body_style))
    elements.append(Spacer(1, 12))

    # 8. Disclaimer & Limitations
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=8))
    disclaimer = (
        "<b>LEGAL & FINANCIAL DISCLAIMER:</b> This report is generated by an autonomous decision-support platform. "
        "All investment yields, savings projections, and ripple effects are based on mathematical models and assumptions, "
        "not commercial guarantees. Historical inputs may include synthetic demonstration data. Formal board decisions "
        "must be validated by certified public accountants and chartered financial analysts."
    )
    elements.append(Paragraph(disclaimer, ParagraphStyle("Discl", parent=body_style, fontSize=7, leading=9, textColor=colors.HexColor("#64748b"))))

    # Build PDF
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    if output_path:
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes

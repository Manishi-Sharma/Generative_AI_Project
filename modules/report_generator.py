import io
import re
import html
from datetime import datetime, timezone
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from utils.formatting import format_currency

def format_markdown_for_reportlab(text: str) -> str:
    """
    Safely translates basic markdown bold, italic, and headers to ReportLab XML tags.
    """
    # Escape raw XML/HTML characters first
    escaped = html.escape(text)

    # Convert escaped bold **text** to <b>text</b>
    escaped = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', escaped)

    # Convert escaped italic *text* or _text_ to <i>text</i>
    escaped = re.sub(r'\*(.+?)\*', r'<i>\1</i>', escaped)

    return escaped

class PDFReportGenerator:
    """
    Generates professional, structured academic financial audit and ripple-effect simulation reports.
    """

    @staticmethod
    def generate_pdf(
        org_data: Dict[str, Any],
        financial_records: List[Dict[str, Any]],
        calculations: Dict[str, Any],
        simulation_result: Dict[str, Any],
        ai_analysis_text: str
    ) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom Palette
        c_primary = colors.HexColor("#0A1128")
        c_secondary = colors.HexColor("#034078")
        c_accent = colors.HexColor("#1282A2")
        c_dark = colors.HexColor("#1F2937")
        c_light = colors.HexColor("#F9FAFB")
        c_border = colors.HexColor("#E5E7EB")

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=c_primary,
            spaceAfter=4
        )

        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            textColor=c_secondary,
            spaceAfter=12
        )

        h2_style = ParagraphStyle(
            "Heading2Custom",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=c_secondary,
            spaceBefore=14,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            "BodyCustom",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=c_dark,
            spaceAfter=6
        )

        story = []

        # Header Title
        story.append(Paragraph("THE FINANCIAL BUTTERFLY EFFECT", title_style))
        story.append(Paragraph("AI-Powered Public Financial Analysis & Ripple-Effect Prediction System", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=2, spaceAfter=10))

        # Metadata Header Bar
        org_name = org_data.get("name", "Target Organisation")
        country = org_data.get("country", "Global")
        industry = org_data.get("industry", "Enterprise")
        ticker = org_data.get("ticker", "N/A")
        exchange = org_data.get("stock_exchange", "N/A")
        gen_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        meta_data = [
            [
                Paragraph(f"<b>Target Organisation:</b> {html.escape(str(org_name))}", body_style),
                Paragraph(f"<b>Jurisdiction:</b> {html.escape(str(country))}", body_style)
            ],
            [
                Paragraph(f"<b>Industry:</b> {html.escape(str(industry))}", body_style),
                Paragraph(f"<b>Ticker / Exchange:</b> {html.escape(str(ticker))} ({html.escape(str(exchange))})", body_style)
            ],
            [
                Paragraph(f"<b>Generated On:</b> {gen_time}", body_style),
                Paragraph(f"<b>Evaluation Engine:</b> Python NetworkX + NVIDIA Nemotron", body_style)
            ]
        ]
        meta_table = Table(meta_data, colWidths=[270, 270])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), c_light),
            ('BOX', (0, 0), (-1, -1), 0.5, c_border),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 10))

        # Section 1: Baseline Disclosed Financials
        story.append(Paragraph("1. Verified Public Financial Disclosures", h2_style))
        fin_rows = [["Metric", "Reported Value", "Period", "Status", "Source"]]
        for r in financial_records[:10]:
            val = r.get("value")
            val_str = f"{val:,.2f} {r.get('currency', 'USD')}" if val is not None else "N/A"
            fin_rows.append([
                r.get("metric_name", ""),
                val_str,
                r.get("period", "N/A"),
                r.get("status", ""),
                r.get("source_name", "Public Source")[:25]
            ])

        fin_table = Table(fin_rows, colWidths=[120, 100, 75, 115, 130])
        fin_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8.5),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, c_border),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(fin_table)
        story.append(Spacer(1, 10))

        # Section 2: Butterfly Effect Scenario Specification
        init_var = simulation_result.get("initial_variable", "N/A")
        init_change = simulation_result.get("initial_change_pct", 0.0)
        horizon = simulation_result.get("time_horizon", "1 Year")

        story.append(Paragraph("2. Hypothetical Ripple-Effect Scenario", h2_style))
        scenario_desc = (
            f"<b>Perturbation Input:</b> Hypothetical adjustment of <b>{init_change:+.2f}%</b> in <b>{html.escape(str(init_var))}</b>.<br/>"
            f"<b>Simulation Horizon:</b> {html.escape(str(horizon))} | <b>Propagation Model:</b> Matrix-Vector Directed Transmission with Dampening."
        )
        story.append(Paragraph(scenario_desc, body_style))

        # Section 3: Simulation Results Table
        story.append(Paragraph("3. Multi-Order Ripple Propagation Outcomes", h2_style))
        var_results = simulation_result.get("variable_results", {})
        sim_rows = [["Financial Variable", "Initial Shock", "Order-1 Direct", "Cumulative Delta", "Projected Value"]]
        for var, res in var_results.items():
            base_val = res.get("baseline_value")
            sim_val = res.get("simulated_value")
            val_display = f"{sim_val:,.1f}" if sim_val is not None else "Indexed Scale"

            sim_rows.append([
                var,
                f"{res.get('initial_delta_pct', 0.0):+.2f}%",
                f"{res.get('step1_direct_pct', 0.0):+.2f}%",
                f"{res.get('cumulative_delta_pct', 0.0):+.2f}%",
                val_display
            ])

        sim_table = Table(sim_rows, colWidths=[130, 85, 95, 105, 125])
        sim_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), c_primary),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8.5),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, c_border),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(sim_table)
        story.append(Spacer(1, 10))

        # Section 4: AI Insights and Interpretations
        story.append(Paragraph("4. NVIDIA Nemotron AI Insights & Decision Analysis", h2_style))
        for line in ai_analysis_text.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith("### "):
                header_text = line.replace("### ", "").strip()
                story.append(Paragraph(f"<b>{html.escape(header_text)}</b>", h2_style))
            elif line.startswith("## "):
                header_text = line.replace("## ", "").strip()
                story.append(Paragraph(f"<b>{html.escape(header_text)}</b>", h2_style))
            else:
                formatted_line = format_markdown_for_reportlab(line)
                story.append(Paragraph(formatted_line, body_style))

        # Section 5: Assumptions & Governance Disclaimers
        story.append(Spacer(1, 10))
        story.append(Paragraph("5. Model Assumptions, Uncertainty & Limitations", h2_style))
        assumptions = simulation_result.get("assumptions", [])
        for a in assumptions:
            story.append(Paragraph(f"• {html.escape(str(a))}", body_style))

        story.append(Spacer(1, 6))
        disclaimer = (
            "<b>ACADEMIC RESEARCH DISCLAIMER:</b> This report was generated by an academic simulation system "
            "for demonstration and educational purposes. Hypothetical scenarios must never be construed as "
            "official company disclosures, strategic guidance, or investment advice."
        )
        story.append(Paragraph(disclaimer, ParagraphStyle("Disc", parent=body_style, fontSize=8, textColor=colors.gray)))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

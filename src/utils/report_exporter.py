"""Report Export — Generate PDF and CSV diagnosis reports."""

import csv
import io
import os
from datetime import datetime
from pathlib import Path
from typing import Any


def generate_csv_report(result: dict) -> bytes:
    """Generate CSV report from diagnosis result."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(["Multi-Agent AI Health Diagnostic Report"])
    writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
    writer.writerow([])

    # Input
    writer.writerow(["INPUT DATA"])
    writer.writerow(["Symptom Description", result.get("symptom_input", "N/A")])
    writer.writerow(["Age", result.get("age", "N/A")])
    writer.writerow(["Gender", result.get("gender", "N/A")])
    writer.writerow(["BMI", result.get("bmi", "N/A")])
    writer.writerow([])

    # Severity
    writer.writerow(["SEVERITY ASSESSMENT"])
    writer.writerow(["Severity Level", result.get("severity", "N/A")])
    writer.writerow(["Action", result.get("severity_action", "N/A")])
    writer.writerow([])

    # Diagnoses
    writer.writerow(["DIAGNOSES"])
    writer.writerow(["Condition", "Confidence", "ICD-10", "Rationale"])
    diagnoses = result.get("diagnosis", [])
    for d in diagnoses:
        writer.writerow([
            d.get("condition", "Unknown"),
            f"{d.get('confidence', 0) * 100:.0f}%",
            d.get("icd10_code", ""),
            d.get("rationale", ""),
        ])
    writer.writerow([])

    # Red Flags
    red_flags = result.get("red_flags", [])
    if red_flags:
        writer.writerow(["RED FLAGS"])
        for i, flag in enumerate(red_flags, 1):
            writer.writerow([f"{i}. {flag}"])
        writer.writerow([])

    # Symptoms
    writer.writerow(["SYMPTOMS DETECTED"])
    symptoms = result.get("symptoms", [])
    for s in symptoms:
        writer.writerow([s.get("symptom", ""), s.get("category", "")])
    writer.writerow([])

    # Confidence Breakdown
    confidence = result.get("confidence", {})
    breakdown = confidence.get("breakdown", {})
    if breakdown:
        writer.writerow(["CONFIDENCE BREAKDOWN"])
        for agent, score in breakdown.items():
            writer.writerow([agent, f"{score * 100:.0f}%"])
        writer.writerow([])

    # Recommendations
    writer.writerow(["RECOMMENDATIONS"])
    for i, rec in enumerate(result.get("recommendations", []), 1):
        writer.writerow([f"{i}. {rec}"])
    writer.writerow([])

    # Explanation
    writer.writerow(["AI ANALYSIS SUMMARY"])
    writer.writerow([result.get("explanation", "N/A")])
    writer.writerow([])

    if result.get("patient_explanation"):
        writer.writerow(["WHAT THIS MEANS FOR YOU"])
        writer.writerow([result.get("patient_explanation", "")])
        writer.writerow([])

    # Disclaimer
    writer.writerow(["DISCLAIMER"])
    writer.writerow([result.get("disclaimer", "")])

    return output.getvalue().encode("utf-8")


def generate_pdf_report(result: dict) -> bytes:
    """Generate PDF report from diagnosis result.

    Falls back to HTML-based PDF if reportlab is unavailable.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm, inch
        from reportlab.lib.colors import HexColor, black, white
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
            PageBreak,
            KeepTogether,
        )
        from reportlab.lib import colors
        from io import BytesIO

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=25 * mm,
            leftMargin=25 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        )

        styles = getSampleStyleSheet()

        # Custom styles
        styles.add(ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontSize=18,
            textColor=HexColor("#1E40AF"),
            spaceAfter=2 * mm,
            alignment=TA_CENTER,
        ))
        styles.add(ParagraphStyle(
            name="SectionHeader",
            parent=styles["Heading2"],
            fontSize=13,
            textColor=HexColor("#1E40AF"),
            spaceBefore=6 * mm,
            spaceAfter=3 * mm,
            borderWidth=1,
            borderColor=HexColor("#E5E7EB"),
            borderPadding=3,
            borderRadius=2,
        ))
        styles.add(ParagraphStyle(
            name="BodyTextCustom",
            parent=styles["BodyText"],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
        ))
        styles.add(ParagraphStyle(
            name="SmallCaption",
            parent=styles["BodyText"],
            fontSize=8,
            textColor=HexColor("#6B7280"),
        ))

        story = []

        # Title
        story.append(Paragraph("Multi-Agent AI Health Diagnostic Report", styles["ReportTitle"]))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
            styles["SmallCaption"],
        ))
        story.append(Paragraph(
            "Clinical decision support only — requires review by a licensed clinician.",
            styles["SmallCaption"],
        ))
        story.append(Spacer(0, 4 * mm))

        # Patient info
        story.append(Paragraph("Patient Information", styles["SectionHeader"]))
        info_data = [
            ["Symptom Description", result.get("symptom_input", "N/A")],
            ["Age", str(result.get("age", "N/A"))],
            ["Gender", str(result.get("gender", "N/A"))],
            ["BMI", str(result.get("bmi", "N/A"))],
        ]
        info_table = Table(info_data, colWidths=[50 * mm, 120 * mm])
        info_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), HexColor("#F3F4F6")),
            ("TEXTCOLOR", (0, 0), (-1, -1), black),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (0, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#D1D5DB")),
        ]))
        story.append(info_table)

        # Severity
        severity = result.get("severity", "N/A")
        sev_color = {"mild": "#28A745", "moderate": "#FFC107", "severe": "#DC3545", "critical": "#721C24"}.get(severity, "#6C757D")
        story.append(Paragraph("Severity Assessment", styles["SectionHeader"]))
        sev_data = [[f"SEVERITY: {severity.upper()}", result.get("severity_action", "N/A")]]
        sev_table = Table(sev_data, colWidths=[85 * mm, 85 * mm])
        sev_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), HexColor(sev_color)),
            ("TEXTCOLOR", (0, 0), (0, 0), white),
            ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#D1D5DB")),
        ]))
        story.append(sev_table)

        # Diagnoses
        story.append(Paragraph("Possible Conditions", styles["SectionHeader"]))
        diagnoses = result.get("diagnosis", [])
        if diagnoses:
            diag_header = ["Condition", "Confidence", "ICD-10", "Rationale"]
            diag_data = [diag_header]
            for d in diagnoses:
                diag_data.append([
                    d.get("condition", "Unknown"),
                    f"{d.get('confidence', 0) * 100:.0f}%",
                    d.get("icd10_code", ""),
                    d.get("rationale", ""),
                ])
            diag_table = Table(diag_data, colWidths=[35 * mm, 25 * mm, 25 * mm, 85 * mm])
            diag_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1E40AF")),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 1), (1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#D1D5DB")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, HexColor("#F9FAFB")]),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(diag_table)

        triage_entropy = result.get("triage_entropy")
        if triage_entropy is not None:
            story.append(Paragraph("DEMAT Triage", styles["SectionHeader"]))
            story.append(Paragraph(
                f"Diagnostic entropy: {float(triage_entropy):.2f} bits",
                styles["BodyTextCustom"],
            ))

        execution_trace = result.get("execution_trace", [])
        if execution_trace:
            story.append(Paragraph("Agent Execution Trace", styles["SectionHeader"]))
            trace_data = [["Agent", "Status", "Elapsed", "Summary"]]
            for event in execution_trace:
                if event.get("type") != "agent":
                    continue
                trace_data.append([
                    str(event.get("agent") or event.get("node") or "Agent"),
                    str(event.get("status", "")),
                    f"{float(event.get('elapsed_ms') or 0):.0f} ms",
                    str(event.get("summary", "")),
                ])
            if len(trace_data) > 1:
                trace_table = Table(trace_data, colWidths=[34 * mm, 22 * mm, 22 * mm, 92 * mm], repeatRows=1)
                trace_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1E40AF")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#D1D5DB")),
                ]))
                story.append(trace_table)

        # Red flags
        red_flags = result.get("red_flags", [])
        if red_flags:
            story.append(Paragraph("Red Flags", styles["SectionHeader"]))
            for flag in red_flags:
                story.append(Paragraph(f"• {flag}", styles["BodyTextCustom"]))

        # Symptoms
        symptoms = result.get("symptoms", [])
        if symptoms:
            story.append(Paragraph("Symptoms Detected", styles["SectionHeader"]))
            symptoms_text = ", ".join(s.get("symptom", "") for s in symptoms)
            story.append(Paragraph(symptoms_text, styles["BodyTextCustom"]))

        # Confidence breakdown
        confidence = result.get("confidence", {})
        breakdown = confidence.get("breakdown", {})
        if breakdown:
            story.append(Paragraph("Agent Confidence Breakdown", styles["SectionHeader"]))
            conf_data = [["Agent", "Score"]]
            for agent, score in breakdown.items():
                conf_data.append([agent, f"{score * 100:.0f}%"])
            conf_table = Table(conf_data, colWidths=[85 * mm, 85 * mm])
            conf_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1E40AF")),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (1, 1), (1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#D1D5DB")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, HexColor("#F9FAFB")]),
            ]))
            story.append(conf_table)

        # Recommendations
        recommendations = result.get("recommendations", [])
        if recommendations:
            story.append(Paragraph("Recommendations", styles["SectionHeader"]))
            for i, rec in enumerate(recommendations, 1):
                story.append(Paragraph(f"{i}. {rec}", styles["BodyTextCustom"]))

        # Explanation
        explanation = result.get("explanation", "")
        if explanation:
            story.append(Paragraph("AI Analysis Summary", styles["SectionHeader"]))
            story.append(Paragraph(explanation, styles["BodyTextCustom"]))

        patient_exp = result.get("patient_explanation", "")
        if patient_exp:
            story.append(Paragraph("What This Means for You", styles["SectionHeader"]))
            story.append(Paragraph(patient_exp, styles["BodyTextCustom"]))

        # Keep the disclaimer in a page footer so it cannot strand a mostly
        # empty trailing page when the report content ends near a page break.
        disclaimer = result.get("disclaimer", "") or "AegisMed is clinical decision support and does not replace independent clinical judgment."

        def draw_footer(canvas, _doc):
            canvas.saveState()
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(HexColor("#6B7280"))
            canvas.drawString(25 * mm, 11 * mm, disclaimer[:220])
            canvas.restoreState()

        doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)
        return buffer.getvalue()

    except ImportError:
        # Fallback: generate simple text report
        return generate_text_report(result).encode("utf-8")


def generate_text_report(result: dict) -> str:
    """Generate plain text report (fallback if reportlab unavailable)."""
    lines = [
        "=" * 60,
        "MULTI-AGENT AI HEALTH DIAGNOSTIC REPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 60,
        "",
        "PATIENT INFORMATION",
        "-" * 40,
        f"Symptoms: {result.get('symptom_input', 'N/A')}",
        f"Age: {result.get('age', 'N/A')}",
        f"Gender: {result.get('gender', 'N/A')}",
        f"BMI: {result.get('bmi', 'N/A')}",
        "",
        "SEVERITY ASSESSMENT",
        "-" * 40,
        f"Level: {result.get('severity', 'N/A')}",
        f"Action: {result.get('severity_action', 'N/A')}",
        "",
        "POSSIBLE CONDITIONS",
        "-" * 40,
    ]

    for d in result.get("diagnosis", []):
        lines.append(f"• {d.get('condition', 'Unknown')} ({d.get('confidence', 0)*100:.0f}%)")
        if d.get("icd10_code"):
            lines.append(f"  ICD-10: {d['icd10_code']}")
        if d.get("rationale"):
            lines.append(f"  {d['rationale']}")

    red_flags = result.get("red_flags", [])
    if red_flags:
        lines.extend(["", "RED FLAGS", "-" * 40])
        for flag in red_flags:
            lines.append(f"⚠️  {flag}")

    recommendations = result.get("recommendations", [])
    if recommendations:
        lines.extend(["", "RECOMMENDATIONS", "-" * 40])
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"{i}. {rec}")

    lines.extend([
        "",
        "AI ANALYSIS SUMMARY",
        "-" * 40,
        result.get("explanation", "N/A"),
        "",
        "=" * 60,
        result.get("disclaimer", ""),
        "=" * 60,
    ])

    return "\n".join(lines)

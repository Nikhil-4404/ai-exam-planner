from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.models import PlannerRequest, StrategyResponse


def _draw_wrapped_lines(pdf: canvas.Canvas, text: str, x: int, y: int, max_width: int, line_height: int) -> int:
    words = text.split()
    current = []
    current_width = 0

    for word in words:
        trial = " ".join([*current, word])
        width = pdf.stringWidth(trial, "Helvetica", 11)
        if width <= max_width:
            current = [*current, word]
            current_width = width
            continue

        pdf.drawString(x, y, " ".join(current))
        y -= line_height
        current = [word]
        current_width = pdf.stringWidth(word, "Helvetica", 11)

    if current:
        pdf.drawString(x, y, " ".join(current))
        y -= line_height

    return y


def build_plan_pdf(title: str, payload: PlannerRequest, strategy: StrategyResponse) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    x = 48
    y = height - 54
    max_width = int(width - 96)

    pdf.setTitle(title)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(x, y, title)
    y -= 28

    pdf.setFont("Helvetica", 11)
    meta_lines = [
        f"Exam: {payload.exam_name}",
        f"Target date: {payload.target_date}",
        f"Weekly hours: {payload.weekly_hours}",
        f"Target score: {payload.target_score}%",
        f"Study style: {payload.study_style}",
    ]
    for line in meta_lines:
        pdf.drawString(x, y, line)
        y -= 16

    sections = [
        ("Summary", [strategy.summary]),
        ("Focus subjects", strategy.focus_subjects),
        ("Next steps", strategy.next_steps),
        ("Weekly plan", strategy.weekly_plan),
        ("Risk alerts", strategy.risk_alerts),
    ]

    for heading, items in sections:
        if y < 120:
            pdf.showPage()
            y = height - 54

        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(x, y, heading)
        y -= 18
        pdf.setFont("Helvetica", 11)

        for item in items:
            if y < 80:
                pdf.showPage()
                y = height - 54
                pdf.setFont("Helvetica", 11)

            bullet_text = item if heading == "Summary" else f"- {item}"
            y = _draw_wrapped_lines(pdf, bullet_text, x, y, max_width, 14)
            y -= 4

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()

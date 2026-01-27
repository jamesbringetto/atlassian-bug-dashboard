#!/usr/bin/env python3
"""Generate a PDF one-pager with setup instructions for Atlassian Bug Tracker."""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def create_setup_guide():
    doc = SimpleDocTemplate(
        "Atlassian_Bug_Tracker_Setup_Guide.pdf",
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=22,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=colors.HexColor("#0052CC"),
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.gray,
    )

    section_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=12,
        spaceBefore=12,
        spaceAfter=6,
        textColor=colors.HexColor("#172B4D"),
        borderPadding=(0, 0, 3, 0),
    )

    step_style = ParagraphStyle(
        "StepStyle",
        parent=styles["Normal"],
        fontSize=9,
        spaceAfter=3,
        leftIndent=15,
    )

    code_style = ParagraphStyle(
        "CodeStyle",
        parent=styles["Code"],
        fontSize=8,
        fontName="Courier",
        backColor=colors.HexColor("#F4F5F7"),
        borderPadding=6,
        spaceAfter=6,
        leftIndent=15,
    )

    note_style = ParagraphStyle(
        "NoteStyle",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#6B778C"),
        leftIndent=15,
        spaceAfter=6,
    )

    story = []

    # Title
    story.append(Paragraph("Atlassian Bug Tracker", title_style))
    story.append(Paragraph("Local Development Setup Guide", subtitle_style))

    # Prerequisites
    story.append(Paragraph("Prerequisites", section_style))
    prereqs = [
        "• Python 3.11+ with Poetry installed",
        "• Node.js 18+ with npm",
        "• Docker (for PostgreSQL database)",
        "• Anthropic API key (for AI triage features)",
    ]
    for prereq in prereqs:
        story.append(Paragraph(prereq, step_style))
    story.append(Spacer(1, 8))

    # Step 1: Database
    story.append(Paragraph("Step 1: Start PostgreSQL Database", section_style))
    story.append(Paragraph("Run the following command to start PostgreSQL in Docker:", step_style))
    db_cmd = """docker run --name postgres-atlassian \\<br/>
&nbsp;&nbsp;-e POSTGRES_USER=atlassian_user \\<br/>
&nbsp;&nbsp;-e POSTGRES_PASSWORD=atlassian_pass \\<br/>
&nbsp;&nbsp;-e POSTGRES_DB=atlassian_bugs \\<br/>
&nbsp;&nbsp;-p 5432:5432 -d postgres:latest"""
    story.append(Paragraph(db_cmd, code_style))

    # Step 2: Backend Setup
    story.append(Paragraph("Step 2: Install Backend Dependencies", section_style))
    story.append(Paragraph("cd backend && poetry install --no-root", code_style))

    # Step 3: Initialize Database
    story.append(Paragraph("Step 3: Initialize the Database", section_style))
    story.append(Paragraph("poetry run python scripts/init_db.py", code_style))

    # Step 4: Environment Variables
    story.append(Paragraph("Step 4: Configure Environment Variables", section_style))
    story.append(Paragraph("Create <b>backend/.env</b> file with:", step_style))
    env_vars = """DATABASE_URL=postgresql://atlassian_user:atlassian_pass@localhost:5432/atlassian_bugs<br/>
ANTHROPIC_API_KEY=sk-ant-your-key-here<br/>
ALLOWED_ORIGINS=http://localhost:3000"""
    story.append(Paragraph(env_vars, code_style))
    story.append(Paragraph("Get your API key from: https://console.anthropic.com", note_style))

    # Step 5: Start Backend
    story.append(Paragraph("Step 5: Start the Backend Server", section_style))
    story.append(Paragraph("poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000", code_style))
    story.append(Paragraph("API will be available at: http://localhost:8000", note_style))

    # Step 6: Frontend Setup
    story.append(Paragraph("Step 6: Install Frontend Dependencies (new terminal)", section_style))
    story.append(Paragraph("cd .. && npm install", code_style))

    # Step 7: Update API URL
    story.append(Paragraph("Step 7: Update Frontend API URL", section_style))
    story.append(Paragraph("Edit <b>src/lib/api.ts</b> and change API_BASE_URL to:", step_style))
    story.append(Paragraph("http://localhost:8000/api", code_style))

    # Step 8: Start Frontend
    story.append(Paragraph("Step 8: Start the Frontend Server", section_style))
    story.append(Paragraph("npm run dev", code_style))
    story.append(Paragraph("Dashboard will be available at: http://localhost:3000", note_style))

    # Step 9: Sync Data
    story.append(Paragraph("Step 9: Load Bug Data (optional)", section_style))
    story.append(Paragraph('curl -X POST "http://localhost:8000/api/bugs/sync?auto_triage=true"', code_style))

    story.append(Spacer(1, 12))

    # Access Points Table
    story.append(Paragraph("Access Points Summary", section_style))
    table_data = [
        ["Service", "URL", "Purpose"],
        ["Dashboard", "http://localhost:3000", "Main Bug Tracker UI"],
        ["API Server", "http://localhost:8000", "REST API endpoints"],
        ["API Docs", "http://localhost:8000/docs", "Interactive Swagger docs"],
    ]
    table = Table(table_data, colWidths=[1.5 * inch, 2.5 * inch, 2.5 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0052CC")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F4F5F7")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DFE1E6")),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
                ("TOPPADDING", (0, 1), (-1, -1), 6),
            ]
        )
    )
    story.append(table)

    story.append(Spacer(1, 12))

    # Quick Start Commands
    story.append(Paragraph("Quick Reference - All Commands", section_style))
    quick_cmds = """# Terminal 1 - Database &amp; Backend<br/>
docker run --name postgres-atlassian -e POSTGRES_USER=atlassian_user -e POSTGRES_PASSWORD=atlassian_pass -e POSTGRES_DB=atlassian_bugs -p 5432:5432 -d postgres:latest<br/>
cd backend &amp;&amp; poetry install --no-root &amp;&amp; poetry run python scripts/init_db.py<br/>
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000<br/><br/>
# Terminal 2 - Frontend<br/>
npm install &amp;&amp; npm run dev"""
    story.append(Paragraph(quick_cmds, code_style))

    doc.build(story)
    print("✓ PDF created: Atlassian_Bug_Tracker_Setup_Guide.pdf")


if __name__ == "__main__":
    create_setup_guide()

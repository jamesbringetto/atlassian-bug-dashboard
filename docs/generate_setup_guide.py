#!/usr/bin/env python3
"""Generate a PDF one-pager setup guide for the Atlassian Bug Tracker."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Colors
ATLASSIAN_BLUE = HexColor("#0052CC")
DARK_GRAY = HexColor("#172B4D")
LIGHT_GRAY = HexColor("#F4F5F7")
WHITE = HexColor("#FFFFFF")

def create_setup_guide():
    """Create the PDF setup guide."""
    doc = SimpleDocTemplate(
        "atlassian_bug_tracker_setup_guide.pdf",
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.4*inch,
        bottomMargin=0.4*inch
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=ATLASSIAN_BLUE,
        alignment=TA_CENTER,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=DARK_GRAY,
        alignment=TA_CENTER,
        spaceAfter=12
    )

    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=WHITE,
        spaceBefore=8,
        spaceAfter=4,
        fontName='Helvetica-Bold',
        backColor=ATLASSIAN_BLUE,
        leftIndent=6,
        rightIndent=6,
        leading=18
    )

    step_style = ParagraphStyle(
        'Step',
        parent=styles['Normal'],
        fontSize=9,
        textColor=DARK_GRAY,
        spaceBefore=2,
        spaceAfter=2,
        leftIndent=10
    )

    code_style = ParagraphStyle(
        'Code',
        parent=styles['Normal'],
        fontSize=8,
        fontName='Courier',
        textColor=DARK_GRAY,
        backColor=LIGHT_GRAY,
        leftIndent=20,
        rightIndent=10,
        spaceBefore=2,
        spaceAfter=4,
        leading=11
    )

    note_style = ParagraphStyle(
        'Note',
        parent=styles['Normal'],
        fontSize=8,
        textColor=HexColor("#666666"),
        leftIndent=10,
        fontName='Helvetica-Oblique'
    )

    story = []

    # Title
    story.append(Paragraph("Atlassian Bug Tracker", title_style))
    story.append(Paragraph("Quick Start Setup Guide", subtitle_style))
    story.append(Spacer(1, 6))

    # Prerequisites
    story.append(Paragraph("PREREQUISITES", section_style))
    story.append(Spacer(1, 4))
    prereq_data = [
        ["Requirement", "Version", "Install Command"],
        ["Python", "3.11+", "pyenv install 3.11"],
        ["Node.js", "20+", "nvm install 20"],
        ["Docker Desktop", "Latest", "docker.com/products/docker-desktop"],
        ["Poetry", "Latest", "curl -sSL install.python-poetry.org | python3 -"],
    ]
    prereq_table = Table(prereq_data, colWidths=[1.8*inch, 1*inch, 4.2*inch])
    prereq_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), ATLASSIAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 1), (-1, -1), LIGHT_GRAY),
        ('GRID', (0, 0), (-1, -1), 0.5, DARK_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(prereq_table)
    story.append(Spacer(1, 8))

    # Step 1: Start Database
    story.append(Paragraph("STEP 1: START POSTGRESQL DATABASE", section_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Start the PostgreSQL database container using Docker Compose:", step_style))
    story.append(Paragraph("cd ~/atlassian-bug-dashboard<br/>docker-compose up -d postgres", code_style))
    story.append(Paragraph("Note: Wait a few seconds for the database to initialize before proceeding.", note_style))
    story.append(Spacer(1, 6))

    # Step 2: Backend Setup
    story.append(Paragraph("STEP 2: SET UP BACKEND (API SERVER)", section_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("a) Install Python dependencies:", step_style))
    story.append(Paragraph("cd backend<br/>poetry install --no-root", code_style))
    story.append(Paragraph("b) Create environment file (.env in backend/ directory):", step_style))
    story.append(Paragraph(
        "DATABASE_URL=postgresql://atlassian_user:atlassian_pass@localhost:5432/atlassian_bugs<br/>"
        "ANTHROPIC_API_KEY=sk-ant-...  # Optional: for AI triage<br/>"
        "ALLOWED_ORIGINS=http://localhost:3000",
        code_style
    ))
    story.append(Paragraph("c) Initialize the database:", step_style))
    story.append(Paragraph("poetry run python scripts/init_db.py", code_style))
    story.append(Paragraph("d) Start the API server:", step_style))
    story.append(Paragraph("poetry run uvicorn app.main:app --reload", code_style))
    story.append(Paragraph("Backend will be available at: http://localhost:8000", note_style))
    story.append(Spacer(1, 6))

    # Step 3: Frontend Setup
    story.append(Paragraph("STEP 3: SET UP FRONTEND (WEB UI)", section_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Open a new terminal window and run:", step_style))
    story.append(Paragraph("cd ~/atlassian-bug-dashboard<br/>npm install<br/>npm run dev", code_style))
    story.append(Paragraph("Frontend will be available at: http://localhost:3000", note_style))
    story.append(Spacer(1, 6))

    # Step 4: Load Data
    story.append(Paragraph("STEP 4: SYNC BUG DATA FROM JIRA", section_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Trigger a data sync to load bugs from Atlassian Jira:", step_style))
    story.append(Paragraph("curl -X POST \"http://localhost:8000/api/bugs/sync?auto_triage=true\"", code_style))
    story.append(Paragraph("Or visit http://localhost:8000/docs and use the Swagger UI.", note_style))
    story.append(Spacer(1, 6))

    # Access Points
    story.append(Paragraph("ACCESS POINTS", section_style))
    story.append(Spacer(1, 4))
    access_data = [
        ["Service", "URL", "Description"],
        ["Dashboard", "http://localhost:3000", "Main bug tracker dashboard"],
        ["Bug List", "http://localhost:3000/bugs", "Detailed bug listing page"],
        ["API Docs", "http://localhost:8000/docs", "Swagger UI for API testing"],
        ["Health Check", "http://localhost:8000/api/health", "API health status endpoint"],
    ]
    access_table = Table(access_data, colWidths=[1.5*inch, 2.5*inch, 3*inch])
    access_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), ATLASSIAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 1), (-1, -1), LIGHT_GRAY),
        ('GRID', (0, 0), (-1, -1), 0.5, DARK_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(access_table)
    story.append(Spacer(1, 8))

    # Quick Troubleshooting
    story.append(Paragraph("TROUBLESHOOTING", section_style))
    story.append(Spacer(1, 4))
    trouble_data = [
        ["Issue", "Solution"],
        ["Database connection failed", "Ensure Docker is running: docker ps | grep postgres"],
        ["Port 3000 already in use", "Kill existing process: lsof -ti:3000 | xargs kill -9"],
        ["Port 8000 already in use", "Kill existing process: lsof -ti:8000 | xargs kill -9"],
        ["Poetry not found", "Ensure Poetry is in PATH: export PATH=\"$HOME/.local/bin:$PATH\""],
        ["npm: command not found", "Install Node.js via nvm: nvm install 20 && nvm use 20"],
    ]
    trouble_table = Table(trouble_data, colWidths=[2.5*inch, 4.5*inch])
    trouble_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), ATLASSIAN_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 1), (-1, -1), LIGHT_GRAY),
        ('GRID', (0, 0), (-1, -1), 0.5, DARK_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(trouble_table)

    # Build PDF
    doc.build(story)
    print("PDF created: atlassian_bug_tracker_setup_guide.pdf")

if __name__ == "__main__":
    create_setup_guide()

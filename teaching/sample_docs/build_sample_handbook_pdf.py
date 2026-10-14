#!/usr/bin/env python3
"""Generate a sample multi-section PDF for Azure Blob + AI Search RAG demos."""

from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

OUT = Path(__file__).resolve().parent / "Acme_Employee_Handbook.pdf"

TEAL = HexColor("#0c7c7c")
INK = HexColor("#141e2a")
MUTED = HexColor("#5a6675")


def build() -> Path:
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            parent=styles["Title"],
            fontSize=28,
            textColor=INK,
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverSub",
            parent=styles["Normal"],
            fontSize=14,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H1Doc",
            parent=styles["Heading1"],
            fontSize=16,
            textColor=TEAL,
            spaceBefore=16,
            spaceAfter=10,
            fontName="Helvetica-Bold",
        )
    )
    styles.add(
        ParagraphStyle(
            name="H2Doc",
            parent=styles["Heading2"],
            fontSize=13,
            textColor=INK,
            spaceBefore=12,
            spaceAfter=6,
            fontName="Helvetica-Bold",
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyDoc",
            parent=styles["Normal"],
            fontSize=10.5,
            textColor=INK,
            leading=15,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Meta",
            parent=styles["Normal"],
            fontSize=9,
            textColor=MUTED,
            spaceAfter=4,
        )
    )

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=letter,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title="Acme Corp Employee Handbook",
        author="Acme Corp HR",
    )

    story = []

    story.append(Spacer(1, 1.8 * inch))
    story.append(Paragraph("ACME CORPORATION", styles["CoverSub"]))
    story.append(Paragraph("Employee Handbook", styles["CoverTitle"]))
    story.append(
        HRFlowable(
            width="60%",
            thickness=2,
            color=TEAL,
            spaceBefore=8,
            spaceAfter=16,
            hAlign="CENTER",
        )
    )
    story.append(Paragraph("Sample document for Azure AI Search RAG demos", styles["CoverSub"]))
    story.append(Paragraph("Version 2026.1  |  Effective: January 1, 2026", styles["CoverSub"]))
    story.append(Paragraph("Policy IDs: RW-12, BP-04, SEC-03", styles["CoverSub"]))
    story.append(Spacer(1, 0.6 * inch))
    story.append(
        Paragraph(
            "This handbook summarizes selected company policies for remote work, benefits, "
            "and information security. Use it as test content when indexing PDFs from Azure "
            "Blob Storage into Azure AI Search.",
            styles["BodyDoc"],
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("1. Introduction", styles["H1Doc"]))
    story.append(
        Paragraph(
            "Welcome to Acme Corporation. This handbook helps employees find clear answers "
            "about workplace policies. It is written as realistic RAG sample data: multiple "
            "topics, headings, policy IDs, and fact-dense paragraphs so you can test chunking, "
            "embeddings, hybrid search, and metadata filters.",
            styles["BodyDoc"],
        )
    )
    story.append(
        Paragraph(
            "Questions this document can answer in a RAG demo include: How many remote days "
            "are allowed? Who approves remote schedules? What is the equipment stipend? When "
            "does vision coverage start? Is security training required before VPN access?",
            styles["BodyDoc"],
        )
    )

    story.append(Paragraph("2. Remote Work Policy (RW-12)", styles["H1Doc"]))
    story.append(
        Paragraph(
            "Policy RW-12 governs remote and hybrid work for full-time Acme employees in the "
            "United States. Managers remain responsible for team coverage, customer response "
            "times, and performance standards whether employees work onsite or remotely.",
            styles["BodyDoc"],
        )
    )

    story.append(Paragraph("2.1 Eligibility and schedule", styles["H2Doc"]))
    story.append(
        Paragraph(
            "Employees may work remotely up to three days per week. The remaining workdays "
            "must be spent at an approved Acme office or customer site unless an exception is "
            "documented in writing. Remote days should be scheduled in advance so teams can "
            "plan collaboration and meetings.",
            styles["BodyDoc"],
        )
    )
    story.append(
        Paragraph(
            "Managers must approve remote schedules by Friday of the preceding week. "
            "Last-minute remote requests may be denied if they conflict with onsite duties, "
            "client visits, or team ceremonies. Temporary full-remote arrangements require HR "
            "and department director approval.",
            styles["BodyDoc"],
        )
    )

    story.append(Paragraph("2.2 Equipment stipend", styles["H2Doc"]))
    story.append(
        Paragraph(
            "Equipment stipends are $500 per year for eligible full-time employees. The "
            "stipend may be used for ergonomic chairs, monitors, keyboards, headsets, or "
            "home-office networking equipment that supports productive remote work. Unused "
            "stipend balances do not roll over to the next calendar year.",
            styles["BodyDoc"],
        )
    )
    story.append(
        Paragraph(
            "Receipts must be submitted through the Contoso Expense portal within 45 days of "
            "purchase. Acme-owned laptops and phones remain company property and are not "
            "purchased with the stipend.",
            styles["BodyDoc"],
        )
    )

    story.append(Paragraph("2.3 Availability and communication", styles["H2Doc"]))
    story.append(
        Paragraph(
            "While remote, employees must remain reachable on Teams during core hours of "
            "10:00 AM to 3:00 PM local time unless an alternate arrangement is approved. "
            "Status messages should indicate meeting blocks and focus time. Customer-facing "
            "roles may have stricter availability rules defined by their manager.",
            styles["BodyDoc"],
        )
    )

    story.append(PageBreak())
    story.append(Paragraph("3. Benefits Policy (BP-04)", styles["H1Doc"]))
    story.append(
        Paragraph(
            "Policy BP-04 describes dental and vision benefits under the Acme Plan. Benefits "
            "enrollment is managed by HR during open enrollment and qualifying life events. "
            "This section is intentionally dense so RAG systems can be tested on multi-fact "
            "paragraphs and proposition-style questions.",
            styles["BodyDoc"],
        )
    )

    story.append(Paragraph("3.1 Dental and vision waiting periods", styles["H2Doc"]))
    story.append(
        Paragraph(
            "The Acme Plan covers dental after a six-month waiting period and vision after "
            "ninety days for full-time staff. Part-time employees are eligible for vision "
            "only after one hundred eighty days. Dental coverage is not available to "
            "part-time employees.",
            styles["BodyDoc"],
        )
    )
    story.append(
        Paragraph(
            "Waiting periods begin on the employee's benefits-effective date recorded in "
            "Workday. Coverage start dates are calculated in calendar days. Employees "
            "transferring from part-time to full-time status may need a new waiting period "
            "for dental unless HR grants credit for prior continuous service.",
            styles["BodyDoc"],
        )
    )

    story.append(Paragraph("3.2 Dependents and documentation", styles["H2Doc"]))
    story.append(
        Paragraph(
            "Eligible dependents include a legal spouse and children under age 26. Proof of "
            "relationship may be requested during enrollment. Dependent coverage begins on "
            "the same date as the employee once waiting periods, if any, are satisfied.",
            styles["BodyDoc"],
        )
    )

    story.append(Paragraph("3.3 How to get help", styles["H2Doc"]))
    story.append(
        Paragraph(
            "For claims questions, contact Acme Benefits Support at benefits@acme.example or "
            "call 1-800-555-0142 on weekdays between 8:00 AM and 6:00 PM Central Time. For "
            "plan documents, open the Benefits Hub on the employee intranet and search for "
            "BP-04.",
            styles["BodyDoc"],
        )
    )

    story.append(Paragraph("4. Information Security Policy (SEC-03)", styles["H1Doc"]))
    story.append(
        Paragraph(
            "Policy SEC-03 protects Acme systems, customer data, and employee accounts. "
            "Violations may result in loss of access, disciplinary action, or termination. "
            "Security requirements apply equally to office and remote workers.",
            styles["BodyDoc"],
        )
    )

    story.append(Paragraph("4.1 Authentication and VPN", styles["H2Doc"]))
    story.append(
        Paragraph(
            "Multi-factor authentication (MFA) is required before VPN access is granted. "
            "Employees must enroll an authenticator app or approved hardware key. SMS-only "
            "MFA is not sufficient for privileged accounts.",
            styles["BodyDoc"],
        )
    )
    story.append(
        Paragraph(
            "Security training is mandatory before VPN access is granted. New hires complete "
            "the Security Essentials course within their first seven calendar days. Annual "
            "refresher training is due each November. Accounts without current training are "
            "automatically blocked from remote access.",
            styles["BodyDoc"],
        )
    )

    story.append(Paragraph("4.2 Devices and remote access", styles["H2Doc"]))
    story.append(
        Paragraph(
            "VPN is permitted only on company-managed devices that meet endpoint protection "
            "baselines. Personal computers may not connect to the corporate VPN. Lost or "
            "stolen devices must be reported to the IT Service Desk within four hours.",
            styles["BodyDoc"],
        )
    )

    story.append(Paragraph("4.3 Offboarding and device wipe", styles["H2Doc"]))
    story.append(
        Paragraph(
            "Upon resignation or termination, IT initiates a remote device wipe for company "
            "laptops and phones. Employees must return badges and hardware within five "
            "business days. Access to email, Teams, and source control is revoked on the last "
            "working day unless Legal requests a litigation hold.",
            styles["BodyDoc"],
        )
    )

    story.append(PageBreak())
    story.append(Paragraph("5. Time Off and Holidays", styles["H1Doc"]))
    story.append(
        Paragraph(
            "Full-time employees accrue paid time off (PTO) at a rate of 6.15 hours per pay "
            "period, which equals approximately twenty days per year. Unused PTO may carry "
            "over up to forty hours into the next year. PTO requests should be submitted at "
            "least two weeks in advance when possible.",
            styles["BodyDoc"],
        )
    )
    story.append(
        Paragraph(
            "Acme observes the following U.S. holidays: New Year's Day, Memorial Day, "
            "Independence Day, Labor Day, Thanksgiving Day, the day after Thanksgiving, and "
            "Christmas Day. Holiday pay rules for part-time staff are described in the "
            "Timekeeping Guide on the intranet.",
            styles["BodyDoc"],
        )
    )

    story.append(Paragraph("6. Frequently Asked Questions", styles["H1Doc"]))
    story.append(Paragraph("Q: How much is the equipment stipend?", styles["H2Doc"]))
    story.append(
        Paragraph(
            "A: The equipment stipend under policy RW-12 is $500 per year for eligible "
            "full-time employees.",
            styles["BodyDoc"],
        )
    )
    story.append(
        Paragraph("Q: When does vision coverage start for full-time staff?", styles["H2Doc"])
    )
    story.append(
        Paragraph(
            "A: Under the Acme Plan (BP-04), vision coverage for full-time staff begins after "
            "a ninety-day waiting period.",
            styles["BodyDoc"],
        )
    )
    story.append(Paragraph("Q: Is security training required before VPN?", styles["H2Doc"]))
    story.append(
        Paragraph(
            "A: Yes. Security training is mandatory before VPN access is granted, and MFA is "
            "also required (SEC-03).",
            styles["BodyDoc"],
        )
    )

    story.append(Spacer(1, 0.3 * inch))
    story.append(HRFlowable(width="100%", thickness=1, color=TEAL, spaceBefore=8, spaceAfter=12))
    story.append(
        Paragraph(
            "End of sample handbook. Document purpose: Azure Blob Storage upload to Azure AI "
            "Search indexer / integrated vectorization for RAG retrieval testing. Not legal "
            "advice; fictional company policies only.",
            styles["Meta"],
        )
    )

    def footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(0.85 * inch, 0.45 * inch, "Acme Corp Employee Handbook - RAG sample")
        canvas.drawRightString(letter[0] - 0.85 * inch, 0.45 * inch, f"Page {doc_.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return OUT


if __name__ == "__main__":
    path = build()
    print(f"Wrote {path} ({path.stat().st_size} bytes)")

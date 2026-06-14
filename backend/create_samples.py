import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

os.makedirs("sample_docs", exist_ok=True)

styles = getSampleStyleSheet()


def make_pdf(filename, title, content_blocks):
    doc = SimpleDocTemplate(f"sample_docs/{filename}", pagesize=letter)
    story = []
    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 20))
    for block in content_blocks:
        if isinstance(block, str):
            story.append(Paragraph(block, styles["Normal"]))
            story.append(Spacer(1, 10))
        else:
            story.append(block)
            story.append(Spacer(1, 10))
    doc.build(story)
    print(f"Created: sample_docs/{filename}")


# 1. Company Financial Report
make_pdf(
    "financial_report_q4.pdf",
    "Q4 2024 Financial Report",
    [
        "Executive Summary",
        "This report presents the financial performance of AcmeCorp for Q4 2024. "
        "Total revenue reached $4.2 million, representing a 18% increase year-over-year. "
        "Operating expenses were $2.8 million, resulting in a net profit of $1.4 million.",

        "Revenue Breakdown by Department:",
        Table(
            [
                ["Department", "Q4 Revenue", "YoY Growth"],
                ["Product Sales", "$2,100,000", "+22%"],
                ["Services", "$1,400,000", "+12%"],
                ["Licensing", "$700,000", "+18%"],
                ["Total", "$4,200,000", "+18%"],
            ],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ])
        ),

        "Key Highlights",
        "1. Product division achieved record sales driven by new enterprise contracts. "
        "2. Services revenue grew steadily due to expansion into three new markets. "
        "3. Operating costs were reduced by 5% through process automation initiatives. "
        "4. Cash reserves stand at $3.1 million providing strong liquidity position.",

        "Outlook for Q1 2025",
        "Management projects continued growth of 15-20% in Q1 2025 based on the current "
        "sales pipeline and signed contracts. Investment in R&D will increase by 30% to "
        "support new product development scheduled for mid-2025 launch.",
    ]
)

# 2. Employee Onboarding Manual
make_pdf(
    "employee_onboarding_manual.pdf",
    "Employee Onboarding Manual — AcmeCorp",
    [
        "Welcome to AcmeCorp",
        "We are excited to have you join our team. This manual covers everything you need "
        "to know to get started in your first 30 days at AcmeCorp.",

        "Day 1 Checklist",
        "1. Collect your laptop and access badge from IT on the 3rd floor. "
        "2. Set up your company email and Slack account. "
        "3. Complete the mandatory security awareness training on the HR portal. "
        "4. Meet with your direct manager for a 1-on-1 orientation session. "
        "5. Review and sign the NDA and IP assignment agreement.",

        "Company Policies",
        "Working Hours: Standard hours are 9 AM to 6 PM Monday through Friday. "
        "Remote Work: Employees may work remotely up to 3 days per week after probation. "
        "Leave Policy: 20 days paid annual leave, 10 days sick leave per year. "
        "Code of Conduct: All employees must adhere to the AcmeCorp Code of Conduct "
        "available on the internal wiki.",

        "IT and Security",
        "All company devices must have full disk encryption enabled. "
        "Passwords must be at least 12 characters and use a password manager. "
        "Never share credentials or access cards with colleagues or visitors. "
        "Report any suspicious activity immediately to security@acmecorp.com.",

        "Benefits",
        "Health Insurance: Full medical, dental, and vision coverage from day one. "
        "Retirement: 401k with 4% company match vesting immediately. "
        "Learning Budget: $1500 annual budget for courses, books, and conferences. "
        "Gym Allowance: $50 per month reimbursement for fitness expenses.",
    ]
)

# 3. Research Paper
make_pdf(
    "ai_research_paper.pdf",
    "Advances in Retrieval Augmented Generation Systems",
    [
        "Abstract",
        "This paper surveys recent advances in Retrieval Augmented Generation (RAG) systems "
        "for large language models. We analyze key components including dense retrieval, "
        "chunk optimization, reranking strategies, and citation grounding. Our evaluation "
        "across five benchmark datasets shows that hybrid retrieval with reranking improves "
        "answer accuracy by 34% compared to naive RAG baselines.",

        "1. Introduction",
        "Large language models have demonstrated remarkable capabilities in text generation "
        "but suffer from hallucination and knowledge cutoff limitations. RAG systems address "
        "these issues by grounding model outputs in retrieved document evidence. "
        "The core pipeline consists of document ingestion, chunk indexing, query-time "
        "retrieval, and answer synthesis with source attribution.",

        "2. Retrieval Methods",
        "Sparse retrieval methods such as BM25 rely on keyword matching and are highly "
        "efficient but miss semantic relationships. Dense retrieval using bi-encoder models "
        "like sentence-transformers captures semantic similarity but requires more compute. "
        "Hybrid retrieval combining both approaches consistently outperforms either alone.",

        "3. Chunking Strategies",
        "Optimal chunk size depends on document type and query complexity. "
        "Our experiments show that 400-600 word chunks with 10% overlap yield the best "
        "retrieval precision for technical documents. Sentence-boundary-aware chunking "
        "reduces context fragmentation significantly.",

        "4. Citation Grounding",
        "Grounded citation generation requires the model to attribute every claim to a "
        "specific source document and page. Fine-tuned models show 89% citation accuracy "
        "versus 61% for prompted-only approaches. Inline citation formats outperform "
        "footnote styles in user comprehension studies.",

        "5. Conclusion",
        "RAG systems continue to evolve rapidly. Future work should focus on multi-modal "
        "retrieval, real-time index updates, and improved faithfulness evaluation metrics.",
    ]
)

# 4. Invoice
make_pdf(
    "invoice_2024_1089.pdf",
    "INVOICE #2024-1089",
    [
        "Bill From: TechSolutions Ltd | 42 Innovation Drive, San Francisco CA 94105",
        "Bill To: AcmeCorp | 100 Business Ave, New York NY 10001",
        "Invoice Date: December 15, 2024 | Due Date: January 15, 2025",

        "Services Rendered:",
        Table(
            [
                ["Description", "Qty", "Unit Price", "Total"],
                ["Backend API Development", "80 hrs", "$150/hr", "$12,000"],
                ["Frontend UI Implementation", "60 hrs", "$130/hr", "$7,800"],
                ["DevOps and Deployment Setup", "20 hrs", "$140/hr", "$2,800"],
                ["Code Review and QA", "15 hrs", "$120/hr", "$1,800"],
                ["", "", "Subtotal", "$24,400"],
                ["", "", "Tax (8.5%)", "$2,074"],
                ["", "", "Total Due", "$26,474"],
            ],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ])
        ),

        "Payment Terms",
        "Payment is due within 30 days of invoice date. Late payments incur a 1.5% "
        "monthly interest charge. Please transfer to: Bank: Chase Bank | "
        "Account: 4521-8834-9921 | Routing: 021000021",

        "Thank you for your business. Questions? Contact billing@techsolutions.com",
    ]
)

# 5. Project Requirements Document
make_pdf(
    "project_requirements.pdf",
    "Project Requirements — SmartPortal v2.0",
    [
        "Project Overview",
        "SmartPortal v2.0 is a customer-facing web portal that enables enterprise clients "
        "to manage their accounts, view analytics, raise support tickets, and configure "
        "integrations. The project targets a Q2 2025 launch with a team of 8 engineers.",

        "Functional Requirements",
        "FR-01: Users must be able to register and log in using email or SSO (Google, Microsoft). "
        "FR-02: Dashboard must display real-time usage analytics with chart visualizations. "
        "FR-03: Support ticket system must support file attachments up to 25MB. "
        "FR-04: Integration marketplace must list and activate third-party connectors. "
        "FR-05: Admin panel must allow role-based access control with audit logging.",

        "Non-Functional Requirements",
        "NFR-01: System must handle 10,000 concurrent users with under 200ms response time. "
        "NFR-02: Uptime SLA of 99.9% with automated failover. "
        "NFR-03: All data must be encrypted at rest (AES-256) and in transit (TLS 1.3). "
        "NFR-04: GDPR compliance required — users can export and delete their data. "
        "NFR-05: Mobile-responsive design supporting iOS 15+ and Android 12+.",

        "Technical Stack",
        "Frontend: Next.js 14 with TypeScript and Tailwind CSS. "
        "Backend: FastAPI (Python 3.11) with PostgreSQL and Redis. "
        "Infrastructure: AWS ECS with RDS, ElastiCache, and CloudFront CDN. "
        "Monitoring: Datadog APM with PagerDuty alerting.",

        "Timeline",
        "Phase 1 (Weeks 1-4): Authentication, user management, and core dashboard. "
        "Phase 2 (Weeks 5-8): Support tickets, file uploads, and integrations. "
        "Phase 3 (Weeks 9-12): Admin panel, analytics, and performance optimization. "
        "Phase 4 (Weeks 13-14): QA, security audit, and production deployment.",
    ]
)

print("\nAll sample documents created in sample_docs/")
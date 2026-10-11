from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt


OUT = Path(__file__).with_name("TenantAI_10_Slide_Jury_Presentation.pptx")
W, H = 13.333, 7.5
BG = RGBColor(7, 13, 27)
PANEL = RGBColor(16, 27, 48)
PANEL_ALT = RGBColor(21, 38, 66)
TEXT = RGBColor(239, 246, 255)
MUTED = RGBColor(159, 176, 201)
TEAL = RGBColor(45, 212, 191)
BLUE = RGBColor(96, 165, 250)
AMBER = RGBColor(251, 191, 36)
RED = RGBColor(248, 113, 113)
LINE = RGBColor(48, 70, 103)


def add_text(slide, value, x, y, w, h, size=16, color=TEXT, bold=False, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.vertical_anchor = MSO_ANCHOR.TOP
    para = frame.paragraphs[0]
    para.alignment = align
    run = para.add_run()
    run.text = value
    run.font.name = "Aptos"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def card(slide, x, y, w, h, title, body, accent=TEAL, size=12):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = PANEL
    shape.line.color.rgb = LINE
    add_text(slide, title, x + 0.18, y + 0.16, w - 0.36, 0.3, 14, accent, True)
    add_text(slide, body, x + 0.18, y + 0.58, w - 0.36, h - 0.72, size, TEXT)


def slide_base(prs, title, subtitle, section):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = BG
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.12), Inches(H))
    bar.fill.solid()
    bar.fill.fore_color.rgb = TEAL
    bar.line.fill.background()
    add_text(slide, section.upper(), 0.7, 0.25, 2.0, 0.2, 9, TEAL, True)
    add_text(slide, title, 0.68, 0.52, 12.0, 0.5, 27, TEXT, True)
    add_text(slide, subtitle, 0.7, 1.08, 11.8, 0.3, 11, MUTED)
    add_text(slide, f"tenantAI  |  jury presentation  |  {len(prs.slides):02d}", 0.7, 7.16, 12, 0.18, 8, MUTED)
    return slide


def flow(slide, labels, y=2.2, start=0.55, width=1.48, gap=0.15):
    for i, label in enumerate(labels):
        x = start + i * (width + gap)
        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(width), Inches(0.9)
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = PANEL_ALT
        shape.line.color.rgb = TEAL
        add_text(slide, str(i + 1), x + 0.07, y + 0.1, 0.2, 0.2, 10, TEAL, True)
        add_text(slide, label, x + 0.25, y + 0.16, width - 0.3, 0.55, 10, TEXT, True, PP_ALIGN.CENTER)


prs = Presentation()
prs.slide_width = Inches(W)
prs.slide_height = Inches(H)

# 1. Introduction
slide = slide_base(prs, "tenantAI", "Secure multi-tenant AI knowledge platform", "Introduction")
add_text(slide, "Company knowledge.\nGrounded answers.\nProvable isolation.", 0.9, 1.8, 7.1, 2.0, 31, TEXT, True)
add_text(slide, "tenantAI converts private company documents into a searchable AI assistant with citations, role-based access, tenant isolation, and audit telemetry.", 0.95, 4.15, 7.4, 0.8, 17, MUTED)
card(slide, 9.0, 1.85, 1.55, 1.2, "RAG", "Cited answers", TEAL, 11)
card(slide, 10.8, 1.85, 1.55, 1.2, "RBAC", "Role control", BLUE, 11)
card(slide, 9.0, 3.35, 1.55, 1.2, "404", "Hidden IDOR", AMBER, 11)
card(slide, 10.8, 3.35, 1.55, 1.2, "OTP", "Verified users", TEAL, 11)
add_text(slide, "TriCity AI Hackathon | SaaSsum AI track | Jury-ready MVP", 0.95, 6.35, 8.5, 0.3, 12, TEAL, True)

# 2. Problem statement
slide = slide_base(prs, "Problem statement", "Why traditional knowledge access is slow, uncertain, and risky", "Problem")
card(slide, 0.7, 1.75, 2.85, 3.85, "Fragmented knowledge", "Manual search across PDFs, manuals, emails, and policies creates duplicated effort and inconsistent answers.", RED, 13)
card(slide, 3.75, 1.75, 2.85, 3.85, "Slow decisions", "Support and operations teams spend time finding information instead of acting on verified information.", AMBER, 13)
card(slide, 6.8, 1.75, 2.85, 3.85, "AI trust gap", "A fluent answer without a source is difficult to approve, explain, or correct when company policy changes.", BLUE, 13)
card(slide, 9.85, 1.75, 2.85, 3.85, "Data leakage", "A shared search index or missing tenant filter can expose one company's confidential documents to another.", RED, 13)
add_text(slide, "Core challenge: make enterprise AI useful without sacrificing evidence, ownership, or privacy.", 0.9, 6.15, 11.5, 0.35, 15, TEAL, True, PP_ALIGN.CENTER)

# 3. Solution
slide = slide_base(prs, "Our solution", "A verified, tenant-scoped, citation-first AI workspace", "Solution")
flow(slide, ["Verify user", "Resolve tenant", "Upload files", "Retrieve owned chunks", "Answer with citations", "Audit event"], y=2.1, start=0.38, width=1.85, gap=0.14)
card(slide, 0.85, 4.0, 3.7, 1.55, "Useful", "Ask natural-language questions instead of searching folders manually.", TEAL, 14)
card(slide, 4.82, 4.0, 3.7, 1.55, "Explainable", "Answers include source document/page evidence and retrieval metadata.", BLUE, 14)
card(slide, 8.79, 4.0, 3.7, 1.55, "Defensible", "The backend enforces tenant ownership before data is retrieved or changed.", AMBER, 14)
add_text(slide, "The platform refuses unsupported questions rather than presenting unrelated or invented company facts.", 0.95, 6.2, 11.4, 0.35, 14, MUTED, False, PP_ALIGN.CENTER)

# 4. Features
slide = slide_base(prs, "Key features and user value", "The MVP covers the complete company knowledge lifecycle", "Product")
card(slide, 0.6, 1.7, 2.95, 4.15, "Authentication", "Registration\nEmail OTP verification\nBcrypt password hashing\nJWT session\nRole-based access\n\nValue: only verified users enter protected workspaces.", TEAL, 12)
card(slide, 3.65, 1.7, 2.95, 4.15, "Knowledge base", "PDF/TXT/MD upload\nFile validation and quotas\nText extraction\nChunking and embeddings\nREADY/FAILED status\n\nValue: approved material becomes searchable.", BLUE, 12)
card(slide, 6.7, 1.7, 2.95, 4.15, "AI workspace", "Tenant-scoped RAG\nConversation history\nPage citations\nConfidence and latency\nOut-of-domain refusal\n\nValue: answers are useful and traceable.", TEAL, 12)
card(slide, 9.75, 1.7, 2.95, 4.15, "Governance", "Audit and telemetry\nTenant quotas\nAdmin center\nSecurity events\nIDOR simulator\n\nValue: operators can prove system behavior.", AMBER, 12)

# 5. Tech stack
slide = slide_base(prs, "Technology stack", "Practical tools selected for speed, clarity, and a production path", "Engineering")
card(slide, 0.7, 1.75, 3.0, 1.6, "Frontend", "Next.js 16\nReact 19\nTypeScript\nTailwind CSS\nLucide icons", BLUE, 13)
card(slide, 3.9, 1.75, 3.0, 1.6, "Backend", "Python\nFastAPI\nUvicorn\nPydantic v2\nJWT + bcrypt", TEAL, 13)
card(slide, 7.1, 1.75, 3.0, 1.6, "Data and AI", "SQLAlchemy\nSQLite local mode\nPostgreSQL + pgvector path\nSemantic embeddings\nGrounded RAG", AMBER, 13)
card(slide, 10.3, 1.75, 2.3, 1.6, "Operations", "Docker Compose\nRender blueprint\nSMTP OTP\nTelegram worker path", TEAL, 12)
add_text(slide, "Design principle: keep the local demo zero-dependency where possible, while preserving a clear PostgreSQL, storage, and worker path for production.", 1.0, 4.4, 11.2, 0.65, 17, TEXT, True, PP_ALIGN.CENTER)
add_text(slide, "Security tooling: server-side tenant guards, strict CORS, production secret validation, redacted logs, security headers, and automated regression tests.", 0.95, 5.55, 11.4, 0.55, 14, MUTED, False, PP_ALIGN.CENTER)

# 6. Architecture
slide = slide_base(prs, "System architecture", "The browser requests; the backend decides", "Architecture")
card(slide, 0.7, 1.7, 2.55, 1.45, "Next.js UI", "Dashboard, chat, documents, admin, auth", BLUE, 12)
card(slide, 3.6, 1.7, 2.55, 1.45, "FastAPI gateway", "JWT, RBAC, tenant guards, APIs", TEAL, 12)
card(slide, 6.5, 1.7, 2.55, 1.45, "Database", "Tenants, users, docs, chunks, messages, logs", AMBER, 12)
card(slide, 9.4, 1.7, 2.55, 1.45, "RAG engine", "Scoped retrieval, grounded response, citations", TEAL, 12)
flow(slide, ["Request", "Authenticate", "Authorize", "Filter tenant data", "Retrieve evidence", "Respond + audit"], y=4.0, start=0.45, width=1.75, gap=0.16)
add_text(slide, "Security invariant: tenant_id is derived from the verified identity. Client-supplied tenant IDs are not trusted for regular users.", 0.95, 5.75, 11.4, 0.5, 16, TEXT, True, PP_ALIGN.CENTER)

# 7. Comparison table
slide = slide_base(prs, "Traditional approach vs tenantAI", "The product difference is visible across the entire workflow", "Differentiation")
headers = [("Area", 0.55, 2.0), ("Traditional approach", 2.7, 4.45), ("tenantAI", 7.25, 5.55)]
for title, x, w in headers:
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(1.62), Inches(w), Inches(0.48))
    shape.fill.solid()
    shape.fill.fore_color.rgb = PANEL_ALT
    shape.line.color.rgb = LINE
    add_text(slide, title, x + 0.12, 1.75, w - 0.24, 0.2, 12, TEAL, True)
rows = [
    ("Search", "Folders, PDFs, keyword search", "Natural-language semantic retrieval"),
    ("Answers", "Manual interpretation or generic AI", "Grounded answer from owned documents"),
    ("Evidence", "Source verification is manual", "Document/page citations included"),
    ("Tenancy", "Separate systems or fragile filters", "Server-side tenant predicates"),
    ("Security", "Login may be the main control", "OTP, JWT, RBAC, ownership checks, hidden 404"),
    ("Governance", "Limited access visibility", "Audit events, latency, tokens, outcomes"),
    ("Failure", "May return irrelevant content", "Explicit refusal when evidence is absent"),
]
for r, row in enumerate(rows):
    y = 2.1 + r * 0.61
    for value, x, w in zip(row, [0.55, 2.7, 7.25], [2.0, 4.45, 5.55]):
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(0.58))
        shape.fill.solid()
        shape.fill.fore_color.rgb = PANEL if r % 2 == 0 else BG
        shape.line.color.rgb = LINE
        add_text(slide, value, x + 0.12, y + 0.13, w - 0.24, 0.3, 10 if x < 2 else 11, TEXT if x != 7.25 else TEAL, x == 7.25)
add_text(slide, "Traditional systems answer “where is the file?” tenantAI answers “what does our verified knowledge say, and can we prove it?”", 0.85, 6.55, 11.7, 0.3, 13, AMBER, True, PP_ALIGN.CENTER)

# 8. Security and IDOR
slide = slide_base(prs, "Security proof: the IDOR simulator", "A live demonstration of Company A attempting to access Company B", "Security")
card(slide, 0.75, 1.75, 3.7, 3.8, "Attack", "Company A changes a document or conversation ID to target Company B.\n\nThe request is intentionally modeled as an Insecure Direct Object Reference attempt.", RED, 14)
card(slide, 4.8, 1.75, 3.7, 3.8, "Backend control", "The server uses the authenticated JWT tenant and ownership filters.\n\nThe browser cannot override tenant scope through a URL or request body.", BLUE, 14)
card(slide, 8.85, 1.75, 3.7, 3.8, "Observed result", "HTTP 404\n0 bytes leaked\ncross_tenant_denied audit event\n\n404 hides resource existence instead of confirming another tenant's data.", TEAL, 14)
add_text(slide, "The simulator is restricted to SuperAdmin and is a controlled proof of isolation—not a normal end-user feature.", 0.9, 6.15, 11.5, 0.35, 14, MUTED, False, PP_ALIGN.CENTER)

# 9. Demo and evidence
slide = slide_base(prs, "Jury demo flow and evidence", "A short sequence that shows usefulness and security", "Demo")
demo = [
    ("1", "Login as TechNova", "Use the demo account and show its private knowledge list."),
    ("2", "Ask warranty question", "Show grounded answer with UltraBook manual citation."),
    ("3", "Switch to GreenLeaf", "Show a different company workspace and document set."),
    ("4", "Ask foreign question", "Show refusal and zero TechNova citations."),
    ("5", "Run IDOR simulator", "Show HTTP 404, no leaked data, and security event."),
    ("6", "Open telemetry", "Explain actor, tenant, action, outcome, latency, and redaction."),
]
for i, (num, title, body) in enumerate(demo):
    y = 1.55 + i * 0.72
    add_text(slide, num, 0.9, y, 0.35, 0.3, 14, TEAL, True)
    add_text(slide, title, 1.45, y, 3.2, 0.3, 15, TEXT, True)
    add_text(slide, body, 5.0, y, 7.2, 0.3, 13, MUTED)
card(slide, 1.0, 6.05, 5.2, 0.55, "TechNova", "admin@technova.com  |  DemoPass123!", TEAL, 10)
card(slide, 7.1, 6.05, 5.2, 0.55, "GreenLeaf", "admin@greenleaf.com  |  DemoPass123!", BLUE, 10)

# 10. Conclusion and roadmap
slide = slide_base(prs, "Conclusion and future roadmap", "Secure foundations first; scale only what can be verified", "Closing")
card(slide, 0.7, 1.7, 3.8, 3.9, "What is working now", "Tenant-scoped authentication\nDocument upload and processing\nGrounded RAG with citations\nConversation history\nAudit telemetry\nIDOR security demonstration\nAccessible responsive UI", TEAL, 13)
card(slide, 4.8, 1.7, 3.8, 3.9, "Next implementation", "Alembic migrations\nPrivate object storage\nRate limiting and WAF\nDependency scanning\nAsync workers and OCR\nVerified Render deployment\nBackups and alerting", BLUE, 13)
card(slide, 8.9, 1.7, 3.8, 3.9, "Long-term vision", "SSO and MFA\nSlack/Teams/Telegram channels\nHybrid search and reranking\nCompliance controls\nUsage billing\nEnterprise knowledge operating system", AMBER, 13)
add_text(slide, "tenantAI is not only a chatbot—it is a secure, auditable knowledge layer for organizations.", 0.9, 6.25, 11.5, 0.4, 18, TEAL, True, PP_ALIGN.CENTER)

prs.save(OUT)
print(OUT)

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


OUT = Path(__file__).with_name("SaaSsum_AI_Presentation.pptx")
BG = RGBColor(11, 17, 32)
CARD = RGBColor(17, 26, 45)
TEXT = RGBColor(229, 237, 247)
MUTED = RGBColor(148, 163, 184)
ACCENT = RGBColor(45, 212, 191)


def add_text(slide, text, x, y, w, h, size=24, color=TEXT, bold=False, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    paragraph = frame.paragraphs[0]
    paragraph.alignment = align
    run = paragraph.add_run()
    run.text = text
    run.font.name = "Aptos"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def add_card(slide, x, y, w, h, title, body):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = CARD
    shape.line.color.rgb = RGBColor(45, 58, 82)
    add_text(slide, title, x + 0.2, y + 0.18, w - 0.4, 0.35, 16, ACCENT, True)
    add_text(slide, body, x + 0.2, y + 0.65, w - 0.4, h - 0.8, 12, TEXT)


def base_slide(prs, title, subtitle=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = BG
    add_text(slide, title, 0.65, 0.45, 12, 0.55, 28, TEXT, True)
    if subtitle:
        add_text(slide, subtitle, 0.68, 1.08, 11.8, 0.35, 12, MUTED)
    return slide


prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

slide = base_slide(prs, "tenantAI", "Secure multi-tenant AI knowledge platform | Hackathon presentation")
add_text(slide, "Company knowledge, grounded answers, and tenant isolation in one workspace.", 0.8, 2.1, 11.5, 1.0, 30, TEXT, True)
add_text(slide, "FastAPI + SQLAlchemy + Next.js + tenant-scoped RAG + security telemetry", 0.85, 3.35, 11.2, 0.45, 16, ACCENT)
add_text(slide, "TriCity AI Hackathon | SaaSsum AI track", 0.85, 6.55, 11.5, 0.3, 11, MUTED)

slide = base_slide(prs, "The problem", "Enterprise knowledge is valuable only when it is findable and isolated.")
add_card(slide, 0.75, 1.8, 3.8, 3.3, "Fragmented knowledge", "Teams search across PDFs, manuals, and policies with no consistent answer path.")
add_card(slide, 4.8, 1.8, 3.8, 3.3, "Slow decisions", "Manual document review consumes time and makes answers difficult to audit.")
add_card(slide, 8.85, 1.8, 3.8, 3.3, "Isolation risk", "A shared retrieval layer can expose another company's private information.")

slide = base_slide(prs, "The solution", "A secure assistant for each company's own knowledge boundary.")
add_card(slide, 0.8, 1.8, 3.7, 3.7, "Register", "Create a company workspace and verify the administrator email with a six-digit OTP.")
add_card(slide, 4.8, 1.8, 3.7, 3.7, "Retrieve", "Search only READY documents belonging to the authenticated tenant.")
add_card(slide, 8.8, 1.8, 3.7, 3.7, "Answer", "Return grounded responses with document and page citations plus audit telemetry.")

slide = base_slide(prs, "Who benefits?", "One platform supports several enterprise personas without mixing their data.")
add_card(slide, 0.75, 1.8, 3.8, 3.55, "Company administrator", "Creates the workspace, manages members, reviews usage, and monitors security events.")
add_card(slide, 4.8, 1.8, 3.8, 3.55, "Knowledge worker", "Uploads approved material, asks natural-language questions, and reuses conversation history.")
add_card(slide, 8.85, 1.8, 3.8, 3.55, "Platform operator", "Uses SuperAdmin analytics, tenant summaries, quotas, and the live IDOR simulator.")
add_text(slide, "Value: faster answers, fewer repeated support questions, and evidence that each answer stayed inside the correct workspace.", 0.95, 6.0, 11.4, 0.55, 15, ACCENT, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "Product surfaces", "The MVP is organized around the full knowledge-work lifecycle.")
add_card(slide, 0.65, 1.75, 2.85, 3.9, "Authentication", "Registration\nEmail OTP verification\nVerified login\nJWT session\nRole-based access")
add_card(slide, 3.65, 1.75, 2.85, 3.9, "Knowledge base", "PDF/TXT upload\nFile validation\nText extraction\nChunking\nDocument lifecycle status")
add_card(slide, 6.65, 1.75, 2.85, 3.9, "AI workspace", "Grounded chat\nSimilarity retrieval\nPage citations\nConversation history\nOut-of-domain refusal")
add_card(slide, 9.65, 1.75, 2.85, 3.9, "Governance", "Audit logs\nLatency and token telemetry\nTenant quotas\nAdmin center\nIDOR simulator")

slide = base_slide(prs, "Architecture", "Shared backend and database; tenant identity is derived from authenticated state.")
add_card(slide, 0.7, 1.75, 2.6, 1.35, "Next.js", "Dark-first web dashboard")
add_card(slide, 3.65, 1.75, 2.6, 1.35, "FastAPI", "Auth, RBAC, tenant guards")
add_card(slide, 6.6, 1.75, 2.6, 1.35, "SQLAlchemy", "Shared relational data")
add_card(slide, 9.55, 1.75, 2.6, 1.35, "RAG", "Scoped retrieval + citations")
add_text(slide, "Frontend → API gateway → database and document storage → RAG engine → grounded response", 1.0, 4.1, 11.2, 0.7, 20, ACCENT, True, PP_ALIGN.CENTER)
add_text(slide, "All tenant-sensitive paths validate ownership server-side; frontend IDs are never trusted.", 1.0, 5.2, 11.2, 0.45, 14, TEXT, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "Workflow automation", "Document Upload → File Validation → Extraction → Chunking → Embeddings → Tenant-Scoped Indexing")
steps = ["Upload", "Validate", "Extract", "Chunk", "Embed", "Index", "Retrieve", "Cite"]
for i, step in enumerate(steps):
    x = 0.55 + i * 1.58
    add_card(slide, x, 2.2, 1.25, 1.2, str(i + 1), step)
add_text(slide, "Processing status is persisted as PENDING / PROCESSING / READY / FAILED with safe retry visibility.", 1.0, 4.5, 11.2, 0.5, 16, TEXT, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "Security model", "Verified identity and server-side scoping protect every workspace.")
add_card(slide, 0.75, 1.75, 3.8, 3.65, "Email verification", "OTP is cryptographically random, hashed at rest, expires after five minutes, and is rate limited.")
add_card(slide, 4.8, 1.75, 3.8, 3.65, "Tenant isolation", "Documents, chunks, conversations, logs, and retrieval queries require the authenticated tenant scope.")
add_card(slide, 8.85, 1.75, 3.8, 3.65, "Auditability", "Login, upload, deletion, query, and cross-tenant probes are recorded for review.")

slide = base_slide(prs, "Security proof: the IDOR demo", "The project demonstrates prevention, not only a security claim.")
add_text(slide, "Attacker scenario", 0.9, 1.7, 3.0, 0.4, 18, ACCENT, True)
add_text(slide, "GreenLeaf user attempts to fetch TechNova document ID #1.", 0.9, 2.2, 4.5, 0.9, 19, TEXT, True)
add_text(slide, "Server enforcement", 5.0, 1.7, 3.0, 0.4, 18, ACCENT, True)
add_text(slide, "JWT tenant identity overrides client-supplied IDs and applies tenant filters to the query.", 5.0, 2.2, 3.5, 1.35, 17, TEXT, True)
add_text(slide, "Observed result", 9.0, 1.7, 3.0, 0.4, 18, ACCENT, True)
add_text(slide, "HTTP 404\n0 bytes leaked\ncross_tenant_denied audit event", 9.0, 2.2, 3.4, 1.5, 21, TEXT, True)
add_text(slide, "404 instead of 403 also avoids revealing whether another tenant's resource exists.", 1.0, 5.6, 11.2, 0.5, 16, ACCENT, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "RAG behavior", "Answers are constrained by the verified workspace knowledge base.")
add_card(slide, 0.75, 1.8, 3.8, 3.6, "1. Retrieve", "The query is embedded and compared against chunks from READY documents in the caller's tenant only.")
add_card(slide, 4.8, 1.8, 3.8, 3.6, "2. Ground", "Relevant chunks are passed as context to the response layer; unsupported claims are not treated as facts.")
add_card(slide, 8.85, 1.8, 3.8, 3.6, "3. Cite or refuse", "The answer includes document/page evidence or explicitly refuses when the workspace has no support.")
add_text(slide, "Example: GreenLeaf can answer its 30-day return policy, but cannot answer TechNova's laptop warranty question.", 0.9, 6.0, 11.5, 0.45, 15, ACCENT, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "Live demo path", "Use real data and label anything not yet deployed.")
add_text(slide, "1  Register company", 1.0, 1.8, 5.2, 0.5, 20, TEXT, True)
add_text(slide, "2  Verify OTP from SMTP or development log", 1.0, 2.5, 6.8, 0.5, 20, TEXT, True)
add_text(slide, "3  Upload a PDF/TXT/MD document", 1.0, 3.2, 6.8, 0.5, 20, TEXT, True)
add_text(slide, "4  Ask a grounded question and inspect citations", 1.0, 3.9, 7.5, 0.5, 20, TEXT, True)
add_text(slide, "5  Register a second company and verify isolation", 1.0, 4.6, 8.4, 0.5, 20, TEXT, True)
add_text(slide, "Optional follow-up: connect the same tenant-scoped APIs to a Telegram worker after deployment.", 1.0, 6.25, 11.0, 0.35, 13, ACCENT)

slide = base_slide(prs, "Demo credentials and data", "Use these legacy fixtures only for the jury walkthrough; do not use them in production.")
add_card(slide, 0.75, 1.75, 3.8, 3.75, "TechNova Solutions", "Admin: admin@technova.com\nPassword: DemoPass123!\n\nKnowledge: UltraBook Pro X15 hardware manual")
add_card(slide, 4.8, 1.75, 3.8, 3.75, "GreenLeaf Retail", "Admin: admin@greenleaf.com\nPassword: DemoPass123!\n\nKnowledge: customer refund and return policy")
add_card(slide, 8.85, 1.75, 3.8, 3.75, "Best demo sequence", "Login as TechNova → ask a warranty question → switch to GreenLeaf → verify TechNova data is invisible → run the IDOR simulator.")
add_text(slide, "These accounts are presentation fixtures and intentionally remain unchanged by request.", 1.0, 6.15, 11.2, 0.35, 13, MUTED, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "Deployment and testing", "Move from local proof to a repeatable production setup.")
add_card(slide, 0.75, 1.75, 3.8, 3.75, "Local stack", "Next.js at :3000\nFastAPI at :8001\nSQLite for zero-dependency development\nPytest for API and isolation checks")
add_card(slide, 4.8, 1.75, 3.8, 3.75, "Production shape", "Render frontend + backend\nManaged PostgreSQL/pgvector\nSMTP provider\nPersistent object storage\nEnvironment-managed secrets")
add_card(slide, 8.85, 1.75, 3.8, 3.75, "Release gates", "Health endpoint\nStrict CORS\nNo development reload\nRegistration and OTP test\nTenant isolation regression test")

slide = base_slide(prs, "API and observability", "The platform exposes clear boundaries for UI, integrations, and operators.")
add_card(slide, 0.75, 1.75, 3.8, 3.8, "Auth APIs", "register\nverify-email\nresend-verification\nlogin\nme")
add_card(slide, 4.8, 1.75, 3.8, 3.8, "Knowledge APIs", "documents\nupload\ninspect/delete document\nchat message\nconversation history")
add_card(slide, 8.85, 1.75, 3.8, 3.8, "Operator APIs", "logs and telemetry\nadmin stats\ntenant summaries\nprovision tenants\nsecurity simulation")
add_text(slide, "Every sensitive operation is measurable: actor, tenant, action, outcome, latency, and resource context.", 0.95, 6.15, 11.4, 0.35, 14, ACCENT, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "Evaluation snapshot", "How the implementation maps to a jury rubric.")
add_card(slide, 0.75, 1.75, 3.8, 3.85, "Working MVP", "Authentication, document upload, RAG chat, citations, tenant dashboards, logs, and an interactive security demo.")
add_card(slide, 4.8, 1.75, 3.8, 3.85, "Differentiation", "Security is visible and testable: out-of-domain refusal, tenant-scoped retrieval, 404 IDOR protection, and audit evidence.")
add_card(slide, 8.85, 1.75, 3.8, 3.85, "Business value", "Reusable company knowledge, faster support decisions, lower information risk, and a path to per-tenant SaaS pricing.")
add_text(slide, "Honest status: deployment verification, object storage, OCR, and formal migrations remain production follow-up work.", 0.9, 6.15, 11.5, 0.4, 13, MUTED, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "Conclusion and roadmap", "Secure foundations first; integrate only what can be verified.")
add_card(slide, 0.75, 1.8, 3.8, 3.6, "Now", "Tenant-scoped FastAPI APIs, grounded RAG, OTP registration, dark-first auth UI, audit telemetry.")
add_card(slide, 4.8, 1.8, 3.8, 3.6, "Next", "Complete Telegram account linking and 120-second session enforcement on a shared bot service.")
add_card(slide, 8.85, 1.8, 3.8, 3.6, "Future", "Async workers, OCR, object storage, richer feedback/export, and managed deployment verification.")
add_text(slide, "Build trust into the architecture, then make the demo visible.", 1.0, 6.25, 11.2, 0.4, 18, ACCENT, True, PP_ALIGN.CENTER)

prs.save(OUT)
print(OUT)

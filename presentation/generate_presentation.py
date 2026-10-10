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

slide = base_slide(prs, "SaaSsum AI", "Multi-tenant AI chatbot platform | Hackathon presentation")
add_text(slide, "Company knowledge, grounded answers, and tenant isolation in one workspace.", 0.8, 2.1, 11.5, 1.0, 30, TEXT, True)
add_text(slide, "Production direction: FastAPI + SQLAlchemy + Next.js + tenant-scoped RAG", 0.85, 3.35, 10.5, 0.45, 16, ACCENT)
add_text(slide, "Implemented surfaces are distinguished from follow-up integration work.", 0.85, 6.55, 11.5, 0.3, 11, MUTED)

slide = base_slide(prs, "The problem", "Enterprise knowledge is valuable only when it is findable and isolated.")
add_card(slide, 0.75, 1.8, 3.8, 3.3, "Fragmented knowledge", "Teams search across PDFs, manuals, and policies with no consistent answer path.")
add_card(slide, 4.8, 1.8, 3.8, 3.3, "Slow decisions", "Manual document review consumes time and makes answers difficult to audit.")
add_card(slide, 8.85, 1.8, 3.8, 3.3, "Isolation risk", "A shared retrieval layer can expose another company's private information.")

slide = base_slide(prs, "The solution", "A secure assistant for each company's own knowledge boundary.")
add_card(slide, 0.8, 1.8, 3.7, 3.7, "Register", "Create a company workspace and verify the administrator email with a six-digit OTP.")
add_card(slide, 4.8, 1.8, 3.7, 3.7, "Retrieve", "Search only READY documents belonging to the authenticated tenant.")
add_card(slide, 8.8, 1.8, 3.7, 3.7, "Answer", "Return grounded responses with document and page citations plus audit telemetry.")

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

slide = base_slide(prs, "Live demo path", "Use real data and label anything not yet deployed.")
add_text(slide, "1  Register company", 1.0, 1.8, 5.2, 0.5, 20, TEXT, True)
add_text(slide, "2  Verify OTP from SMTP or development log", 1.0, 2.5, 6.8, 0.5, 20, TEXT, True)
add_text(slide, "3  Upload a PDF/TXT/MD document", 1.0, 3.2, 6.8, 0.5, 20, TEXT, True)
add_text(slide, "4  Ask a grounded question and inspect citations", 1.0, 3.9, 7.5, 0.5, 20, TEXT, True)
add_text(slide, "5  Register a second company and verify isolation", 1.0, 4.6, 8.4, 0.5, 20, TEXT, True)
add_text(slide, "Telegram bot: integration point documented; no fabricated bot or token.", 1.0, 6.25, 11.0, 0.35, 13, ACCENT)

slide = base_slide(prs, "Deployment and testing", "Prepare production infrastructure without performing paid or irreversible actions.")
add_card(slide, 0.75, 1.8, 3.8, 3.6, "Runtime", "Frontend and backend containers, managed PostgreSQL, persistent document storage, SMTP provider.")
add_card(slide, 4.8, 1.8, 3.8, 3.6, "Checks", "19 existing backend tests pass, including tenant isolation, RAG citations, admin access, and uploads.")
add_card(slide, 8.85, 1.8, 3.8, 3.6, "Operator checklist", "Set secrets, CORS, storage, health checks, migrations, and verify registration before launch.")

slide = base_slide(prs, "Conclusion and roadmap", "Secure foundations first; integrate only what can be verified.")
add_card(slide, 0.75, 1.8, 3.8, 3.6, "Now", "Tenant-scoped FastAPI APIs, grounded RAG, OTP registration, dark-first auth UI, audit telemetry.")
add_card(slide, 4.8, 1.8, 3.8, 3.6, "Next", "Complete Telegram account linking and 120-second session enforcement on a shared bot service.")
add_card(slide, 8.85, 1.8, 3.8, 3.6, "Future", "Async workers, OCR, object storage, richer feedback/export, and managed deployment verification.")
add_text(slide, "Build trust into the architecture, then make the demo visible.", 1.0, 6.25, 11.2, 0.4, 18, ACCENT, True, PP_ALIGN.CENTER)

prs.save(OUT)
print(OUT)

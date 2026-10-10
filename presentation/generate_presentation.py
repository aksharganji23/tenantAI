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
    add_text(slide, title, x + 0.2, y + 0.18, w - 0.4, 0.35, 15, ACCENT, True)
    add_text(slide, body, x + 0.2, y + 0.65, w - 0.4, h - 0.8, 11, TEXT)


def base_slide(prs, title, subtitle=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = BG
    add_text(slide, title, 0.65, 0.45, 12, 0.55, 28, TEXT, True)
    if subtitle:
        add_text(slide, subtitle, 0.68, 1.08, 11.8, 0.35, 12, MUTED)
    add_text(slide, f"tenantAI  |  jury presentation  |  {len(prs.slides):02d}", 0.68, 7.16, 12, 0.2, 8, MUTED)
    return slide


prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

slide = base_slide(prs, "tenantAI", "Secure multi-tenant AI knowledge platform | Hackathon presentation")
add_text(slide, "Company knowledge, grounded answers, and tenant isolation in one workspace.", 0.8, 2.1, 11.5, 1.0, 30, TEXT, True)
add_text(slide, "FastAPI + SQLAlchemy + Next.js + tenant-scoped RAG + security telemetry", 0.85, 3.35, 11.2, 0.45, 16, ACCENT)
add_text(slide, "The product turns scattered company documents into a searchable, auditable assistant without making privacy a configuration afterthought.", 0.85, 4.15, 11.3, 0.65, 16, TEXT)
add_text(slide, "TriCity AI Hackathon | SaaSsum AI track | MVP built for a jury-verifiable demo", 0.85, 6.55, 11.5, 0.3, 11, MUTED)

slide = base_slide(prs, "The problem", "Enterprise knowledge is valuable only when it is findable and isolated.")
add_card(slide, 0.75, 1.8, 3.8, 3.3, "Fragmented knowledge", "Teams search across PDFs, manuals, and policies with no consistent answer path.\n\nImpact: duplicated effort, inconsistent guidance, and slow onboarding.")
add_card(slide, 4.8, 1.8, 3.8, 3.3, "Slow decisions", "Manual document review consumes time and makes answers difficult to audit.\n\nImpact: support teams spend time finding facts instead of acting on them.")
add_card(slide, 8.85, 1.8, 3.8, 3.3, "Isolation risk", "A shared retrieval layer can expose another company's private information.\n\nImpact: one IDOR or missing filter can become a multi-tenant breach.")

slide = base_slide(prs, "The solution", "A secure assistant for each company's own knowledge boundary.")
add_card(slide, 0.8, 1.8, 3.7, 3.7, "Register", "Create a company workspace and verify the administrator email with a six-digit OTP.\n\nControl: unverified accounts cannot log in.")
add_card(slide, 4.8, 1.8, 3.7, 3.7, "Retrieve", "Search only READY documents belonging to the authenticated tenant.\n\nControl: tenant scope is applied server-side, not taken from the browser.")
add_card(slide, 8.8, 1.8, 3.7, 3.7, "Answer", "Return grounded responses with document and page citations plus audit telemetry.\n\nControl: unsupported questions receive an explicit refusal.")

slide = base_slide(prs, "Who benefits?", "One platform supports several enterprise personas without mixing their data.")
add_card(slide, 0.75, 1.8, 3.8, 3.55, "Company administrator", "Creates the workspace, manages members, reviews usage, and monitors security events.\n\nSuccess signal: clear ownership and faster policy decisions.")
add_card(slide, 4.8, 1.8, 3.8, 3.55, "Knowledge worker", "Uploads approved material, asks natural-language questions, and reuses conversation history.\n\nSuccess signal: answer plus citation in seconds.")
add_card(slide, 8.85, 1.8, 3.8, 3.55, "Platform operator", "Uses SuperAdmin analytics, tenant summaries, quotas, and the live IDOR simulator.\n\nSuccess signal: usage and risk are visible, not hidden.")
add_text(slide, "Value: faster answers, fewer repeated support questions, and evidence that each answer stayed inside the correct workspace.", 0.95, 6.0, 11.4, 0.55, 15, ACCENT, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "Product surfaces", "The MVP is organized around the full knowledge-work lifecycle.")
add_card(slide, 0.65, 1.75, 2.85, 3.9, "Authentication", "Registration\nEmail OTP verification\nVerified login\nJWT session\nRole-based access\n\nOutcome: trusted identity before data access.")
add_card(slide, 3.65, 1.75, 2.85, 3.9, "Knowledge base", "PDF/TXT upload\nFile validation\nText extraction\nChunking\nDocument lifecycle status\n\nOutcome: searchable source material.")
add_card(slide, 6.65, 1.75, 2.85, 3.9, "AI workspace", "Grounded chat\nSimilarity retrieval\nPage citations\nConversation history\nOut-of-domain refusal\n\nOutcome: useful and explainable answers.")
add_card(slide, 9.65, 1.75, 2.85, 3.9, "Governance", "Audit logs\nLatency and token telemetry\nTenant quotas\nAdmin center\nIDOR simulator\n\nOutcome: operators can prove behavior.")

slide = base_slide(prs, "Architecture", "Shared backend and database; tenant identity is derived from authenticated state.")
add_card(slide, 0.7, 1.75, 2.6, 1.35, "Next.js", "Dark-first web dashboard\nAccessible auth and tenant UI")
add_card(slide, 3.65, 1.75, 2.6, 1.35, "FastAPI", "Auth, RBAC, tenant guards\nHealth and API boundaries")
add_card(slide, 6.6, 1.75, 2.6, 1.35, "SQLAlchemy", "Shared relational data\nOwnership and status relationships")
add_card(slide, 9.55, 1.75, 2.6, 1.35, "RAG", "Scoped retrieval + citations\nGrounded response generation")
add_text(slide, "Frontend → API gateway → database and document storage → RAG engine → grounded response", 1.0, 4.1, 11.2, 0.7, 20, ACCENT, True, PP_ALIGN.CENTER)
add_text(slide, "All tenant-sensitive paths validate ownership server-side; frontend IDs are never trusted. The shared database is safe because every sensitive query carries the authenticated tenant boundary.", 1.0, 5.2, 11.2, 0.65, 14, TEXT, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "Workflow automation", "Document Upload → File Validation → Extraction → Chunking → Embeddings → Tenant-Scoped Indexing")
steps = ["Upload", "Validate", "Extract", "Chunk", "Embed", "Index", "Retrieve", "Cite"]
for i, step in enumerate(steps):
    x = 0.55 + i * 1.58
    add_card(slide, x, 2.2, 1.25, 1.2, str(i + 1), step)
add_text(slide, "Processing status is persisted as PENDING / PROCESSING / READY / FAILED with safe retry visibility. Unsupported formats, quotas, and parser failures produce explicit user-facing outcomes.", 1.0, 4.5, 11.2, 0.7, 15, TEXT, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "Security model", "Verified identity and server-side scoping protect every workspace.")
add_card(slide, 0.75, 1.75, 3.8, 3.65, "Email verification", "OTP is cryptographically random, hashed at rest, expires after five minutes, and is rate limited.\n\nEvidence: only verified users receive login tokens.")
add_card(slide, 4.8, 1.75, 3.8, 3.65, "Tenant isolation", "Documents, chunks, conversations, logs, and retrieval queries require the authenticated tenant scope.\n\nEvidence: cross-tenant resources return hidden 404 responses.")
add_card(slide, 8.85, 1.75, 3.8, 3.65, "Auditability", "Login, upload, deletion, query, and cross-tenant probes are recorded for review.\n\nEvidence: `/logs` shows action, outcome, actor, and tenant context.")

slide = base_slide(prs, "Security proof: the IDOR demo", "The project demonstrates prevention, not only a security claim.")
add_text(slide, "Attacker scenario", 0.9, 1.7, 3.0, 0.4, 18, ACCENT, True)
add_text(slide, "GreenLeaf user attempts to fetch TechNova document ID #1.", 0.9, 2.2, 4.5, 0.9, 19, TEXT, True)
add_text(slide, "Server enforcement", 5.0, 1.7, 3.0, 0.4, 18, ACCENT, True)
add_text(slide, "JWT tenant identity overrides client-supplied IDs and applies tenant filters to the query.\n\nThe attacker cannot select a different tenant by changing a URL or request body.", 5.0, 2.2, 3.5, 1.75, 16, TEXT, True)
add_text(slide, "Observed result", 9.0, 1.7, 3.0, 0.4, 18, ACCENT, True)
add_text(slide, "HTTP 404\n0 bytes leaked\ncross_tenant_denied audit event\n\nThe response avoids confirming another tenant's resource.", 9.0, 2.2, 3.4, 2.15, 18, TEXT, True)
add_text(slide, "404 instead of 403 also avoids revealing whether another tenant's resource exists.", 1.0, 5.6, 11.2, 0.5, 16, ACCENT, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "RAG behavior", "Answers are constrained by the verified workspace knowledge base.")
add_card(slide, 0.75, 1.8, 3.8, 3.6, "1. Retrieve", "The query is embedded and compared against chunks from READY documents in the caller's tenant only.\n\nFilter: tenant ID + document status + relevance.")
add_card(slide, 4.8, 1.8, 3.8, 3.6, "2. Ground", "Relevant chunks are passed as context to the response layer; unsupported claims are not treated as facts.\n\nTraceability: source text and page metadata stay attached.")
add_card(slide, 8.85, 1.8, 3.8, 3.6, "3. Cite or refuse", "The answer includes document/page evidence or explicitly refuses when the workspace has no support.\n\nSafety: absence of evidence is communicated instead of invented.")
add_text(slide, "Example: GreenLeaf can answer its 30-day return policy, but cannot answer TechNova's laptop warranty question.", 0.9, 6.0, 11.5, 0.45, 15, ACCENT, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "Live demo path", "Use real data and label anything not yet deployed.")
add_text(slide, "1  Register company", 1.0, 1.8, 5.2, 0.5, 20, TEXT, True)
add_text(slide, "2  Verify OTP from SMTP or development log", 1.0, 2.5, 6.8, 0.5, 20, TEXT, True)
add_text(slide, "3  Upload a PDF/TXT/MD document", 1.0, 3.2, 6.8, 0.5, 20, TEXT, True)
add_text(slide, "4  Ask a grounded question and inspect citations", 1.0, 3.9, 7.5, 0.5, 20, TEXT, True)
add_text(slide, "5  Register a second company and verify isolation", 1.0, 4.6, 8.4, 0.5, 20, TEXT, True)
add_text(slide, "6  Open logs and explain the evidence: actor, tenant, action, result, latency, and citations.", 1.0, 5.25, 10.5, 0.45, 17, TEXT, True)
add_text(slide, "Optional follow-up: connect the same tenant-scoped APIs to a Telegram worker after deployment.", 1.0, 6.55, 11.0, 0.3, 12, ACCENT)

slide = base_slide(prs, "Demo credentials and data", "Use these legacy fixtures only for the jury walkthrough; do not use them in production.")
add_card(slide, 0.75, 1.75, 3.8, 3.75, "TechNova Solutions", "Admin: admin@technova.com\nPassword: DemoPass123!\n\nKnowledge: UltraBook Pro X15 hardware manual\n\nAsk: “What is the battery warranty?”")
add_card(slide, 4.8, 1.75, 3.8, 3.75, "GreenLeaf Retail", "Admin: admin@greenleaf.com\nPassword: DemoPass123!\n\nKnowledge: customer refund and return policy\n\nAsk: “What is the return window?”")
add_card(slide, 8.85, 1.75, 3.8, 3.75, "Best demo sequence", "Login as TechNova → ask a warranty question → inspect citation → switch to GreenLeaf → verify invisibility → run the IDOR simulator → inspect logs.")
add_text(slide, "These accounts are presentation fixtures and intentionally remain unchanged by request.", 1.0, 6.15, 11.2, 0.35, 13, MUTED, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "Deployment and testing", "Move from local proof to a repeatable production setup.")
add_card(slide, 0.75, 1.75, 3.8, 3.75, "Local stack", "Next.js at :3000\nFastAPI at :8001\nSQLite for zero-dependency development\nPytest for API and isolation checks\n\nFast feedback: run frontend and backend independently.")
add_card(slide, 4.8, 1.75, 3.8, 3.75, "Production shape", "Render frontend + backend\nManaged PostgreSQL/pgvector\nSMTP provider\nPersistent object storage\nEnvironment-managed secrets\n\nScale path: worker service for async processing.")
add_card(slide, 8.85, 1.75, 3.8, 3.75, "Release gates", "Health endpoint\nStrict CORS\nNo development reload\nRegistration and OTP test\nTenant isolation regression test\n\nGate: no deployment is called complete until login and chat work.")

slide = base_slide(prs, "API and observability", "The platform exposes clear boundaries for UI, integrations, and operators.")
add_card(slide, 0.75, 1.75, 3.8, 3.8, "Auth APIs", "register\nverify-email\nresend-verification\nlogin\nme\n\nBoundary: public registration ends at verified identity.")
add_card(slide, 4.8, 1.75, 3.8, 3.8, "Knowledge APIs", "documents\nupload\ninspect/delete document\nchat message\nconversation history\n\nBoundary: all resources resolve through tenant ownership.")
add_card(slide, 8.85, 1.75, 3.8, 3.8, "Operator APIs", "logs and telemetry\nadmin stats\ntenant summaries\nprovision tenants\nsecurity simulation\n\nBoundary: global views require SuperAdmin role.")
add_text(slide, "Every sensitive operation is measurable: actor, tenant, action, outcome, latency, and resource context.", 0.95, 6.15, 11.4, 0.35, 14, ACCENT, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "Evaluation snapshot", "How the implementation maps to a jury rubric.")
add_card(slide, 0.75, 1.75, 3.8, 3.85, "Working MVP", "Authentication, document upload, RAG chat, citations, tenant dashboards, logs, and an interactive security demo.\n\nProof: local backend tests pass and the production frontend build generates 16 routes.")
add_card(slide, 4.8, 1.75, 3.8, 3.85, "Differentiation", "Security is visible and testable: out-of-domain refusal, tenant-scoped retrieval, 404 IDOR protection, and audit evidence.\n\nProof: the jury can trigger and inspect the denial.")
add_card(slide, 8.85, 1.75, 3.8, 3.85, "Business value", "Reusable company knowledge, faster support decisions, lower information risk, and a path to per-tenant SaaS pricing.\n\nModel: charge per workspace, seats, storage, or usage.")
add_text(slide, "Honest status: deployment verification, object storage, OCR, and formal migrations remain production follow-up work.", 0.9, 6.15, 11.5, 0.4, 13, MUTED, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "Data model and isolation boundary", "Tenant identity is carried through every relationship that contains private knowledge.")
add_card(slide, 0.55, 1.7, 2.35, 3.95, "Tenant", "Company workspace\nSlug and quota\nAdmin membership\nOwns all private records\n\nBoundary: root of ownership.")
add_card(slide, 3.05, 1.7, 2.35, 3.95, "User", "Email and password hash\nVerified status\nRole: admin/user\nBelongs to one tenant\n\nBoundary: JWT carries identity.")
add_card(slide, 5.55, 1.7, 2.35, 3.95, "Document", "Tenant-owned file\nPENDING → READY\nParser metadata\nSafe deletion boundary\n\nBoundary: status gates retrieval.")
add_card(slide, 8.05, 1.7, 2.35, 3.95, "Chunks", "Text segments\nEmbedding vectors\nPage/source metadata\nTenant-scoped retrieval\n\nBoundary: no global search.")
add_card(slide, 10.55, 1.7, 2.35, 3.95, "Conversation", "Tenant-owned thread\nMessages and citations\nAudit-linked question\nNo cross-tenant joins\n\nBoundary: history stays private.")
add_text(slide, "Security invariant: a valid resource ID is not sufficient; the authenticated tenant must also own the resource.", 0.85, 6.15, 11.6, 0.4, 15, ACCENT, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "Request security flow", "A typical chat request is authorized before retrieval or generation.")
steps = ["JWT\nverified", "User + role\nloaded", "Tenant ID\nresolved", "Documents\nfiltered", "Chunks\nretrieved", "Answer +\ncitations", "Audit\nwritten"]
for i, step in enumerate(steps):
    x = 0.45 + i * 1.82
    add_card(slide, x, 2.1, 1.5, 1.65, str(i + 1), step)
add_text(slide, "Client input: question only. Tenant identity, ownership, and authorization are server decisions.", 1.0, 4.65, 11.2, 0.45, 17, TEXT, False, PP_ALIGN.CENTER)
add_text(slide, "Failure paths are explicit: 401 unauthenticated, 403 insufficient role, 404 hidden cross-tenant resource, or a grounded refusal.", 0.9, 5.55, 11.5, 0.5, 15, ACCENT, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "Telegram assistant", "The bot uses the same tenant-scoped backend concepts instead of creating a second data silo.")
add_card(slide, 0.75, 1.75, 3.8, 3.85, "Authentication", "/start and login flow\nTenant-aware Telegram session\n120-second sliding inactivity timeout\nSession state persisted in the database\n\nBehavior: activity refreshes the window; only inactivity expires it.")
add_card(slide, 4.8, 1.75, 3.8, 3.85, "Commands", "/chat\n/documents\n/upload\n/conversations\n/audits\n/telemetry\n\nResult: the bot exposes the same knowledge workflow through chat.")
add_card(slide, 8.85, 1.75, 3.8, 3.85, "Administration", "/settings\n/setcompany\n/setdomain\nAdmin-only settings changes\nFriendly upload success/failure responses\n\nSafety: failed processing does not expose internal exception details.")
add_text(slide, "Operational rule: every authenticated command refreshes activity; only inactivity expires the session.", 0.95, 6.15, 11.4, 0.35, 14, ACCENT, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "Quality and verification", "Evidence used to reduce regression risk before the jury demo.")
add_card(slide, 0.75, 1.75, 3.8, 3.8, "Backend tests", "Authentication and verification\nTenant authorization\nAdmin access\nDocument lifecycle\nRAG citations\nTelegram session expiry\n\nPurpose: protect security and behavior regressions.")
add_card(slide, 4.8, 1.75, 3.8, 3.8, "Frontend checks", "Production build\n16 generated routes\nAccessible labels and focus states\nResponsive landing/auth flows\nReduced-motion support\n\nPurpose: verify the jury-facing path builds cleanly.")
add_card(slide, 8.85, 1.75, 3.8, 3.8, "Operational checks", "Health endpoint\nStrict CORS defaults\nProduction reload disabled\nGeneric user-facing failures\nDiff and presentation validation\n\nPurpose: avoid demo-only configuration surprises.")
add_text(slide, "The demo separates verified behavior from roadmap items so the jury can evaluate the working MVP honestly.", 0.95, 6.15, 11.4, 0.35, 14, ACCENT, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "Render deployment runbook", "A repeatable path from the repository to a public demo environment.")
add_text(slide, "1  Create Blueprint", 0.9, 1.7, 5.3, 0.45, 19, TEXT, True)
add_text(slide, "Select the repository and apply render.yaml.", 0.9, 2.15, 5.5, 0.35, 14, MUTED)
add_text(slide, "2  Configure secrets", 0.9, 2.85, 5.3, 0.45, 19, TEXT, True)
add_text(slide, "DATABASE_URL, SECRET_KEY, CORS_ORIGINS, SMTP, and Telegram token.", 0.9, 3.3, 5.8, 0.55, 14, MUTED)
add_text(slide, "3  Seed and verify", 0.9, 4.0, 5.3, 0.45, 19, TEXT, True)
add_text(slide, "Run the explicit jury seed command, then test health, login, upload, chat, and logs.", 0.9, 4.45, 6.0, 0.7, 14, MUTED)
add_card(slide, 7.3, 1.7, 5.2, 3.7, "Production checklist", "Frontend URL added to backend CORS\nManaged PostgreSQL connected\nPersistent file storage selected\nSMTP delivery verified\nSecrets stored in Render, not Git\nWorker health and logs monitored\n\nSmoke test: health → register → verify → login → upload → chat → logs.")
add_text(slide, "Deployment is an operator-controlled step; no paid or irreversible action is performed by the application.", 0.9, 6.2, 11.5, 0.35, 14, ACCENT, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "Risks and mitigations", "The design acknowledges what can fail and how the platform responds.")
add_card(slide, 0.75, 1.75, 3.8, 3.85, "Hallucination risk", "Mitigation: tenant-scoped retrieval, grounded prompts, citations, and explicit out-of-domain refusal.")
add_card(slide, 4.8, 1.75, 3.8, 3.85, "Data leakage risk", "Mitigation: server-side tenant filters, hidden 404 responses, role guards, audit events, and IDOR simulation.")
add_card(slide, 8.85, 1.75, 3.8, 3.85, "Production scale risk", "Mitigation roadmap: Alembic migrations, object storage, async workers, OCR, rate limits, and managed observability.")
add_text(slide, "Security is treated as a product feature and an observable operating process, not a UI promise.", 0.95, 6.15, 11.4, 0.35, 14, ACCENT, False, PP_ALIGN.CENTER)

slide = base_slide(prs, "Jury questions: concise answers", "Use this slide as a speaker prompt during evaluation.")
add_card(slide, 0.65, 1.7, 2.85, 4.0, "Why multi-tenant?", "A company assistant must be useful without mixing confidential workspaces. Tenant scope is enforced in backend queries.")
add_card(slide, 3.65, 1.7, 2.85, 4.0, "Why RAG?", "Company policies change. Retrieval grounds answers in the latest approved documents instead of model memory.")
add_card(slide, 6.65, 1.7, 2.85, 4.0, "How do you prove security?", "Run the IDOR simulator, observe 404 and zero leaked bytes, then inspect the audit event.")
add_card(slide, 9.65, 1.7, 2.85, 4.0, "What is next?", "Production migrations, storage, OCR, async processing, and verified Render rollout.")

slide = base_slide(prs, "Conclusion and roadmap", "Secure foundations first; integrate only what can be verified.")
add_card(slide, 0.75, 1.8, 3.8, 3.6, "Now", "Tenant-scoped FastAPI APIs, grounded RAG, OTP registration, dark-first auth UI, audit telemetry.")
add_card(slide, 4.8, 1.8, 3.8, 3.6, "Next", "Complete Telegram account linking and 120-second session enforcement on a shared bot service.")
add_card(slide, 8.85, 1.8, 3.8, 3.6, "Future", "Async workers, OCR, object storage, richer feedback/export, and managed deployment verification.")
add_text(slide, "Build trust into the architecture, then make the demo visible.", 1.0, 6.25, 11.2, 0.4, 18, ACCENT, True, PP_ALIGN.CENTER)

prs.save(OUT)
print(OUT)

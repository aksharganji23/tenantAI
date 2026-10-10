import os
import json
import time
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.models.tenant import Tenant
from app.models.user import User
from app.models.document import Document, DocumentChunk
from app.models.conversation import Conversation, Message
from app.models.usage_log import UsageLog
from app.api.deps import get_password_hash
from app.services.document_parser import extract_text_from_txt, chunk_pages_text
from app.services.embeddings import get_embedding


JURY_PASSWORD = "DemoPass123!"


def run_seed(db: Session = None):
    """Seed demo tenants, users, sample documents, chunks, and logs."""
    close_db_after = False
    if db is None:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        close_db_after = True

    try:
        print("[Seed] Initializing database schema...")
        Base.metadata.create_all(bind=engine)

        # 1. Create or get Tenants
        technova = db.query(Tenant).filter(Tenant.slug == "technova").first()
        if not technova:
            technova = Tenant(
                name="TechNova Solutions",
                slug="technova",
                domain="technova.io",
                plan="enterprise",
                quota_docs=100,
                quota_queries=10000
            )
            db.add(technova)
            db.commit()
            db.refresh(technova)
            print("[Seed] Created Tenant: TechNova Solutions")

        greenleaf = db.query(Tenant).filter(Tenant.slug == "greenleaf").first()
        if not greenleaf:
            greenleaf = Tenant(
                name="GreenLeaf Retail",
                slug="greenleaf",
                domain="greenleafretail.com",
                plan="growth",
                quota_docs=50,
                quota_queries=5000
            )
            db.add(greenleaf)
            db.commit()
            db.refresh(greenleaf)
            print("[Seed] Created Tenant: GreenLeaf Retail")

        # 2. Create Users
        demo_password_hash = get_password_hash("DemoPass123!")
        super_password_hash = get_password_hash("SuperAdmin123!")

        users_to_seed = [
            {
                "email": "admin@tenantai.com",
                "hashed_password": super_password_hash,
                "full_name": "Antigravity Global Admin",
                "role": "superadmin",
                "tenant_id": technova.id,  # superadmin can switch workspaces
                "is_verified": True,
            },
            {
                "email": "admin@technova.com",
                "hashed_password": demo_password_hash,
                "full_name": "Marcus Vance (TechNova Admin)",
                "role": "tenant_admin",
                "tenant_id": technova.id,
                "is_verified": True,
            },
            {
                "email": "user@technova.com",
                "hashed_password": demo_password_hash,
                "full_name": "Sophia Chen (TechNova Engineer)",
                "role": "tenant_user",
                "tenant_id": technova.id,
                "is_verified": True,
            },
            {
                "email": "admin@greenleaf.com",
                "hashed_password": demo_password_hash,
                "full_name": "Elena Rostova (GreenLeaf Ops)",
                "role": "tenant_admin",
                "tenant_id": greenleaf.id,
                "is_verified": True,
            },
            {
                "email": "user@greenleaf.com",
                "hashed_password": demo_password_hash,
                "full_name": "Liam Thorne (GreenLeaf Support)",
                "role": "tenant_user",
                "tenant_id": greenleaf.id,
                "is_verified": True,
            }
        ]

        for u in users_to_seed:
            existing_user = db.query(User).filter(User.email == u["email"]).first()
            if not existing_user:
                new_user = User(
                    email=u["email"],
                    hashed_password=u["hashed_password"],
                    full_name=u["full_name"],
                    role=u["role"],
                    tenant_id=u["tenant_id"],
                    is_verified=u["is_verified"],
                    is_active=True
                )
                db.add(new_user)
                print(f"[Seed] Created User: {u['email']} ({u['role']})")
        db.commit()

        # 3. Seed TechNova Document (Laptop Manual)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        technova_file_path = os.path.join(current_dir, "data", "technova_laptop_manual.txt")

        existing_tn_doc = db.query(Document).filter(
            Document.tenant_id == technova.id,
            Document.filename == "TechNova_UltraBook_Pro_Manual.txt"
        ).first()

        if not existing_tn_doc and os.path.exists(technova_file_path):
            file_size = os.path.getsize(technova_file_path)
            doc_tn = Document(
                tenant_id=technova.id,
                filename="TechNova_UltraBook_Pro_Manual.txt",
                file_path=technova_file_path,
                file_type="txt",
                file_size=file_size,
                title="TechNova UltraBook Pro X15 Hardware Manual",
                status="READY",
                chunk_count=0
            )
            db.add(doc_tn)
            db.commit()
            db.refresh(doc_tn)

            pages = extract_text_from_txt(technova_file_path)
            chunks = chunk_pages_text(pages)
            for ch in chunks:
                emb = get_embedding(ch["content"])
                chunk_rec = DocumentChunk(
                    document_id=doc_tn.id,
                    tenant_id=technova.id,
                    chunk_index=ch["chunk_index"],
                    content=ch["content"],
                    page_number=ch["page_number"],
                    token_count=ch["token_count"],
                    embedding=json.dumps(emb)
                )
                db.add(chunk_rec)
            doc_tn.chunk_count = len(chunks)
            db.commit()
            print(f"[Seed] Seeded TechNova Manual with {len(chunks)} chunks.")

        # 4. Seed GreenLeaf Document (Refund Policy)
        greenleaf_file_path = os.path.join(current_dir, "data", "greenleaf_refund_policy.txt")
        existing_gl_doc = db.query(Document).filter(
            Document.tenant_id == greenleaf.id,
            Document.filename == "GreenLeaf_Retail_Refund_Policy.txt"
        ).first()

        if not existing_gl_doc and os.path.exists(greenleaf_file_path):
            file_size = os.path.getsize(greenleaf_file_path)
            doc_gl = Document(
                tenant_id=greenleaf.id,
                filename="GreenLeaf_Retail_Refund_Policy.txt",
                file_path=greenleaf_file_path,
                file_type="txt",
                file_size=file_size,
                title="GreenLeaf Customer Refund & Return Policy",
                status="READY",
                chunk_count=0
            )
            db.add(doc_gl)
            db.commit()
            db.refresh(doc_gl)

            pages = extract_text_from_txt(greenleaf_file_path)
            chunks = chunk_pages_text(pages)
            for ch in chunks:
                emb = get_embedding(ch["content"])
                chunk_rec = DocumentChunk(
                    document_id=doc_gl.id,
                    tenant_id=greenleaf.id,
                    chunk_index=ch["chunk_index"],
                    content=ch["content"],
                    page_number=ch["page_number"],
                    token_count=ch["token_count"],
                    embedding=json.dumps(emb)
                )
                db.add(chunk_rec)
            doc_gl.chunk_count = len(chunks)
            db.commit()
            print(f"[Seed] Seeded GreenLeaf Refund Policy with {len(chunks)} chunks.")

        # 5. Seed Realistic Telemetry Logs
        initial_log_count = db.query(UsageLog).count()
        if initial_log_count < 4:
            sample_logs = [
                UsageLog(
                    tenant_id=technova.id,
                    user_email="admin@technova.com",
                    action="login",
                    outcome="SUCCESS",
                    latency_ms=45,
                    details="Admin login session initialized",
                    ip_address="192.168.1.10"
                ),
                UsageLog(
                    tenant_id=technova.id,
                    user_email="user@technova.com",
                    action="chat_query",
                    outcome="SUCCESS",
                    latency_ms=180,
                    tokens_used=142,
                    model_name="Local-Grounded-RAG",
                    details="Q: 'What is the warranty coverage for the battery?' | Citations: 1",
                    ip_address="192.168.1.15"
                ),
                UsageLog(
                    tenant_id=greenleaf.id,
                    user_email="admin@greenleaf.com",
                    action="doc_upload",
                    outcome="SUCCESS",
                    latency_ms=210,
                    details="Uploaded 'GreenLeaf_Retail_Refund_Policy.txt'",
                    ip_address="10.0.4.20"
                ),
                UsageLog(
                    tenant_id=greenleaf.id,
                    user_email="user@greenleaf.com",
                    action="chat_query",
                    outcome="SUCCESS",
                    latency_ms=165,
                    tokens_used=115,
                    model_name="Local-Grounded-RAG",
                    details="Q: 'What is the return window for purchases?' | Citations: 1",
                    ip_address="10.0.4.22"
                )
            ]
            db.add_all(sample_logs)
            db.commit()
            print("[Seed] Seeded baseline telemetry logs.")

        # 6. Seed tenant-scoped conversation history for the jury dashboard.
        # Conversations are keyed by title and user so this remains safe to rerun.
        demo_conversations = [
            {
                "tenant": technova,
                "email": "admin@technova.com",
                "title": "UltraBook warranty coverage",
                "question": "What is the warranty coverage for the battery?",
                "answer": (
                    "The TechNova UltraBook Pro X15 includes a 36-month chassis warranty "
                    "and a 24-month battery replacement guarantee."
                ),
                "document_title": "TechNova UltraBook Pro X15 Hardware Manual",
            },
            {
                "tenant": technova,
                "email": "user@technova.com",
                "title": "UltraBook battery care",
                "question": "How should the UltraBook battery be maintained?",
                "answer": (
                    "For best battery life, keep the device in a cool, dry environment, "
                    "avoid blocking ventilation, and use the approved USB-C charger."
                ),
                "document_title": "TechNova UltraBook Pro X15 Hardware Manual",
            },
            {
                "tenant": greenleaf,
                "email": "admin@greenleaf.com",
                "title": "Customer refund window",
                "question": "What is the return window for purchases?",
                "answer": (
                    "GreenLeaf accepts eligible returns within 30 days of purchase when "
                    "the customer provides a valid receipt and the item is in resalable condition."
                ),
                "document_title": "GreenLeaf Customer Refund & Return Policy",
            },
            {
                "tenant": greenleaf,
                "email": "user@greenleaf.com",
                "title": "Restocking fee policy",
                "question": "When does GreenLeaf charge a restocking fee?",
                "answer": (
                    "A restocking fee may apply to opened or used items unless the return "
                    "is due to a verified product defect."
                ),
                "document_title": "GreenLeaf Customer Refund & Return Policy",
            },
        ]

        for item in demo_conversations:
            user = (
                db.query(User)
                .filter(
                    User.email == item["email"],
                    User.tenant_id == item["tenant"].id,
                )
                .first()
            )
            document = (
                db.query(Document)
                .filter(
                    Document.tenant_id == item["tenant"].id,
                    Document.title == item["document_title"],
                    Document.status == "READY",
                )
                .first()
            )
            if not user or not document:
                continue

            existing_conversation = (
                db.query(Conversation)
                .filter(
                    Conversation.tenant_id == item["tenant"].id,
                    Conversation.user_id == user.id,
                    Conversation.title == item["title"],
                )
                .first()
            )
            if existing_conversation:
                continue

            conversation = Conversation(
                tenant_id=item["tenant"].id,
                user_id=user.id,
                title=item["title"],
            )
            db.add(conversation)
            db.flush()
            citation = json.dumps(
                [
                    {
                        "document_title": document.title,
                        "page_number": 1,
                        "excerpt": item["answer"],
                        "relevance_score": 0.98,
                    }
                ]
            )
            db.add_all(
                [
                    Message(
                        conversation_id=conversation.id,
                        tenant_id=item["tenant"].id,
                        sender="user",
                        content=item["question"],
                    ),
                    Message(
                        conversation_id=conversation.id,
                        tenant_id=item["tenant"].id,
                        sender="assistant",
                        content=item["answer"],
                        citations=citation,
                        confidence_score=0.98,
                        latency_ms=180,
                        tokens_used=48,
                    ),
                ]
            )
            print(f"[Seed] Created conversation: {item['title']} ({item['tenant'].slug})")
        db.commit()

        print("[Seed] Seed data successfully applied!")

    finally:
        if close_db_after:
            db.close()


if __name__ == "__main__":
    run_seed()

"""Telegram interface for the shared SaaSum AI backend and database.

Run from backend/ with:
    python telegram_bot.py

The bot never stores Telegram passwords. A successful /login creates a database
session bound to the Telegram chat ID and expires it after inactivity.
"""

import asyncio
import json
import logging
import os
import re
import time
from datetime import datetime, timedelta
from typing import Optional

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.api.deps import verify_password
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import Conversation, Document, DocumentChunk, Message, TelegramSession, Tenant, UsageLog, User
from app.services.audit_logger import log_event
from app.services.document_parser import chunk_pages_text, extract_text_from_pdf, extract_text_from_txt
from app.services.embeddings import get_embedding
from app.services.rag_engine import run_rag_query

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("saasum.telegram")

LOGIN_EMAIL = "telegram_login_email"
LOGIN_PASSWORD = "telegram_login_password"


def now() -> datetime:
    return datetime.utcnow()


def get_session(chat_id: int, db) -> Optional[TelegramSession]:
    session = db.query(TelegramSession).filter(TelegramSession.telegram_chat_id == chat_id).first()
    if not session:
        return None
    current_time = now()
    inactivity_limit = timedelta(seconds=settings.TELEGRAM_SESSION_TIMEOUT_SECONDS)
    if current_time - session.last_activity_at >= inactivity_limit:
        db.delete(session)
        db.commit()
        return None
    # Sliding expiration: every authenticated update gets a fresh inactivity window.
    session.last_activity_at = current_time
    session.expires_at = current_time + inactivity_limit
    db.commit()
    return session


def expired_message() -> str:
    return "Your session expired due to inactivity. Please log in again to continue."


def command_list() -> str:
    return (
        "Available commands:\n"
        "/status - account, company, and session status\n"
        "/documents - list your company's documents\n"
        "/upload - upload a PDF, TXT, or MD file, then send it as a Telegram document\n"
        "/conversations - list your saved chat conversations\n"
        "/audits - show recent audit and telemetry events\n"
        "/settings - show company settings\n"
        "/setcompany <name> - rename the company (tenant admins only)\n"
        "/setdomain <domain> - change the company domain (tenant admins only)\n"
        "/help - show this command list\n"
        "/logout - revoke this Telegram session\n\n"
        "You can also send any document question as plain text."
    )


def with_command_list(message: str) -> str:
    return f"{message}\n\nAvailable commands:\n\n{command_list()}"


def authenticated_context(chat_id: int):
    """Return an active session, user, and database session for one Telegram chat."""
    db = SessionLocal()
    session = get_session(chat_id, db)
    if not session:
        db.close()
        return None, None, db
    user = (
        db.query(User)
        .filter(
            User.id == session.user_id,
            User.tenant_id == session.tenant_id,
            User.is_active.is_(True),
            User.is_verified.is_(True),
        )
        .first()
    )
    if not user:
        db.delete(session)
        db.commit()
        db.close()
        return None, None, None
    return session, user, db


async def require_login(update: Update):
    session, user, db = authenticated_context(update.effective_chat.id)
    if not session or not user:
        await update.message.reply_text(expired_message())
        return None, None, db
    return session, user, db


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome to tenantAI.\n\n"
        "Use /login to authenticate with your verified company account.\n"
        "After login, manage documents, telemetry, company settings, and chat "
        "from Telegram.\n\n"
        + command_list()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(command_list())


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    context.user_data[LOGIN_EMAIL] = True
    await update.message.reply_text("Enter your verified application email address:")


async def handle_login_or_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip()
    chat_id = update.effective_chat.id

    if context.user_data.get(LOGIN_EMAIL) is True:
        context.user_data[LOGIN_EMAIL] = text.lower()
        context.user_data[LOGIN_PASSWORD] = True
        await update.message.reply_text("Enter your application password. It is used only for this login attempt:")
        return

    if context.user_data.get(LOGIN_PASSWORD) is True:
        email = context.user_data.get(LOGIN_EMAIL)
        context.user_data.clear()
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user or not verify_password(text, user.hashed_password):
                await update.message.reply_text("Incorrect email or password. Use /login to try again.")
                return
            if not user.is_active:
                await update.message.reply_text("This application account is disabled.")
                return
            if not user.is_verified:
                await update.message.reply_text("Verify your email in the web application before using Telegram.")
                return
            if not user.tenant_id:
                await update.message.reply_text("This account is not assigned to a company workspace.")
                return

            existing = db.query(TelegramSession).filter(TelegramSession.telegram_chat_id == chat_id).first()
            if existing:
                db.delete(existing)
                db.flush()
            created = now()
            session = TelegramSession(
                telegram_chat_id=chat_id,
                user_id=user.id,
                tenant_id=user.tenant_id,
                authenticated_at=created,
                last_activity_at=created,
                expires_at=created + timedelta(seconds=settings.TELEGRAM_SESSION_TIMEOUT_SECONDS),
            )
            db.add(session)
            db.commit()
            log_event(db, user.tenant_id, user.id, user.email, "telegram_login", "SUCCESS", details="Telegram session authenticated")
            await update.message.reply_text(
                f"Authenticated for {user.tenant.name if user.tenant else 'your company'}. "
                f"Your session expires after {settings.TELEGRAM_SESSION_TIMEOUT_SECONDS} seconds of inactivity.\n\n"
                "Here are the available commands:\n\n"
                + command_list()
            )
        finally:
            db.close()
        return

    session, user, db = authenticated_context(chat_id)
    if not session or not user:
        await update.message.reply_text(expired_message())
        return
    try:
        conv = Conversation(
            tenant_id=session.tenant_id,
            user_id=user.id,
            title=text[:40] + ("..." if len(text) > 40 else ""),
        )
        db.add(conv)
        db.flush()
        db.add(Message(conversation_id=conv.id, tenant_id=session.tenant_id, sender="user", content=text))
        result = run_rag_query(db, session.tenant_id, text, top_k=4)
        db.add(Message(
            conversation_id=conv.id,
            tenant_id=session.tenant_id,
            sender="assistant",
            content=result["content"],
            citations=json.dumps(result["citations"]) if result["citations"] else None,
            confidence_score=result["confidence_score"],
            latency_ms=result["latency_ms"],
            tokens_used=result["tokens_used"],
        ))
        db.commit()
        log_event(db, session.tenant_id, user.id, user.email, "telegram_chat_query", "SUCCESS", tokens_used=result["tokens_used"], model_name=result["model_name"], details=f"Question: {text[:100]}")
        citations = ""
        if result["citations"]:
            citations = "\n\nSources:\n" + "\n".join(
                f"- {item['document_title']} (page {item['page_number']})" for item in result["citations"]
            )
        await update.message.reply_text(result["content"] + citations)
    finally:
        db.close()


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session, user, db = await require_login(update)
    if not session or not user:
        if db:
            db.close()
        return
    try:
        tenant_name = user.tenant.name if user and user.tenant else "your company"
        remaining = max(0, int((session.expires_at - now()).total_seconds()))
        await update.message.reply_text(
            f"Authenticated as {user.email}\n"
            f"Company: {tenant_name}\n"
            f"Role: {user.role}\n"
            f"Session remaining: {remaining} seconds"
        )
    finally:
        db.close()


async def documents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session, user, db = await require_login(update)
    if not session or not user:
        if db:
            db.close()
        return
    try:
        items = (
            db.query(Document)
            .filter(Document.tenant_id == session.tenant_id)
            .order_by(Document.created_at.desc())
            .limit(20)
            .all()
        )
        if not items:
            await update.message.reply_text("No documents are uploaded for this company yet.")
            return
        lines = ["Company documents:"]
        for item in items:
            lines.append(f"- {item.title} [{item.status}, {item.chunk_count} chunks]")
        await update.message.reply_text("\n".join(lines))
    finally:
        db.close()


async def upload_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session, user, db = await require_login(update)
    if db:
        db.close()
    if not session or not user:
        return
    await update.message.reply_text(
        "Send a PDF, TXT, or MD file as a Telegram document now. "
        "The file will be processed inside your company workspace."
    )


async def handle_document_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.document:
        return
    session, user, db = await require_login(update)
    if not session or not user:
        if db:
            db.close()
        return
    try:
        telegram_document = update.message.document
        original_name = os.path.basename(telegram_document.file_name or "telegram_upload.txt")
        extension = os.path.splitext(original_name)[1].lower().lstrip(".")
        if extension not in settings.ALLOWED_EXTENSIONS:
            await update.message.reply_text(
                with_command_list(
                    f"Upload unsuccessful.\n"
                    f"Unsupported file type .{extension}. "
                    f"Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
                )
            )
            return
        tenant = db.query(Tenant).filter(Tenant.id == session.tenant_id).first()
        document_count = db.query(Document).filter(Document.tenant_id == session.tenant_id).count()
        if tenant and document_count >= tenant.quota_docs:
            await update.message.reply_text(
                with_command_list(
                    "Upload unsuccessful.\nYour company document quota has been reached."
                )
            )
            return

        storage_dir = os.path.join(settings.STORAGE_DIR, f"tenant_{session.tenant_id}")
        os.makedirs(storage_dir, exist_ok=True)
        clean_name = re.sub(r"[^A-Za-z0-9_.-]", "_", original_name)
        saved_path = os.path.join(storage_dir, f"{int(time.time())}_{clean_name}")
        telegram_file = await telegram_document.get_file()
        await telegram_file.download_to_drive(saved_path)
        file_size = os.path.getsize(saved_path)
        if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
            os.remove(saved_path)
            await update.message.reply_text(
                with_command_list(
                    "Upload unsuccessful.\nThe file exceeds the maximum upload size."
                )
            )
            return

        record = Document(
            tenant_id=session.tenant_id,
            filename=original_name,
            file_path=saved_path,
            file_type=extension,
            file_size=file_size,
            title=os.path.splitext(original_name)[0].replace("_", " "),
            status="PROCESSING",
            chunk_count=0,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        try:
            pages = extract_text_from_pdf(saved_path) if extension == "pdf" else extract_text_from_txt(saved_path)
            chunks = chunk_pages_text(pages)
            if not chunks:
                raise ValueError("No extractable text found in the file.")
            for chunk in chunks:
                db.add(
                    DocumentChunk(
                        document_id=record.id,
                        tenant_id=session.tenant_id,
                        chunk_index=chunk["chunk_index"],
                        content=chunk["content"],
                        page_number=chunk["page_number"],
                        token_count=chunk["token_count"],
                        embedding=json.dumps(get_embedding(chunk["content"])),
                    )
                )
            record.status = "READY"
            record.chunk_count = len(chunks)
            db.commit()
            log_event(
                db,
                session.tenant_id,
                user.id,
                user.email,
                "telegram_doc_upload",
                "SUCCESS",
                details=f"Uploaded '{original_name}' ({len(chunks)} chunks)",
            )
            await update.message.reply_text(
                with_command_list(
                    f"Upload successful.\n"
                    f"Document: {record.title}\n"
                    f"Status: READY\n"
                    f"Chunks: {record.chunk_count}"
                )
            )
        except Exception as error:
            record.status = "FAILED"
            record.error_message = str(error)
            db.commit()
            log_event(
                db,
                session.tenant_id,
                user.id,
                user.email,
                "telegram_doc_upload",
                "ERROR",
                details=f"Failed processing '{original_name}': {error}",
            )
            await update.message.reply_text(
                with_command_list(
                    f"Upload unsuccessful.\nDocument processing failed: {error}"
                )
            )
    except Exception as error:
        logger.exception("Telegram document upload failed")
        await update.message.reply_text(
            with_command_list(f"Upload unsuccessful.\nCould not receive the file: {error}")
        )
    finally:
        db.close()


async def conversations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session, user, db = await require_login(update)
    if not session or not user:
        if db:
            db.close()
        return
    try:
        items = (
            db.query(Conversation)
            .filter(Conversation.tenant_id == session.tenant_id, Conversation.user_id == user.id)
            .order_by(Conversation.updated_at.desc())
            .limit(20)
            .all()
        )
        if not items:
            await update.message.reply_text("No saved conversations yet.")
            return
        await update.message.reply_text(
            "Your saved conversations:\n" + "\n".join(
                f"- #{item.id}: {item.title}" for item in items
            )
        )
    finally:
        db.close()


async def audits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session, user, db = await require_login(update)
    if not session or not user:
        if db:
            db.close()
        return
    try:
        items = (
            db.query(UsageLog)
            .filter(UsageLog.tenant_id == session.tenant_id)
            .order_by(UsageLog.created_at.desc())
            .limit(10)
            .all()
        )
        if not items:
            await update.message.reply_text("No audit or telemetry events found.")
            return
        lines = ["Recent audit & telemetry:"]
        for item in items:
            details = (item.details or "").replace("\n", " ")[:100]
            lines.append(f"- {item.action} | {item.outcome} | {details}")
        await update.message.reply_text("\n".join(lines))
    finally:
        db.close()


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session, user, db = await require_login(update)
    if not session or not user:
        if db:
            db.close()
        return
    try:
        tenant = db.query(Tenant).filter(Tenant.id == session.tenant_id).first()
        await update.message.reply_text(
            f"Company settings\n"
            f"Name: {tenant.name}\n"
            f"Domain: {tenant.domain or 'not set'}\n"
            f"Plan: {tenant.plan}\n"
            f"Document quota: {tenant.quota_docs}\n"
            f"Query quota: {tenant.quota_queries}\n\n"
            "Tenant admins can use /setcompany <name> and /setdomain <domain>."
        )
    finally:
        db.close()


async def set_company(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update_tenant_field(update, context, "name", "company name")


async def set_domain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update_tenant_field(update, context, "domain", "domain")


async def update_tenant_field(update: Update, context: ContextTypes.DEFAULT_TYPE, field: str, label: str) -> None:
    session, user, db = await require_login(update)
    if not session or not user:
        if db:
            db.close()
        return
    try:
        if user.role not in {"tenant_admin", "superadmin"}:
            await update.message.reply_text("Only a tenant admin can modify company settings.")
            return
        value = " ".join(context.args).strip()
        if not value:
            await update.message.reply_text(f"Usage: /{update.effective_message.text.split()[0][1:]} <{label}>")
            return
        if field == "name" and len(value) > 255:
            await update.message.reply_text("The company name is too long.")
            return
        tenant = db.query(Tenant).filter(Tenant.id == session.tenant_id).first()
        setattr(tenant, field, value)
        db.commit()
        log_event(db, session.tenant_id, user.id, user.email, "tenant_settings_update", "SUCCESS", details=f"Updated {field} via Telegram")
        await update.message.reply_text(f"Company {label} updated to: {value}")
    finally:
        db.close()


async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = SessionLocal()
    try:
        session = db.query(TelegramSession).filter(TelegramSession.telegram_chat_id == update.effective_chat.id).first()
        if session:
            user = db.query(User).filter(User.id == session.user_id).first()
            db.delete(session)
            db.commit()
            if user:
                log_event(db, user.tenant_id, user.id, user.email, "telegram_logout", "SUCCESS", details="Telegram session revoked")
        await update.message.reply_text("Telegram session logged out.")
    finally:
        db.close()


async def post_init(application) -> None:
    await application.bot.set_my_commands(
        [
            ("start", "Start tenantAI"),
            ("help", "Show all available commands"),
            ("status", "Show account and company status"),
            ("documents", "List company documents"),
            ("upload", "Upload a PDF, TXT, or MD file"),
            ("conversations", "List saved chatbot conversations"),
            ("audits", "Show audit and telemetry events"),
            ("settings", "Show company settings"),
            ("setcompany", "Update company name"),
            ("setdomain", "Update company domain"),
            ("logout", "Log out of Telegram"),
        ]
    )


def main() -> None:
    if not settings.TELEGRAM_BOT_TOKEN or settings.TELEGRAM_BOT_TOKEN.startswith("replace-with"):
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN in backend/.env before starting the bot.")
    Base.metadata.create_all(bind=engine)
    application = (
        ApplicationBuilder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("login", login))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("documents", documents))
    application.add_handler(CommandHandler("upload", upload_prompt))
    application.add_handler(CommandHandler("conversations", conversations))
    application.add_handler(CommandHandler(["audits", "telemetry"], audits))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("setcompany", set_company))
    application.add_handler(CommandHandler("setdomain", set_domain))
    application.add_handler(CommandHandler("logout", logout))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document_upload))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_login_or_question))
    logger.info("SaaSum AI Telegram bot started with %s-second inactivity sessions", settings.TELEGRAM_SESSION_TIMEOUT_SECONDS)
    # Python 3.14 no longer creates a default event loop for the main thread.
    asyncio.set_event_loop(asyncio.new_event_loop())
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

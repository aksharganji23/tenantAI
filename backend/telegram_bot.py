"""Telegram interface for the shared SaaSsum AI backend and database.

Run from backend/ with:
    python telegram_bot.py

The bot never stores Telegram passwords. A successful /login creates a database
session bound to the Telegram chat ID and expires it after inactivity.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from app.api.deps import verify_password
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import Conversation, Message, TelegramSession, User
from app.services.audit_logger import log_event
from app.services.rag_engine import run_rag_query

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("saassum.telegram")

LOGIN_EMAIL = "telegram_login_email"
LOGIN_PASSWORD = "telegram_login_password"


def now() -> datetime:
    return datetime.utcnow()


def get_session(chat_id: int, db) -> Optional[TelegramSession]:
    session = db.query(TelegramSession).filter(TelegramSession.telegram_chat_id == chat_id).first()
    if not session:
        return None
    if session.expires_at <= now():
        db.delete(session)
        db.commit()
        return None
    session.last_activity_at = now()
    session.expires_at = now() + timedelta(seconds=settings.TELEGRAM_SESSION_TIMEOUT_SECONDS)
    db.commit()
    return session


def expired_message() -> str:
    return "Your session expired due to inactivity. Please log in again to continue."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome to SaaSsum AI.\n\n"
        "Use /login to authenticate with your verified company account.\n"
        "Then send a question about your company's uploaded documents.\n\n"
        "Commands: /login, /status, /help, /logout"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/login - authenticate your verified application account\n"
        "/status - show session status and company\n"
        "/logout - revoke this Telegram session\n"
        "/help - show this help\n\n"
        "After login, send a plain-text question about authorized company documents."
    )


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
                f"Your session expires after {settings.TELEGRAM_SESSION_TIMEOUT_SECONDS} seconds of inactivity."
            )
        finally:
            db.close()
        return

    db = SessionLocal()
    try:
        session = get_session(chat_id, db)
        if not session:
            await update.message.reply_text(expired_message())
            return

        user = db.query(User).filter(User.id == session.user_id, User.tenant_id == session.tenant_id).first()
        if not user or not user.is_active or not user.is_verified:
            db.delete(session)
            db.commit()
            await update.message.reply_text("Your account is no longer authorized. Please log in again.")
            return

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
    db = SessionLocal()
    try:
        session = get_session(update.effective_chat.id, db)
        if not session:
            await update.message.reply_text("Not authenticated. Use /login to connect your company account.")
            return
        user = db.query(User).filter(User.id == session.user_id, User.tenant_id == session.tenant_id).first()
        tenant_name = user.tenant.name if user and user.tenant else "your company"
        remaining = max(0, int((session.expires_at - now()).total_seconds()))
        await update.message.reply_text(f"Authenticated as {user.email} for {tenant_name}.\nSession remaining: {remaining} seconds.")
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


def main() -> None:
    if not settings.TELEGRAM_BOT_TOKEN or settings.TELEGRAM_BOT_TOKEN.startswith("replace-with"):
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN in backend/.env before starting the bot.")
    Base.metadata.create_all(bind=engine)
    application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("login", login))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("logout", logout))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_login_or_question))
    logger.info("SaaSsum AI Telegram bot started with %s-second inactivity sessions", settings.TELEGRAM_SESSION_TIMEOUT_SECONDS)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

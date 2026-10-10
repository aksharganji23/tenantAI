import json
import time
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.conversation import Conversation, Message
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.chat import (
    ChatRequest, ChatResponse, ConversationResponse, MessageResponse, Citation
)
from app.api.deps import get_current_user, get_current_tenant_id
from app.services.rag_engine import run_rag_query
from app.services.audit_logger import log_event

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/message", response_model=ChatResponse)
def send_chat_message(
    chat_req: ChatRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Execute tenant-isolated RAG chat query.
    Retrieves knowledge strictly from caller's tenant documents.
    """
    start_time = time.time()
    client_ip = request.client.host if request.client else None

    # Verify or resolve conversation
    conv: Optional[Conversation] = None
    if chat_req.conversation_id:
        conv = db.query(Conversation).filter(
            Conversation.id == chat_req.conversation_id,
            Conversation.tenant_id == tenant_id
        ).first()

        if not conv:
            # Check for cross-tenant breach attempt
            cross_conv = db.query(Conversation).filter(Conversation.id == chat_req.conversation_id).first()
            if cross_conv:
                log_event(
                    db=db,
                    tenant_id=tenant_id,
                    user_id=current_user.id,
                    user_email=current_user.email,
                    action="cross_tenant_denied",
                    outcome="FORBIDDEN",
                    details=f"Cross-tenant conversation access attempt on conv_id {chat_req.conversation_id} (belongs to tenant {cross_conv.tenant_id})",
                    ip_address=client_ip
                )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        # Create new conversation
        title_snippet = chat_req.message.strip()[:40]
        conv_title = title_snippet + ("..." if len(chat_req.message) > 40 else "")
        conv = Conversation(
            tenant_id=tenant_id,
            user_id=current_user.id,
            title=conv_title
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # Record User Message
    user_msg = Message(
        conversation_id=conv.id,
        tenant_id=tenant_id,
        sender="user",
        content=chat_req.message
    )
    db.add(user_msg)
    db.commit()

    # Execute isolated RAG pipeline
    rag_result = run_rag_query(
        db=db,
        tenant_id=tenant_id,
        query=chat_req.message,
        top_k=chat_req.top_k or 4
    )

    # Save Assistant Response Message
    citations_json = json.dumps(rag_result["citations"]) if rag_result["citations"] else None
    asst_msg = Message(
        conversation_id=conv.id,
        tenant_id=tenant_id,
        sender="assistant",
        content=rag_result["content"],
        citations=citations_json,
        confidence_score=rag_result["confidence_score"],
        latency_ms=rag_result["latency_ms"],
        tokens_used=rag_result["tokens_used"]
    )
    db.add(asst_msg)

    # Touch conversation updated_at
    conv.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(asst_msg)

    # Log telemetry event
    log_event(
        db=db,
        tenant_id=tenant_id,
        user_id=current_user.id,
        user_email=current_user.email,
        action="chat_query",
        outcome="SUCCESS",
        latency_ms=rag_result["latency_ms"],
        tokens_used=rag_result["tokens_used"],
        model_name=rag_result["model_name"],
        details=f"Q: '{chat_req.message[:50]}...' | Citations: {len(rag_result['citations'])}",
        ip_address=client_ip
    )

    citation_objs = [Citation(**c) for c in rag_result["citations"]]

    return ChatResponse(
        message_id=asst_msg.id,
        conversation_id=conv.id,
        role="assistant",
        content=rag_result["content"],
        citations=citation_objs,
        confidence_score=rag_result["confidence_score"],
        latency_ms=rag_result["latency_ms"],
        tokens_used=rag_result["tokens_used"],
        is_grounded=rag_result["is_grounded"],
        model_name=rag_result["model_name"]
    )


@router.get("/conversations", response_model=List[ConversationResponse])
def list_conversations(
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """List conversations belonging strictly to current tenant and user."""
    convs = (
        db.query(Conversation)
        .filter(
            Conversation.tenant_id == tenant_id,
            Conversation.user_id == current_user.id
        )
        .order_by(Conversation.updated_at.desc())
        .all()
    )

    results = []
    for c in convs:
        m_count = db.query(Message).filter(Message.conversation_id == c.id).count()
        c_resp = ConversationResponse.model_validate(c)
        c_resp.message_count = m_count
        results.append(c_resp)
    return results


@router.get("/conversations/{conv_id}/messages", response_model=List[MessageResponse])
def get_conversation_messages(
    conv_id: int,
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Retrieve message history for a conversation.
    STRICT CHECK: Returns 404 if conversation does not belong to caller's tenant.
    """
    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.tenant_id == tenant_id
    ).first()

    if not conv:
        # Cross-tenant check
        cross_conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
        if cross_conv:
            log_event(
                db=db,
                tenant_id=tenant_id,
                user_id=current_user.id,
                user_email=current_user.email,
                action="cross_tenant_denied",
                outcome="FORBIDDEN",
                details=f"Cross-tenant attempt to view messages of conv_id {conv_id} (belongs to tenant {cross_conv.tenant_id})"
            )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conv.id,
            Message.tenant_id == tenant_id
        )
        .order_by(Message.created_at.asc())
        .all()
    )

    results = []
    for m in messages:
        c_list = None
        if m.citations:
            try:
                raw_c = json.loads(m.citations)
                c_list = [Citation(**c) for c in raw_c]
            except Exception:
                c_list = None
        results.append(
            MessageResponse(
                id=m.id,
                conversation_id=m.conversation_id,
                sender=m.sender,
                content=m.content,
                citations=c_list,
                confidence_score=m.confidence_score,
                latency_ms=m.latency_ms,
                tokens_used=m.tokens_used,
                created_at=m.created_at
            )
        )
    return results


@router.delete("/conversations/{conv_id}")
def delete_conversation(
    conv_id: int,
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Delete a conversation strictly within caller's tenant."""
    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.tenant_id == tenant_id
    ).first()

    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    db.delete(conv)
    db.commit()
    return {"message": "Conversation deleted successfully"}

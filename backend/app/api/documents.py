import os
import json
import time
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.document import Document, DocumentChunk
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.document import DocumentResponse, DocumentDetailResponse
from app.api.deps import get_current_user, get_current_tenant_id
from app.services.document_parser import extract_text_from_pdf, extract_text_from_txt, chunk_pages_text
from app.services.embeddings import get_embedding
from app.services.audit_logger import log_event

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(None),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Upload and process a document (PDF, TXT, MD) strictly within the user's workspace.
    Extracts text, splits into semantic chunks, and generates vector embeddings.
    """
    start_time = time.time()
    client_ip = request.client.host if request.client else None

    # Validate file extension
    filename = file.filename or "uploaded_document.txt"
    file_ext = filename.split(".")[-1].lower() if "." in filename else ""
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '.{file_ext}'. Allowed formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # Check tenant document quota
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    current_docs = db.query(Document).filter(Document.tenant_id == tenant_id).count()
    if tenant and current_docs >= tenant.quota_docs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Workspace document quota reached ({tenant.quota_docs} documents). Please upgrade or delete old files."
        )

    # Prepare storage directory
    tenant_storage_dir = os.path.join(settings.STORAGE_DIR, f"tenant_{tenant_id}")
    os.makedirs(tenant_storage_dir, exist_ok=True)

    # Generate safe filename and path
    clean_name = os.path.basename(filename).replace(" ", "_")
    timestamp_prefix = int(time.time())
    saved_filename = f"{timestamp_prefix}_{clean_name}"
    saved_path = os.path.join(tenant_storage_dir, saved_filename)

    # Read and validate size
    try:
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_size = os.path.getsize(saved_path)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"File save failed: {str(e)}")

    if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
        if os.path.exists(saved_path):
            os.remove(saved_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB"
        )

    doc_title = title.strip() if title and title.strip() else os.path.splitext(clean_name)[0].replace("_", " ")

    # Create initial document record with PENDING status
    new_doc = Document(
        tenant_id=tenant_id,
        filename=filename,
        file_path=saved_path,
        file_type=file_ext,
        file_size=file_size,
        title=doc_title,
        status="PROCESSING",
        chunk_count=0
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # Parse and chunk document
    try:
        if file_ext == "pdf":
            pages_data = extract_text_from_pdf(saved_path)
        else:
            pages_data = extract_text_from_txt(saved_path)

        if not pages_data:
            raise ValueError("No extractable text found in file.")

        raw_chunks = chunk_pages_text(pages_data)
        if not raw_chunks:
            raise ValueError("Document yielded no valid text chunks.")

        # Create chunk records with vector embeddings
        for chunk_item in raw_chunks:
            chunk_content = chunk_item["content"]
            embedding = get_embedding(chunk_content)

            chunk_record = DocumentChunk(
                document_id=new_doc.id,
                tenant_id=tenant_id,
                chunk_index=chunk_item["chunk_index"],
                content=chunk_content,
                page_number=chunk_item["page_number"],
                token_count=chunk_item["token_count"],
                embedding=json.dumps(embedding)
            )
            db.add(chunk_record)

        new_doc.status = "READY"
        new_doc.chunk_count = len(raw_chunks)
        new_doc.error_message = None
        db.commit()
        db.refresh(new_doc)

        log_event(
            db=db,
            tenant_id=tenant_id,
            user_id=current_user.id,
            user_email=current_user.email,
            action="doc_upload",
            outcome="SUCCESS",
            latency_ms=int((time.time() - start_time) * 1000),
            details=f"Uploaded '{filename}' ({len(raw_chunks)} chunks)",
            ip_address=client_ip
        )

    except Exception as e:
        new_doc.status = "FAILED"
        new_doc.error_message = str(e)
        db.commit()
        db.refresh(new_doc)

        log_event(
            db=db,
            tenant_id=tenant_id,
            user_id=current_user.id,
            user_email=current_user.email,
            action="doc_upload",
            outcome="ERROR",
            latency_ms=int((time.time() - start_time) * 1000),
            details=f"Failed processing '{filename}': {str(e)}",
            ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Document parsing error: {str(e)}"
        )

    return new_doc


@router.get("", response_model=List[DocumentResponse])
def list_documents(
    tenant_id: int = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """
    List all documents strictly belonging to the authenticated tenant.
    Never returns documents from other companies.
    """
    return db.query(Document).filter(Document.tenant_id == tenant_id).order_by(Document.created_at.desc()).all()


@router.get("/{doc_id}", response_model=DocumentDetailResponse)
def get_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Retrieve document details and chunks.
    STRICT CHECK: Returns 404 if the document does not exist in the caller's tenant.
    Never confirms the existence of documents in other tenants.
    """
    doc = db.query(Document).filter(
        Document.id == doc_id,
        Document.tenant_id == tenant_id
    ).first()

    if not doc:
        # Check if cross-tenant unauthorized access attempt occurred
        cross_doc = db.query(Document).filter(Document.id == doc_id).first()
        if cross_doc:
            # Cross-tenant attempt detected! Log security alert
            log_event(
                db=db,
                tenant_id=tenant_id,
                user_id=current_user.id,
                user_email=current_user.email,
                action="cross_tenant_denied",
                outcome="FORBIDDEN",
                details=f"User attempted cross-tenant document read on doc_id {doc_id} belonging to tenant {cross_doc.tenant_id}"
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    chunks = db.query(DocumentChunk).filter(
        DocumentChunk.document_id == doc.id,
        DocumentChunk.tenant_id == tenant_id
    ).order_by(DocumentChunk.chunk_index).all()

    resp = DocumentDetailResponse.model_validate(doc)
    resp.chunks = chunks
    return resp


@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Delete a document and all associated chunks.
    STRICT CHECK: Can only delete documents belonging to the user's tenant.
    """
    doc = db.query(Document).filter(
        Document.id == doc_id,
        Document.tenant_id == tenant_id
    ).first()

    if not doc:
        # Check if this was a malicious cross-tenant delete attempt
        cross_doc = db.query(Document).filter(Document.id == doc_id).first()
        if cross_doc:
            log_event(
                db=db,
                tenant_id=tenant_id,
                user_id=current_user.id,
                user_email=current_user.email,
                action="cross_tenant_denied",
                outcome="FORBIDDEN",
                details=f"User attempted cross-tenant document delete on doc_id {doc_id} belonging to tenant {cross_doc.tenant_id}"
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Remove physical file if it exists
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    doc_filename = doc.filename
    db.delete(doc)
    db.commit()

    log_event(
        db=db,
        tenant_id=tenant_id,
        user_id=current_user.id,
        user_email=current_user.email,
        action="doc_delete",
        outcome="SUCCESS",
        details=f"Deleted document '{doc_filename}' (id: {doc_id})"
    )

    return {"message": f"Document '{doc_filename}' successfully deleted"}

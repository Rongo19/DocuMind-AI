import os
from fastapi import APIRouter, HTTPException
from app.core.store import get_all_documents, get_document, load_store, save_store
from app.core.security import validate_doc_id
from app.services.rag import delete_document_chunks

router = APIRouter()


@router.get("/documents")
def list_documents():
    return {"documents": get_all_documents()}


@router.get("/documents/{doc_id}")
def get_doc(doc_id: str):
    validate_doc_id(doc_id)
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc


@router.get("/documents/{doc_id}/status")
def get_status(doc_id: str):
    validate_doc_id(doc_id)
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return {"doc_id": doc_id, "status": doc["status"]}


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    validate_doc_id(doc_id)
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")

    file_path = doc.get("file_path")
    if file_path and os.path.exists(file_path):
        os.remove(file_path)

    from app.core.config import PAGES_DIR
    pages_dir = os.path.join(PAGES_DIR, doc_id)
    if os.path.exists(pages_dir):
        for f in os.listdir(pages_dir):
            os.remove(os.path.join(pages_dir, f))
        os.rmdir(pages_dir)

    delete_document_chunks(doc_id)

    store = load_store()
    store.pop(doc_id, None)
    save_store(store)

    return {"deleted": True, "doc_id": doc_id}


@router.get("/debug/all")
def debug_all():
    return load_store()
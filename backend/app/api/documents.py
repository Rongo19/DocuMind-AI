from fastapi import APIRouter, HTTPException
from app.core.store import get_all_documents, get_document

router = APIRouter()


@router.get("/documents")
def list_documents():
    return {"documents": get_all_documents()}


@router.get("/documents/{doc_id}")
def get_doc(doc_id: str):
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc


@router.get("/documents/{doc_id}/status")
def get_status(doc_id: str):
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return {"doc_id": doc_id, "status": doc["status"]}
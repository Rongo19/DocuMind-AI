from fastapi import APIRouter, Request
from pydantic import BaseModel
from app.services.rag import query_documents
from app.core.security import sanitize_query
from app.core.limiter import limiter

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    history: list[dict] = []


@router.post("/chat")
@limiter.limit("30/minute")
def chat(request: Request, body: ChatRequest):
    clean_query = sanitize_query(body.query)
    result = query_documents(clean_query)
    return {
        "answer": result["answer"],
        "citations": result["citations"],
    }
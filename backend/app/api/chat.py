from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag import query_documents

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    history: list[dict] = []


@router.post("/chat")
def chat(request: ChatRequest):
    result = query_documents(request.query)
    return {
        "answer": result["answer"],
        "citations": result["citations"],
    }
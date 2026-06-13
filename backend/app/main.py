import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import upload, chat, documents
from app.core.config import PAGES_DIR

app = FastAPI(title="Document Intelligence API")

# CORS — allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve page images statically
os.makedirs(PAGES_DIR, exist_ok=True)
app.mount("/pages", StaticFiles(directory=PAGES_DIR), name="pages")

# Routes
app.include_router(upload.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(documents.router, prefix="/api")

@app.get("/")
def root():
    return {"status": "ok", "message": "Document Intelligence API is running"} 
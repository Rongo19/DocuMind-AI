import os
import uuid
import threading
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from typing import List
from app.core.config import UPLOAD_DIR, ALLOWED_EXTENSIONS
from app.core.store import add_document, update_status
from app.core.security import full_file_validation, sanitize_filename
from app.core.limiter import limiter
from app.services.parser import parse_document
from app.services.classifier import classify_document
from app.services.rag import index_document

router = APIRouter()

os.makedirs(UPLOAD_DIR, exist_ok=True)


def process_document_sync(doc_id: str, file_path: str, filename: str):
    try:
        print(f"[{doc_id}] Starting parse: {filename}")
        update_status(doc_id, "parsing")
        pages = parse_document(file_path, doc_id, filename)
        print(f"[{doc_id}] Parsed {len(pages)} pages")

        update_status(doc_id, "classifying")
        print(f"[{doc_id}] Classifying...")
        classification = classify_document(pages)
        print(f"[{doc_id}] Classified: {classification.get('document_type')}")

        update_status(doc_id, "indexing")
        print(f"[{doc_id}] Indexing...")
        chunk_count = index_document(doc_id, filename, pages)
        print(f"[{doc_id}] Indexed {chunk_count} chunks")

        update_status(doc_id, "ready", {
            "classification": classification,
            "page_count": len(pages),
            "chunk_count": chunk_count,
            "pages": [
                {
                    "page_num": p["page_num"],
                    "image_url": p["image_url"],
                    "has_tables": p["has_tables"],
                }
                for p in pages
            ]
        })
        print(f"[{doc_id}] Done!")

    except Exception as e:
        print(f"[{doc_id}] ERROR: {e}")
        import traceback
        traceback.print_exc()
        update_status(doc_id, "error", {"error": str(e)})


@router.post("/upload")
@limiter.limit("10/minute")
async def upload_files(request: Request, files: List[UploadFile] = File(...)):
    if len(files) > 10:
        raise HTTPException(400, "Maximum 10 files per upload")

    results = []

    for file in files:
        content = await file.read()

        # Security validation
        full_file_validation(file, content)

        # Sanitize filename for display only
        safe_display_name = sanitize_filename(file.filename)

        # Generate UUID-based storage name
        doc_id = str(uuid.uuid4())
        ext = file.filename.rsplit(".", 1)[-1].lower()
        storage_filename = f"{doc_id}.{ext}"
        file_path = os.path.join(UPLOAD_DIR, storage_filename)

        with open(file_path, "wb") as f:
            f.write(content)

        add_document(doc_id, {
            "doc_id": doc_id,
            "filename": safe_display_name,
            "file_path": file_path,
            "status": "queued",
            "classification": None,
            "page_count": 0,
            "chunk_count": 0,
            "pages": [],
        })

        thread = threading.Thread(
            target=process_document_sync,
            args=(doc_id, file_path, safe_display_name),
            daemon=True
        )
        thread.start()

        results.append({
            "doc_id": doc_id,
            "filename": safe_display_name,
            "status": "queued"
        })

    return {"uploaded": results}
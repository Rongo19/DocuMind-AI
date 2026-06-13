import os
import uuid
import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.core.config import UPLOAD_DIR, MAX_FILE_SIZE_MB, ALLOWED_EXTENSIONS
from app.core.store import add_document, update_status
from app.services.parser import parse_document
from app.services.classifier import classify_document
from app.services.rag import index_document

router = APIRouter()

os.makedirs(UPLOAD_DIR, exist_ok=True)


def validate_file(file: UploadFile):
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"File type .{ext} not allowed")


async def process_document(doc_id: str, file_path: str, filename: str):
    try:
        # Step 1: Parse
        update_status(doc_id, "parsing")
        pages = parse_document(file_path, doc_id, filename)

        # Step 2: Classify
        update_status(doc_id, "classifying")
        classification = classify_document(pages)

        # Step 3: Index
        update_status(doc_id, "indexing")
        chunk_count = index_document(doc_id, filename, pages)

        # Done
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

    except Exception as e:
        update_status(doc_id, "error", {"error": str(e)})


@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    results = []

    for file in files:
        validate_file(file)

        # Check file size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(400, f"{file.filename} exceeds {MAX_FILE_SIZE_MB}MB limit")

        # Save file
        doc_id = str(uuid.uuid4())
        ext = file.filename.rsplit(".", 1)[-1].lower()
        safe_filename = f"{doc_id}.{ext}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)

        with open(file_path, "wb") as f:
            f.write(content)

        # Register in store
        add_document(doc_id, {
            "doc_id": doc_id,
            "filename": file.filename,
            "file_path": file_path,
            "status": "queued",
            "classification": None,
            "page_count": 0,
            "chunk_count": 0,
            "pages": [],
        })

        # Process in background
        asyncio.create_task(
            asyncio.to_thread(
                process_document_sync, doc_id, file_path, file.filename
            )
        )

        results.append({"doc_id": doc_id, "filename": file.filename, "status": "queued"})

    return {"uploaded": results}


def process_document_sync(doc_id: str, file_path: str, filename: str):
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        update_status(doc_id, "parsing")
        pages = parse_document(file_path, doc_id, filename)

        update_status(doc_id, "classifying")
        classification = classify_document(pages)

        update_status(doc_id, "indexing")
        chunk_count = index_document(doc_id, filename, pages)

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
    except Exception as e:
        update_status(doc_id, "error", {"error": str(e)})
    finally:
        loop.close()
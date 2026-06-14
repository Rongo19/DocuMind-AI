import os
import uuid
from app.core.store import add_document, update_status
from app.services.parser import parse_document
from app.services.classifier import classify_document
from app.services.rag import index_document

SAMPLE_DIR = "sample_docs"


def seed():
    if not os.path.exists(SAMPLE_DIR):
        print("No sample_docs folder found.")
        return

    files = [f for f in os.listdir(SAMPLE_DIR) if f.lower().endswith((".pdf", ".png", ".jpg", ".jpeg", ".tiff"))]

    if not files:
        print("No sample documents found.")
        return

    for filename in files:
        file_path = os.path.join(SAMPLE_DIR, filename)
        doc_id = str(uuid.uuid4())

        print(f"\nProcessing: {filename}")

        add_document(doc_id, {
            "doc_id": doc_id,
            "filename": filename,
            "file_path": file_path,
            "status": "queued",
            "classification": None,
            "page_count": 0,
            "chunk_count": 0,
            "pages": [],
        })

        try:
            update_status(doc_id, "parsing")
            pages = parse_document(file_path, doc_id, filename)
            print(f"  Parsed {len(pages)} pages")

            update_status(doc_id, "classifying")
            classification = classify_document(pages)
            print(f"  Classified as: {classification.get('document_type')}")

            update_status(doc_id, "indexing")
            chunk_count = index_document(doc_id, filename, pages)
            print(f"  Indexed {chunk_count} chunks")

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
            print(f"  Done: {filename}")

        except Exception as e:
            print(f"  ERROR processing {filename}: {e}")
            update_status(doc_id, "error", {"error": str(e)})


if __name__ == "__main__":
    seed()
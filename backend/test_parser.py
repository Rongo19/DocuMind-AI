import sys
import json
from app.services.parser import parse_document

# Usage: python test_parser.py <path_to_any_pdf>
if __name__ == "__main__":
    file_path = sys.argv[1]
    filename = file_path.split("\\")[-1]
    doc_id = "test_doc_001"

    print(f"Parsing: {filename}")
    pages = parse_document(file_path, doc_id, filename)

    for page in pages:
        print(f"\n--- Page {page['page_num']} ---")
        print(f"Text preview: {page['text'][:300]}")
        print(f"Has tables: {page['has_tables']}")
        print(f"Image saved at: {page['image_path']}")
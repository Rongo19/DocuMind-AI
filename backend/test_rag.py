import json
from app.services.parser import parse_document
from app.services.rag import index_document, query_documents

file_path = r"D:\Downloads\BFAI_AI_Engineer_Assessment.pdf"
filename = "BFAI_AI_Engineer_Assessment.pdf"
doc_id = "test_doc_001"

print("Parsing document...")
pages = parse_document(file_path, doc_id, filename)
print(f"Parsed {len(pages)} pages")

print("\nIndexing document...")
count = index_document(doc_id, filename, pages)
print(f"Indexed {count} chunks")

questions = [
    "What is this document about?",
    "What are the main features to build?",
    "What security measures are required?",
]

for q in questions:
    print(f"\nQuestion: {q}")
    result = query_documents(q)
    print(f"Answer: {result['answer']}")
    print("Citations:")
    for c in result["citations"]:
        print(f"  - {c['filename']}, Page {c['page_num']}")
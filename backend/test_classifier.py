import json
from app.services.parser import parse_document
from app.services.classifier import classify_document

file_path = r"D:\Downloads\BFAI_AI_Engineer_Assessment.pdf"
filename = "BFAI_AI_Engineer_Assessment.pdf"
doc_id = "test_doc_001"

print("Parsing document...")
pages = parse_document(file_path, doc_id, filename)
print(f"Parsed {len(pages)} pages")

print("\nClassifying document...")
result = classify_document(pages)

print("\nClassification Result:")
print(json.dumps(result, indent=2))
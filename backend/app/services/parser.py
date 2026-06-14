import os
import pytesseract
import pdfplumber
from pdf2image import convert_from_path
from PIL import Image
from app.core.config import TESSERACT_PATH, POPPLER_PATH, PAGES_DIR, UPLOAD_DIR
 

PAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "storage", "pages")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "storage", "uploads")

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# ── helpers ────────────────────────────────────────────────────────────────
def get_doc_dir(doc_id: str, base_dir: str) -> str:
    path = os.path.abspath(os.path.join(base_dir, doc_id))
    os.makedirs(path, exist_ok=True)
    return path


def extract_text_from_image(image: Image.Image) -> str:
    return pytesseract.image_to_string(image)


# ── PDF parser ─────────────────────────────────────────────────────────────
def parse_pdf(file_path: str, doc_id: str) -> list[dict]:
    pages_dir = get_doc_dir(doc_id, PAGES_DIR)

    with pdfplumber.open(file_path) as pdf:
        num_pages = len(pdf.pages)
        pages = []

        for i, plumber_page in enumerate(pdf.pages):
            page_num = i + 1

            text = plumber_page.extract_text() or ""

            tables = plumber_page.extract_tables()
            table_text = ""
            if tables:
                for table in tables:
                    for row in table:
                        cleaned = [cell or "" for cell in row]
                        table_text += " | ".join(cleaned) + "\n"

            # Render only this page to image (low memory)
            if POPPLER_PATH:
                page_images = convert_from_path(
                    file_path, dpi=100, poppler_path=POPPLER_PATH,
                    first_page=page_num, last_page=page_num
                )
            else:
                page_images = convert_from_path(
                    file_path, dpi=100,
                    first_page=page_num, last_page=page_num
                )

            page_image = page_images[0]

            if not text.strip():
                text = extract_text_from_image(page_image)

            image_filename = f"page_{page_num}.jpg"
            image_path = os.path.join(pages_dir, image_filename)
            page_image.save(image_path, "JPEG")
            page_image.close()
            del page_images

            pages.append({
                "page_num": page_num,
                "text": (text.strip() + "\n" + table_text.strip()).strip(),
                "image_path": image_path,
                "image_url": f"/pages/{doc_id}/page_{page_num}.jpg",
                "has_tables": bool(tables),
            })

    return pages


# ── image parser ───────────────────────────────────────────────────────────
def parse_image_file(file_path: str, doc_id: str) -> list[dict]:
    pages_dir = get_doc_dir(doc_id, PAGES_DIR)

    image = Image.open(file_path)
    text = extract_text_from_image(image)

    image_path = os.path.join(pages_dir, "page_1.jpg")
    image.convert("RGB").save(image_path, "JPEG")

    return [{
        "page_num": 1,
        "text": text.strip(),
        "image_path": image_path,
        "image_url": f"/pages/{doc_id}/page_1.jpg",
        "has_tables": False,
    }]


# ── entry point ────────────────────────────────────────────────────────────
def parse_document(file_path: str, doc_id: str, filename: str) -> list[dict]:
    ext = filename.rsplit(".", 1)[-1].lower()

    if ext == "pdf":
        return parse_pdf(file_path, doc_id)
    elif ext in ["png", "jpg", "jpeg", "tiff"]:
        return parse_image_file(file_path, doc_id)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
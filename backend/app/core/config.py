import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "storage/uploads")
PAGES_DIR = os.getenv("PAGES_DIR", "storage/pages")
CHROMA_DIR = os.getenv("CHROMA_DIR", "storage/vectors")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 20))
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "pdf,png,jpg,jpeg,tiff").split(",")

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\poppler\Library\bin"
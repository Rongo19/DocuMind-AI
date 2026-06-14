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

# On Linux (Render), tesseract and poppler are installed via apt and are on PATH
# On Windows (local dev), use full paths
TESSERACT_PATH = os.getenv("TESSERACT_PATH", "tesseract")
POPPLER_PATH = os.getenv("POPPLER_PATH", None)  # None = use system PATH on Linux
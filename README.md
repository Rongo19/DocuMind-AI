# DocuMind-AI - Agentic RAG System

A full-stack web app that ingests messy real-world documents, classifies them, and powers a chatbot with grounded citations showing the exact source page.

## Features

- **Document Parser** — handles scanned PDFs, image-heavy files, tables, and plain text using pdfplumber, pdf2image, and pytesseract OCR
- **Document Classifier** — classifies each document across type, topic, sensitivity level, and content characteristics using Groq LLaMA
- **Agentic RAG** — retrieves relevant chunks and generates answers with inline citations and page thumbnails
- **Chatbot Page** — multi-turn conversation with source thumbnails and full-page viewer
- **Bulk Upload Page** — upload multiple documents, track processing status, view and delete documents
- **Security** — file validation, rate limiting, path traversal protection, security headers, input sanitization

## Architecture

```
document-intelligence/
├── backend/                  # FastAPI Python backend
│   ├── app/
│   │   ├── api/              # Route handlers
│   │   │   ├── upload.py     # File upload + processing
│   │   │   ├── chat.py       # RAG chat endpoint
│   │   │   └── documents.py  # Document management
│   │   ├── core/             # Config, security, store
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── limiter.py
│   │   │   └── store.py
│   │   ├── services/         # Core logic
│   │   │   ├── parser.py     # PDF + OCR parsing
│   │   │   ├── classifier.py # LLM classification
│   │   │   └── rag.py        # Embeddings + retrieval
│   │   └── main.py
│   ├── sample_docs/          # 5 sample documents
│   └── storage/              # Runtime storage (gitignored)
└── frontend/                 # Next.js TypeScript frontend
    └── app/
        ├── page.tsx          # Chatbot page
        └── upload/page.tsx   # Bulk upload page
```

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Tesseract OCR installed
- Poppler installed

### 1. Clone the repo

```bash
git clone https://github.com/Rongo19/document-intelligence.git
cd document-intelligence
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:

```
GROQ_API_KEY=your_groq_api_key_here
UPLOAD_DIR=storage/uploads
PAGES_DIR=storage/pages
CHROMA_DIR=storage/vectors
MAX_FILE_SIZE_MB=20
ALLOWED_EXTENSIONS=pdf,png,jpg,jpeg,tiff
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
POPPLER_PATH=C:\poppler\Library\bin
```

Generate sample documents:

```bash
python create_samples.py
```

Start the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Open the app

- Chatbot: http://localhost:3000
- Upload: http://localhost:3000/upload
- API docs: http://localhost:8000/docs

### 5. Load sample documents

Upload the PDFs from `backend/sample_docs/` using the Upload page — they will be parsed, classified, and indexed automatically.

## Security Decisions

### What I implemented

**Upload layer**
- File extension whitelist (pdf, png, jpg, jpeg, tiff only)
- File size limit (20MB max)
- Path traversal detection — blocks filenames containing `..`, `/`, `\`
- Filenames sanitized with regex before display
- Files stored with UUID names — original filename never touches disk
- Max 10 files per request

**Storage layer**
- Uploaded files stored in isolated `storage/uploads/` directory
- Page images stored in per-document subdirectories under `storage/pages/`
- No user-controlled paths used anywhere in file I/O
- `.env` and `storage/` excluded from git via `.gitignore`

**Processing layer**
- Documents processed in isolated threads
- Errors caught and stored — never exposed as raw exceptions to client
- Input text sanitized with bleach before sending to LLM

**API layer**
- Rate limiting: 10 uploads/minute, 30 chat requests/minute per IP
- CORS restricted to frontend origin only
- Security headers on every response (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
- Document IDs validated as UUIDs before any database or file operation
- Chat queries sanitized and length-limited before retrieval

### What I considered but skipped (time constraints)
- Authentication and per-user document isolation
- Virus/malware scanning of uploaded files (e.g. ClamAV)
- MIME type verification using file magic bytes (not just extension)
- Encrypted storage of uploaded files at rest
- Audit logging of all document access and deletion events

### What I would add given more time
- JWT-based auth so each user only sees their own documents
- ClamAV integration for malware scanning before processing
- File magic byte verification alongside extension checks
- AES-256 encryption for files at rest
- Full audit log with timestamps for compliance
- Content Security Policy (CSP) headers on frontend
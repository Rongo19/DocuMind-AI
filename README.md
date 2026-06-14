# DocuMind-AI

A web app that ingests messy documents (scanned PDFs, handwritten pages, tables, images), extracts content with OCR, classifies each document using an LLM, and powers a chatbot that answers questions with grounded citations showing the exact source page.

DocuMind-AI was built for the AI Engineer Intern Assessment — Build Fast with AI.

## Live Demo

- Frontend: https://docu-mind-ai-lemon.vercel.app
- Backend API: https://documind-ai-2zcz.onrender.com

> Note: Backend is on Render's free tier, which sleeps after inactivity — the first request may take 30-60 seconds to wake up.

## Features

- **Document Parser** — extracts text from PDFs and images using pdfplumber, pdf2image, and pytesseract OCR. Each page stores extracted text + a rendered page image.
- **Document Classifier** — classifies each document (type, topic, summary, sensitivity, tags, etc.) as structured JSON using Groq's LLaMA 3.3 70B.
- **Agentic RAG** — chunks and embeds text (sentence-transformers + ChromaDB), retrieves relevant chunks, and answers with inline citations (filename + page number). Says "I could not find this information" instead of hallucinating.
- **Chatbot Page** — multi-turn chat with citations and clickable page thumbnails.
- **Bulk Upload Page** — drag-and-drop multiple files, shows per-file status (parsing → classifying → indexing → ready), and lets you view/delete documents.
- **Voice Input (Bonus)** — real-time speech-to-text using the browser's Web Speech API, with live transcript.

## Tech Stack

- Frontend: Next.js (TypeScript) + Tailwind CSS
- Backend: FastAPI (Python)
- OCR/Parsing: pdfplumber, pdf2image, pytesseract
- Classification + RAG answers: Groq API (free tier)
- Embeddings: sentence-transformers (local, free)
- Vector store: ChromaDB
- Deployment: Render (backend, Docker) + Vercel (frontend)

## Project Structure

```
DOC_AI/
├── backend/
│   ├── app/
│   │   ├── api/          # upload, chat, documents routes
│   │   ├── core/         # config, security, rate limiting, storage
│   │   └── services/     # parser, classifier, rag
│   ├── sample_docs/       # 5 sample documents
│   ├── create_samples.py  # generates sample PDFs
│   ├── seed_samples.py    # indexes sample_docs into the knowledge base
│   └── Dockerfile
└── frontend/
    ├── app/               # chatbot page + upload page
    ├── components/        # navbar, processing banner
    └── lib/                # api client, voice input hook
```

## Running Locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- Tesseract OCR and Poppler installed and on PATH
- A free Groq API key from https://console.groq.com

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

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

Generate and load sample documents, then start the server:

```bash
python create_samples.py
python seed_samples.py
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

```bash
npm run dev
```

Open:
- Chatbot: http://localhost:3000
- Bulk Upload: http://localhost:3000/upload

## Usage

1. Go to **Upload**, drag in PDFs/images (sample docs are pre-loaded if seeded).
2. Watch status move through Parsing → Classifying → Indexing → Ready.
3. Go to **Chatbot** and ask questions — answers show inline citations with page thumbnails. Click a thumbnail for the full page.
4. Click the 🎤 icon for voice input (Chrome/Edge recommended).
5. Delete unneeded documents from the Upload page.

## Security Decisions

**Upload layer**
- Whitelisted file extensions (pdf, png, jpg, jpeg, tiff) and 20MB size limit
- Path traversal protection and filename sanitization
- Files stored with UUID names — original filenames never used as paths
- Max 10 files per upload request

**Storage layer**
- Uploaded files and page images isolated in per-document folders
- `.env` and `storage/` excluded from git

**Processing layer**
- Each document processed in an isolated background thread
- Errors caught and stored — raw stack traces never returned to the client
- Pages processed one at a time to limit memory usage

**API layer**
- Rate limiting (10 uploads/min, 30 chat requests/min per IP)
- CORS restricted to the deployed frontend origin
- Security headers on all responses (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
- Document IDs validated as UUIDs before any file/database operation
- Chat input sanitized and length-limited
- RAG strictly grounded in retrieved context — explicitly told to say "not found" rather than guess

**What I'd add given more time**
- Authentication and per-user document isolation
- Malware scanning of uploads (e.g. ClamAV)
- File content verification (magic bytes, not just extension)
- Encryption at rest
- Audit logging
- Persistent database/storage instead of local disk for production durability

## Known Limitations

- Free-tier hosting (Render) has limited memory and ephemeral storage — large documents may take longer to process, and data can be reset on redeploy. Local execution does not have this issue.
- Voice input works best in Chrome/Edge and requires an internet connection.

## Sample Documents

Included in `backend/sample_docs/`: a financial report, employee onboarding manual, AI research paper, an invoice, and a project requirements document — covering different document types for the classifier and RAG to demonstrate on.

## Author

Rohan Gorde — B.E. AI & Data Science Engineering, PVG's College of Engineering and Technology, Pune
GitHub: [Rongo19](https://github.com/Rongo19)
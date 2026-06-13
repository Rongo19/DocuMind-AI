import os
import re
import bleach
from fastapi import HTTPException, UploadFile

# Allowed MIME types mapped to extensions
ALLOWED_MIME_TYPES = {
    "application/pdf": "pdf",
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/tiff": "tiff",
}

MAX_FILENAME_LENGTH = 255
MAX_FILE_SIZE_MB = 20


def sanitize_filename(filename: str) -> str:
    # Remove any path separators and dangerous characters
    filename = os.path.basename(filename)
    filename = re.sub(r"[^\w\s\-.]", "", filename)
    filename = filename.strip()

    if len(filename) > MAX_FILENAME_LENGTH:
        name, ext = os.path.splitext(filename)
        filename = name[: MAX_FILENAME_LENGTH - len(ext)] + ext

    if not filename:
        filename = "unnamed_file"

    return filename


def validate_file_size(content: bytes, filename: str):
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            400,
            f"{filename} is {size_mb:.1f}MB — max allowed is {MAX_FILE_SIZE_MB}MB"
        )


def validate_file_extension(filename: str):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    allowed = list(ALLOWED_MIME_TYPES.values())
    if ext not in allowed:
        raise HTTPException(
            400,
            f"File type .{ext} is not allowed. Allowed: {', '.join(allowed)}"
        )


def validate_no_path_traversal(filename: str):
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(400, "Invalid filename — path traversal detected")


def sanitize_query(query: str) -> str:
    # Strip HTML tags and limit length
    clean = bleach.clean(query, tags=[], strip=True)
    clean = clean.strip()
    if len(clean) > 1000:
        clean = clean[:1000]
    if not clean:
        raise HTTPException(400, "Query cannot be empty")
    return clean


def validate_doc_id(doc_id: str):
    # Doc IDs must be UUIDs — reject anything else
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
    if not uuid_pattern.match(doc_id):
        raise HTTPException(400, "Invalid document ID format")


def full_file_validation(file: UploadFile, content: bytes):
    validate_no_path_traversal(file.filename)
    validate_file_extension(file.filename)
    validate_file_size(content, file.filename)
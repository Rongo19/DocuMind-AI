import json
import os

# Simple JSON file to track document metadata
STORE_PATH = "storage/documents.json"


def load_store() -> dict:
    if not os.path.exists(STORE_PATH):
        return {}
    try:
        with open(STORE_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return {}


def save_store(data: dict):
    os.makedirs(os.path.dirname(STORE_PATH), exist_ok=True)
    tmp_path = STORE_PATH + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, STORE_PATH)


def add_document(doc_id: str, metadata: dict):
    store = load_store()
    store[doc_id] = metadata
    save_store(store)


def get_document(doc_id: str) -> dict | None:
    store = load_store()
    return store.get(doc_id)


def get_all_documents() -> list[dict]:
    store = load_store()
    return list(store.values())


def update_status(doc_id: str, status: str, extra: dict = {}):
    store = load_store()
    if doc_id in store:
        store[doc_id]["status"] = status
        store[doc_id].update(extra)
        save_store(store)
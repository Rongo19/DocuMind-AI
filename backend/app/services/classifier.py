import json
from groq import Groq
from app.core.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

CLASSIFICATION_PROMPT = """
You are a document classification expert. Analyze the text below and return ONLY a valid JSON object with no extra text, no markdown, no backticks.

Classify across these dimensions:

{{
  "document_type": "one of: invoice, report, form, letter, contract, manual, academic_paper, news_article, handwritten_note, presentation, other",
  "topic": "main subject in 3-5 words",
  "summary": "2-3 sentence summary of the document",
  "language": "detected language",
  "content_characteristics": {{
    "has_tables": true or false,
    "has_images": true or false,
    "has_handwriting": true or false,
    "is_scanned": true or false,
    "estimated_pages": number
  }},
  "sensitivity_level": "one of: public, internal, confidential, highly_confidential",
  "sensitivity_reason": "one sentence explaining the sensitivity level",
  "key_entities": ["list", "of", "important", "names", "orgs", "dates"],
  "tags": ["relevant", "topic", "tags"]
}}

Document text:
{text}
"""


def classify_document(pages: list[dict]) -> dict:
    full_text = "\n\n".join(
        f"[Page {p['page_num']}]\n{p['text']}" for p in pages
    )
    full_text = full_text[:3000]

    prompt = CLASSIFICATION_PROMPT.replace("{text}", full_text)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a document classification expert. Always respond with valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)
import json
import os

from dotenv import load_dotenv
from groq import Groq

from modules.schemas import MedicalInstructionDocument

load_dotenv()


def extract_instructions(pages: list[dict], document_name: str):
    if not pages:
        raise ValueError("No PDF text was provided.")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing.")

    source_text = "\n\n".join(
        f"PAGE {page['page']}:\n{page['text']}"
        for page in pages
    )

    prompt = """
You are a medical document information extraction assistant.

Extract facts ONLY from the supplied document.

Rules:
- Never invent, calculate or modify medication dosages.
- Preserve original medication names and instructions.
- Use null for missing or unclear information.
- Extract only explicitly stated dates.
- Flag ambiguous or conflicting instructions for human review.
- Include source page numbers.
- Never diagnose or recommend treatment.
- Return valid JSON only.

Return these fields:
document_name
medications: medication_name, dosage, route, frequency, timing,
duration, start_date, end_date, source_page, needs_review, review_reason
general_instructions: instruction, category, source_page, needs_review
follow_ups: instruction, date, source_page, needs_review
warnings
extraction_notes

Use empty lists when no information exists.
"""

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": (
                    f"Document name: {document_name}\n\n"
                    f"Document text:\n{source_text}"
                )
            }
        ],
        response_format={"type": "json_object"},
        temperature=0
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("The AI returned an empty response.")

    result = json.loads(content)
    result.setdefault("document_name", document_name)

    return MedicalInstructionDocument.model_validate(result)

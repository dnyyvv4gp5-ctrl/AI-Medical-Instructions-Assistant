import json

import pytest
import pymupdf

from modules.schemas import MedicalInstructionDocument
from modules.pdf_processor import extract_pdf_pages
from modules import reminder_manager
from modules import instruction_extractor


def make_pdf(text="Example medical instruction"):
    document = pymupdf.open()
    page = document.new_page()
    if text:
        page.insert_text((72, 72), text)
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


def test_schema_normalizes_string_warnings_and_notes():
    result = MedicalInstructionDocument.model_validate({
        "document_name": "sample.pdf",
        "warnings": "Check with a clinician",
        "extraction_notes": None,
    })
    assert result.warnings == ["Check with a clinician"]
    assert result.extraction_notes == []


def test_schema_accepts_missing_medication_details():
    result = MedicalInstructionDocument.model_validate({
        "document_name": "sample.pdf",
        "medications": [{"medication_name": "Exampleton"}],
    })
    assert result.medications[0].dosage is None
    assert result.medications[0].needs_review == True


def test_pdf_extraction_returns_page_number_and_text():
    pages = extract_pdf_pages(make_pdf("Take with breakfast"))
    assert pages == [{"page": 1, "text": "Take with breakfast"}]


def test_pdf_extraction_rejects_empty_upload():
    with pytest.raises(ValueError, match="empty"):
        extract_pdf_pages(b"")


def test_pdf_extraction_rejects_invalid_pdf():
    with pytest.raises(ValueError, match="not a valid PDF"):
        extract_pdf_pages(b"not a pdf")


def test_pdf_extraction_rejects_pdf_without_readable_text():
    with pytest.raises(ValueError, match="No readable text"):
        extract_pdf_pages(make_pdf(""))


def test_reminder_requires_explicit_approval():
    with pytest.raises(PermissionError, match="approval"):
        reminder_manager.create_reminder(
            "Take medication",
            "2026-11-20T09:00",
            approved=False,
        )


def test_reminder_create_update_list_and_delete(tmp_path, monkeypatch):
    monkeypatch.setattr(reminder_manager, "DB_PATH", tmp_path / "test_reminders.db")
    reminder_manager.initialize_database()

    reminder_id = reminder_manager.create_reminder(
        "Take medication",
        "2026-11-20T09:00",
        medication_name="Exampleton",
        approved=True,
    )

    reminders = reminder_manager.get_reminders("upcoming")
    assert len(reminders) == 1
    assert reminders[0]["id"] == reminder_id
    assert reminders[0]["medication_name"] == "Exampleton"

    reminder_manager.update_reminder_status(reminder_id, "completed")
    assert reminder_manager.get_reminders("completed")[0]["id"] == reminder_id

    reminder_manager.delete_reminder(reminder_id)
    assert reminder_manager.get_reminders() == []


def test_reminder_rejects_invalid_status(tmp_path, monkeypatch):
    monkeypatch.setattr(reminder_manager, "DB_PATH", tmp_path / "test_reminders.db")
    reminder_manager.initialize_database()

    with pytest.raises(ValueError, match="Invalid reminder status"):
        reminder_manager.update_reminder_status(1, "cancelled")


def test_ai_extraction_rejects_empty_pages():
    with pytest.raises(ValueError, match="No PDF text"):
        instruction_extractor.extract_instructions([], "sample.pdf")


def test_ai_extraction_requires_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GROQ_API_KEY is missing"):
        instruction_extractor.extract_instructions(
            [{"page": 1, "text": "Example instruction"}],
            "sample.pdf",
        )


def test_ai_extraction_validates_json_response(monkeypatch):
    class FakeGroq:
        def __init__(self, api_key):
            assert api_key == "test-key"
            self.chat = self
            self.completions = self

        def create(self, **kwargs):
            payload = {
                "document_name": "sample.pdf",
                "medications": [
                    {
                        "medication_name": "Exampleton",
                        "dosage": "One tablet",
                        "source_page": 1,
                    }
                ],
                "warnings": "",
                "extraction_notes": None,
            }
            message = type("Message", (), {"content": json.dumps(payload)})()
            choice = type("Choice", (), {"message": message})()
            return type("Response", (), {"choices": [choice]})()

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr(instruction_extractor, "Groq", FakeGroq)

    result = instruction_extractor.extract_instructions(
        [{"page": 1, "text": "Exampleton: one tablet"}],
        "sample.pdf",
    )

    assert result.document_name == "sample.pdf"
    assert result.medications[0].dosage == "One tablet"
    assert result.warnings == []
    assert result.extraction_notes == []

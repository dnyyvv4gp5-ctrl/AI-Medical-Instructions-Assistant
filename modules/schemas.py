from pydantic import BaseModel, Field, field_validator


class MedicationInstruction(BaseModel):
    medication_name: str
    dosage: str | None = None
    route: str | None = None
    frequency: str | None = None
    timing: str | None = None
    duration: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    source_page: int | None = None
    needs_review: bool = True
    review_reason: str | None = None


class GeneralInstruction(BaseModel):
    instruction: str
    category: str | None = None
    source_page: int | None = None
    needs_review: bool = True


class FollowUpInstruction(BaseModel):
    instruction: str
    date: str | None = None
    source_page: int | None = None
    needs_review: bool = True


class MedicalInstructionDocument(BaseModel):
    document_name: str
    medications: list[MedicationInstruction] = Field(default_factory=list)
    general_instructions: list[GeneralInstruction] = Field(default_factory=list)
    follow_ups: list[FollowUpInstruction] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    extraction_notes: list[str] = Field(default_factory=list)

    @field_validator("warnings", "extraction_notes", mode="before")
    @classmethod
    def normalize_text_lists(cls, value):
        if value is None or value == "":
            return []
        if isinstance(value, str):
            return [value]
        return value
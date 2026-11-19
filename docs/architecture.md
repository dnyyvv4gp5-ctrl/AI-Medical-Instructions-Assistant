# Architecture

## System Overview

The application is a Streamlit-based prototype organised into four main
stages:

1.  PDF text extraction
2.  AI-based instruction extraction
3.  Structured validation and human review
4.  User-approved reminder management

The application is designed to organise information already present in a
document. It is not intended to interpret medical conditions or make
clinical decisions.

## Component Responsibilities

### Streamlit application --- `app/main.py`

Provides the user interface and coordinates the workflow. The interface
includes document upload and extraction, a review area for extracted
information, and reminder-management views.

### PDF processor --- `modules/pdf_processor.py`

Uses PyMuPDF to read uploaded PDF files and extract text page by page.
Page information is retained so extracted items can be associated with
their source. Empty, invalid or unsupported PDFs are rejected. OCR for
scanned documents is not implemented.

### Instruction extractor --- `modules/instruction_extractor.py`

Sends extracted document text to a Groq-hosted language model with
instructions to return structured information. The extraction prompt is
designed to avoid inventing or changing medication details, preserve
uncertainty, identify missing information and retain source-page
references. The model output is parsed and validated before being used
by the application.

### Data schemas --- `modules/schemas.py`

Uses Pydantic models to represent medication instructions, general
instructions, follow-up information and the overall extracted document.
Missing or uncertain values can be represented rather than silently
filled in. Optional warning and note fields are normalised to
predictable list values.

### Reminder manager --- `modules/reminder_manager.py`

Uses SQLite to persist reminder records. It supports creating, listing,
retrieving, updating status and deleting reminders. Reminder creation
requires explicit approval from the application workflow.

### Tests --- `tests/test_medical_assistant.py`

Contains automated tests for schema handling, PDF processing, reminder
operations and AI-extraction input/output behaviour. External model
responses are mocked in unit tests where appropriate, so the tests do
not depend on a live model request.

## Data Flow

1.  A user uploads a PDF through the Streamlit interface.
2.  The PDF processor extracts readable text and page numbers.
3.  The instruction extractor submits the extracted text to the
    configured Groq model.
4.  The returned structured data is validated against the Pydantic
    schemas.
5.  The application displays the extracted details and source references
    for human review.
6.  The user reviews the information and explicitly approves a reminder.
7.  The reminder manager stores the approved reminder in the local
    SQLite database.
8.  The user can view reminders and update their status or delete them.

## Trust and Safety Considerations

-   The source document remains the reference point; AI output must be
    checked against it.
-   Missing or unclear information should remain missing or be flagged
    for review, not guessed.
-   The extraction workflow must not calculate, alter or recommend
    medication dosages.
-   Reminder creation is gated by explicit user approval.
-   The prototype does not provide clinical advice, diagnosis, treatment
    recommendations or emergency alerts.
-   Demonstrations should use fictional documents rather than real
    patient records.

## Current Constraints

-   PDF text extraction supports text-based documents; OCR is not
    included.
-   Model output can contain errors despite structured validation.
-   SQLite is local application storage. Hosted environments may have
    ephemeral storage, so persistence across restarts is not guaranteed.
-   The reminder feature is an in-app record-management workflow, not a
    background scheduler or push-notification service.

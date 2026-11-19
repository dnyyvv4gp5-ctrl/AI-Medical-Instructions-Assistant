# AI Medical Instructions & Reminder Assistant

A portfolio prototype that uses document intelligence and generative AI
to extract structured information from medical-instruction PDFs and help
users manage reminders.

## Overview

The application demonstrates a workflow for turning information in a
text-based PDF into structured, reviewable instructions. Users can
upload a document, extract medication details, general instructions and
follow-up information, review the results against the source, and create
reminders after explicitly approving them.

## Features

-   **PDF processing:** Extracts readable text page by page with
    PyMuPDF.
-   **AI extraction:** Uses a Groq-hosted large language model to
    identify medication details, general instructions and follow-up
    appointments.
-   **Structured validation:** Uses Pydantic schemas to validate
    extracted data and represent missing or uncertain information.
-   **Source references:** Retains source-page references to support
    manual comparison with the original document.
-   **Human review:** Presents extracted information for review and
    supports medication verification.
-   **Reminder management:** Creates, lists, updates and deletes
    reminders using SQLite.
-   **Explicit approval:** Reminder creation requires user confirmation.
-   **Streamlit interface:** Provides document, review and reminder
    sections, with light and dark themes.

## Technology Stack

-   Python and Streamlit
-   Groq API and large language models
-   PyMuPDF
-   Pydantic
-   SQLite
-   Pytest
-   python-dotenv

## Project Structure

``` text
AI-Medical-Instructions-Assistant/
├── app/
│   └── main.py
├── modules/
│   ├── schemas.py
│   ├── pdf_processor.py
│   ├── instruction_extractor.py
│   └── reminder_manager.py
├── tests/
│   └── test_medical_assistant.py
├── docs/
│   └── architecture.md
├── data/
├── .gitignore
├── requirements.txt
└── README.md
```

## Run Locally

1.  Clone the repository.

2.  Create and activate a virtual environment:

    ``` bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  Install dependencies:

    ``` bash
    pip install -r requirements.txt
    ```

4.  Create a `.env` file in the project root and add your Groq API key:

    ``` text
    GROQ_API_KEY=your_api_key
    ```

5.  Start the application:

    ``` bash
    streamlit run app/main.py
    ```

## Run Tests

``` bash
python -m pytest -q
```

The current local test suite contains 12 passing tests covering schema
validation, PDF processing, reminder operations and AI extraction
behaviour.

## Limitations and Safety

-   This is an educational portfolio prototype, not a medical device or
    clinical decision-support system.
-   AI-extracted information may be incomplete or incorrect. Users must
    compare it with the original document and consult a qualified
    healthcare professional when clarification is needed.
-   The application does not diagnose conditions, recommend treatments
    or modify prescribed dosages.
-   Only text-based PDFs are supported. Scanned documents requiring OCR
    are not currently supported.
-   Reminders are stored in a local SQLite database and managed within
    the application. The prototype does not send push notifications or
    guarantee scheduled alerts.
-   Local database storage may not persist across hosted application
    restarts.
-   Use fictional documents for demonstrations. Do not upload real
    patient records or confidential medical information.

## Project Status

The core portfolio MVP has been implemented and tested locally. The
application supports PDF instruction extraction, structured review and
user-approved reminder management. The current test suite reports 12
passing tests.

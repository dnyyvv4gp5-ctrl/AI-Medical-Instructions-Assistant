import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from datetime import datetime, date, time

from modules.pdf_processor import extract_pdf_pages
from modules.instruction_extractor import extract_instructions
from modules.reminder_manager import (
    initialize_database,
    create_reminder,
    get_reminders,
    update_reminder_status,
    delete_reminder,
)

initialize_database()

st.set_page_config(
    page_title="Medical Instructions Assistant",
    page_icon="✚",
    layout="wide"
)

if "theme" not in st.session_state:
    st.session_state.theme = "Light"

if "extracted" not in st.session_state:
    st.session_state.extracted = None

theme = st.sidebar.selectbox(
    "Appearance",
    ["Light", "Dark"],
    index=["Light", "Dark"].index(st.session_state.theme)
)
st.session_state.theme = theme

if theme == "Light":
    bg = "#EFE7DA"
    primary = "#15210D"
    secondary = "#EFE7DA"
else:
    bg = "#15210D"
    primary = "#AA7524"
    secondary = "#AA7524"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg};
        color: {secondary if theme == "Dark" else primary};
    }}
    h1, h2, h3 {{
        color: {primary} !important;
    }}
    [data-testid="stSidebar"] {{
        background-color: {secondary if theme == "Light" else "#15210D"};
    }}
    div.stButton > button {{
        background-color: {primary};
        color: {bg};
        border-radius: 8px;
        border: none;
    }}

    [data-testid="stSidebar"] * {{
        color: {primary if theme == "Light" else secondary} !important;
    }}
    [data-testid="stSidebar"] button,
    [data-testid="stSidebar"] [role="radio"],
    [data-testid="stToolbar"],
    [data-testid="stToolbar"] *,
    [data-testid="stHeader"] button,
    [data-testid="stHeader"] svg {{
        color: {primary if theme == "Light" else secondary} !important;
        fill: {primary if theme == "Light" else secondary} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Medical Instructions Assistant")
st.caption("Understand, review and organize your medical instructions.")

st.info(
    "Portfolio prototype only. This tool extracts document information; "
    "it does not provide medical advice. Always verify extracted instructions "
    "against the original document and consult a healthcare professional "
    "about unclear or conflicting instructions."
)

section = st.sidebar.radio(
    "Workspace",
    ["Document", "Review", "Reminders"]
)

if section == "Document":
    st.header("Upload medical document")

    uploaded_file = st.file_uploader(
        "Choose a PDF",
        type=["pdf"]
    )

    if uploaded_file and st.button("Extract instructions"):
        try:
            with st.spinner("Reading document and extracting instructions..."):
                pages = extract_pdf_pages(uploaded_file.getvalue())
                result = extract_instructions(
                    pages,
                    uploaded_file.name
                )

                st.session_state.extracted = {
                    "result": result,
                    "pages": pages
                }

            st.success("Extraction completed. Please review all results.")

        except Exception as exc:
            st.error(f"Extraction failed: {exc}")

    if st.session_state.extracted:
        result = st.session_state.extracted["result"]
        st.subheader("Extraction summary")
        st.write("Document:", result.document_name)
        st.write("Medications:", len(result.medications))
        st.write("General instructions:", len(result.general_instructions))
        st.write("Follow-ups:", len(result.follow_ups))


elif section == "Review":
    st.header("Review extracted instructions")

    if not st.session_state.extracted:
        st.info("Upload a document and extract instructions first.")
    else:
        result = st.session_state.extracted["result"]
        pages = st.session_state.extracted["pages"]

        st.subheader("Source document text")
        for page in pages:
            with st.expander(f"Source page {page['page']}"):
                st.text(page["text"])

        st.subheader("Medication instructions")

        approved_medications = []

        for index, medication in enumerate(result.medications):
            with st.container(border=True):
                st.write("**Medication:**", medication.medication_name)
                st.write("**Dosage:**", medication.dosage or "Not specified")
                st.write("**Route:**", medication.route or "Not specified")
                st.write("**Frequency:**", medication.frequency or "Not specified")
                st.write("**Timing:**", medication.timing or "Not specified")
                st.write("**Duration:**", medication.duration or "Not specified")
                st.write("**Source page:**", medication.source_page or "Not specified")

                if medication.needs_review:
                    st.warning(
                        medication.review_reason or
                        "Please verify this instruction against the source."
                    )

                approved = st.checkbox(
                    "I have checked this instruction against the source",
                    key=f"med_approval_{index}"
                )

                if approved:
                    approved_medications.append(index)

        st.subheader("General instructions")

        for index, instruction in enumerate(result.general_instructions):
            with st.container(border=True):
                st.write(instruction.instruction)
                st.caption(f"Source page: {instruction.source_page or 'Not specified'}")

                st.checkbox(
                    "I have verified this instruction",
                    key=f"general_approval_{index}"
                )

        st.subheader("Follow-ups")

        for follow_up in result.follow_ups:
            st.write(follow_up.instruction)
            st.caption(f"Date: {follow_up.date or 'Not specified'}")

        if result.warnings:
            st.subheader("Warnings")
            for warning in result.warnings:
                st.warning(warning)

        if result.extraction_notes:
            st.subheader("Extraction notes")
            for note in result.extraction_notes:
                st.write(note)

        st.divider()
        st.write(
            f"Verified medications: {len(approved_medications)} "
            f"of {len(result.medications)}"
        )


elif section == "Reminders":
    st.header("Reminder dashboard")

    reminders = get_reminders()

    upcoming, completed, missed = st.tabs(
        ["Upcoming", "Completed", "Missed"]
    )

    status_tabs = [
        (upcoming, "upcoming"),
        (completed, "completed"),
        (missed, "missed")
    ]

    for tab, status in status_tabs:
        with tab:
            matching = [r for r in reminders if r["status"] == status]

            if not matching:
                st.info("No reminders in this section.")

            for reminder in matching:
                with st.container(border=True):
                    st.write("**Instruction:**", reminder["instruction"])
                    if reminder["medication_name"]:
                        st.write("**Medication:**", reminder["medication_name"])

                    st.write("**Scheduled:**", reminder["scheduled_at"])

                    if status == "upcoming":
                        if st.button("Mark completed", key=f"done_{reminder['id']}"):
                            update_reminder_status(
                                reminder["id"],
                                "completed"
                            )
                            st.rerun()

                        if st.button("Mark missed", key=f"miss_{reminder['id']}"):
                            update_reminder_status(
                                reminder["id"],
                                "missed"
                            )
                            st.rerun()

                    if st.button("Delete", key=f"delete_{reminder['id']}"):
                        delete_reminder(reminder["id"])
                        st.rerun()

    st.divider()
    st.subheader("Create approved reminder")

    if not st.session_state.extracted:
        st.info("Upload and review a document before creating reminders.")
    else:
        result = st.session_state.extracted["result"]

        medication_names = [
            medication.medication_name
            for index, medication in enumerate(result.medications)
            if st.session_state.get(f'med_approval_{index}', False)
        ]

        selected_medication = st.selectbox(
            "Medication",
            medication_names
        ) if medication_names else None

        instruction = st.text_input(
            "Reminder instruction",
            value=selected_medication or ""
        )

        reminder_date = st.date_input(
            "Reminder date",
            min_value=date.today()
        )

        reminder_time = st.time_input(
            "Reminder time",
            value=time(9, 0)
        )

        confirmed = st.checkbox(
            "I have reviewed and approved this reminder."
        )

        if st.button("Save reminder"):
            if not confirmed:
                st.error("Please confirm your approval first.")
            elif not instruction.strip():
                st.error("Enter a reminder instruction.")
            else:
                scheduled = datetime.combine(
                    reminder_date,
                    reminder_time
                ).isoformat()

                create_reminder(
                    instruction=instruction,
                    scheduled_at=scheduled,
                    medication_name=selected_medication,
                    approved=True
                )

                st.success("Reminder saved.")
                st.rerun()
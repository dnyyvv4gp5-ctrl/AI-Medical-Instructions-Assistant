import sqlite3
from pathlib import Path
from datetime import datetime


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "reminders.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instruction TEXT NOT NULL,
                medication_name TEXT,
                scheduled_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'upcoming',
                created_at TEXT NOT NULL
            )
        """)


def create_reminder(
    instruction: str,
    scheduled_at: str,
    medication_name: str | None = None,
    approved: bool = False
):
    if not approved:
        raise PermissionError(
            "User approval is required before creating a reminder."
        )

    try:
        scheduled = datetime.fromisoformat(scheduled_at)
    except ValueError as exc:
        raise ValueError("Invalid reminder date or time.") from exc

    if not instruction.strip():
        raise ValueError("Reminder instruction cannot be empty.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO reminders
            (instruction, medication_name, scheduled_at, status, created_at)
            VALUES (?, ?, ?, 'upcoming', ?)
            """,
            (
                instruction.strip(),
                medication_name,
                scheduled.isoformat(),
                datetime.now().isoformat()
            )
        )
        return cursor.lastrowid


def get_reminders(status: str | None = None):
    with get_connection() as connection:
        if status:
            rows = connection.execute(
                "SELECT * FROM reminders WHERE status = ? ORDER BY scheduled_at",
                (status,)
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT * FROM reminders ORDER BY scheduled_at"
            ).fetchall()

        return [dict(row) for row in rows]


def update_reminder_status(reminder_id: int, status: str):
    allowed = {"upcoming", "completed", "missed"}

    if status not in allowed:
        raise ValueError("Invalid reminder status.")

    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE reminders SET status = ? WHERE id = ?",
            (status, reminder_id)
        )

        if cursor.rowcount == 0:
            raise ValueError("Reminder not found.")


def delete_reminder(reminder_id: int):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM reminders WHERE id = ?",
            (reminder_id,)
        )
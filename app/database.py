import json
import sqlite3
from datetime import datetime


DB_NAME = "zero_touch_ops.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workflow_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workflow TEXT NOT NULL,
            employee_email TEXT,
            status TEXT,
            result_json TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_workflow_run(workflow: str, employee_email: str, status: str, result: dict):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO workflow_runs (
            workflow,
            employee_email,
            status,
            result_json,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            workflow,
            employee_email,
            status,
            json.dumps(result),
            datetime.utcnow().isoformat(),
        ),
    )

    conn.commit()
    conn.close()


def get_workflow_history(limit: int = 50):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, workflow, employee_email, status, result_json, created_at
        FROM workflow_runs
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "workflow": row[1],
            "employee_email": row[2],
            "status": row[3],
            "result": json.loads(row[4]),
            "created_at": row[5],
        }
        for row in rows
    ]*6
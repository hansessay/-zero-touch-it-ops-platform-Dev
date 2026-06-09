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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS approval_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workflow TEXT NOT NULL,
            employee_email TEXT,
            status TEXT NOT NULL,
            request_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            approved_at TEXT,
            rejected_at TEXT
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
            workflow, employee_email, status, result_json, created_at
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
    ]


def create_approval_request(workflow: str, employee_email: str, request_payload: dict):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO approval_requests (
            workflow, employee_email, status, request_json, created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            workflow,
            employee_email,
            "PENDING_APPROVAL",
            json.dumps(request_payload),
            datetime.utcnow().isoformat(),
        ),
    )

    approval_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {
        "approval_id": approval_id,
        "workflow": workflow,
        "employee_email": employee_email,
        "status": "PENDING_APPROVAL",
    }


def get_approval_requests():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, workflow, employee_email, status, request_json, created_at, approved_at, rejected_at
        FROM approval_requests
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "workflow": row[1],
            "employee_email": row[2],
            "status": row[3],
            "request": json.loads(row[4]),
            "created_at": row[5],
            "approved_at": row[6],
            "rejected_at": row[7],
        }
        for row in rows
    ]


def get_approval_request(approval_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, workflow, employee_email, status, request_json, created_at
        FROM approval_requests
        WHERE id = ?
        """,
        (approval_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "workflow": row[1],
        "employee_email": row[2],
        "status": row[3],
        "request": json.loads(row[4]),
        "created_at": row[5],
    }


def mark_approval_approved(approval_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE approval_requests
        SET status = ?, approved_at = ?
        WHERE id = ?
        """,
        ("APPROVED", datetime.utcnow().isoformat(), approval_id),
    )

    conn.commit()
    conn.close()


def mark_approval_rejected(approval_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE approval_requests
        SET status = ?, rejected_at = ?
        WHERE id = ?
        """,
        ("REJECTED", datetime.utcnow().isoformat(), approval_id),
    )

    conn.commit()
    conn.close()
"""SQLite manager for storing plugin data."""

import json
import sqlite3
from typing import Any, Dict, Optional


class DatabaseManager:
    """Simple SQLite wrapper used by the plugin."""

    def __init__(self, db_path: str = "poiskmore.db") -> None:
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self) -> None:
        """Create tables used by the plugin if they do not already exist."""
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user TEXT PRIMARY KEY,
                password TEXT
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY,
                type TEXT,
                lat REAL,
                lon REAL,
                description TEXT
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sitrep (
                id INTEGER PRIMARY KEY,
                type TEXT,
                datetime TEXT,
                sru TEXT,
                zone TEXT,
                notes TEXT
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT
            )
            """
        )
        self.conn.commit()

    # --- basic helpers -------------------------------------------------

    def authenticate(self, user: str, password: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT password FROM users WHERE user=?", (user,))
        stored = cursor.fetchone()
        return bool(stored and stored[0] == password)

    def save_incident(
        self, incident_type: str, lat: float, lon: float, description: str
    ) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO incidents (type, lat, lon, description) VALUES (?, ?, ?, ?)",
            (incident_type, lat, lon, description),
        )
        self.conn.commit()

    def save_sitrep(
        self, sitrep_type: str, datetime: str, sru: str, zone: str, notes: str
    ) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO sitrep (type, datetime, sru, zone, notes) VALUES (?, ?, ?, ?, ?)",
            (sitrep_type, datetime, sru, zone, notes),
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # --- operations API ------------------------------------------------

    def save_operation(self, operation_data: Dict[str, Any]) -> None:
        """Insert or update an operation record."""
        data_json = json.dumps(operation_data)
        cursor = self.conn.cursor()
        op_id = operation_data.get("id")
        if op_id is None:
            cursor.execute("INSERT INTO operations (data) VALUES (?)", (data_json,))
            operation_data["id"] = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE operations SET data=? WHERE id=?", (data_json, op_id)
            )
        self.conn.commit()

    def load_operation(self, operation_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT data FROM operations WHERE id=?", (operation_id,))
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None

    def archive_operation(self, operation_data: Dict[str, Any]) -> None:
        """Archive an operation by saving it."""
        self.save_operation(operation_data)

    def load_archived_case(self, case_id: int) -> Optional[Dict[str, Any]]:
        return self.load_operation(case_id)

    def has_archived_cases(self) -> bool:
        """Check if any archived operations exist."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT data FROM operations")
        rows = cursor.fetchall()
        for (data_json,) in rows:
            try:
                if json.loads(data_json).get("archived"):
                    return True
            except Exception:
                continue
        return False

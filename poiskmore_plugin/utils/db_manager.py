"""SQLite manager for storing plugin data."""

import json
import sqlite3
import os
from typing import Any, Dict, Optional

class DatabaseManager:
    """Simple SQLite wrapper used by the plugin."""

    def __init__(self, db_path: str = None) -> None:
        # Определяем путь на основе директории плагина
        plugin_dir = os.path.dirname(os.path.dirname(__file__))
        db_dir = os.path.join(plugin_dir, 'data')
        
        # Создаём директорию data, если её нет
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # Устанавливаем путь к БД
        self.db_path = os.path.join(db_dir, 'poiskmore.db') if db_path is None else db_path
        
        # Пытаемся подключиться или создать БД
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.create_tables()
            self.init_default_data()  # Вызов инициализации начальных данных
        except sqlite3.OperationalError as e:
            raise sqlite3.OperationalError(f"Не удалось открыть или создать БД по пути {self.db_path}: {str(e)}")

    def create_tables(self) -> None:
        """Create tables used by the plugin if they do not already exist."""
        with self.conn:
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

    def init_default_data(self) -> None:
        """Initialize default data for the database."""
        with self.conn:
            cursor = self.conn.cursor()

            # Проверка наличия данных в таблице users
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                # Добавляем дефолтного администратора
                cursor.execute(
                    "INSERT INTO users (user, password) VALUES (?, ?)",
                    ("admin", "admin123")  # Пароль можно захешировать (рекомендуется)
                )
                print("Добавлен дефолтный пользователь: admin/admin123")

            # Проверка наличия данных в таблице operations (тестовый архивный случай)
            cursor.execute("SELECT COUNT(*) FROM operations")
            if cursor.fetchone()[0] == 0:
                # Пример архивной операции
                test_operation = {
                    "id": None,
                    "archived": True,
                    "data": {"name": "Тестовая операция", "date": "2025-09-17"}
                }
                cursor.execute("INSERT INTO operations (data) VALUES (?)", (json.dumps(test_operation),))
                print("Добавлена тестовая архивная операция")

    # --- basic helpers -------------------------------------------------

    def authenticate(self, user: str, password: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT password FROM users WHERE user=?", (user,))
        stored = cursor.fetchone()
        return bool(stored and stored[0] == password)

    def save_incident(
        self, incident_type: str, lat: float, lon: float, description: str
    ) -> None:
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO incidents (type, lat, lon, description) VALUES (?, ?, ?, ?)",
                (incident_type, lat, lon, description),
            )

    def save_sitrep(
        self, sitrep_type: str, datetime: str, sru: str, zone: str, notes: str
    ) -> None:
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO sitrep (type, datetime, sru, zone, notes) VALUES (?, ?, ?, ?, ?)",
                (sitrep_type, datetime, sru, zone, notes),
            )

    def close(self) -> None:
        if self.conn:
            self.conn.close()

    # --- operations API ------------------------------------------------

    def save_operation(self, operation_data: Dict[str, Any]) -> None:
        """Insert or update an operation record."""
        data_json = json.dumps(operation_data)
        with self.conn:
            cursor = self.conn.cursor()
            op_id = operation_data.get("id")
            if op_id is None:
                cursor.execute("INSERT INTO operations (data) VALUES (?)", (data_json,))
                operation_data["id"] = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE operations SET data=? WHERE id=?", (data_json, op_id)
                )

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
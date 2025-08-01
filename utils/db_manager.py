"""Простейший менеджер SQLite для хранения данных плагина."""

import sqlite3


class DBManager:
    def __init__(self, db_path: str = "poiskmore.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self) -> None:
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS users (user TEXT PRIMARY KEY, password TEXT)"""
        )
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS incidents (id INTEGER PRIMARY KEY, type TEXT, lat REAL, lon REAL, description TEXT)"""
        )
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS sitrep (id INTEGER PRIMARY KEY, type TEXT, datetime TEXT, sru TEXT, zone TEXT, notes TEXT)"""
        )
        self.conn.commit()

    def authenticate(self, user: str, password: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT password FROM users WHERE user=?", (user,))
        stored = cursor.fetchone()
        return bool(stored and stored[0] == password)

    def save_incident(self, type: str, lat: float, lon: float, description: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO incidents (type, lat, lon, description) VALUES (?, ?, ?, ?)",
            (type, lat, lon, description),
        )
        self.conn.commit()

    def save_sitrep(self, type: str, datetime: str, sru: str, zone: str, notes: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO sitrep (type, datetime, sru, zone, notes) VALUES (?, ?, ?, ?, ?)",
            (type, datetime, sru, zone, notes),
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

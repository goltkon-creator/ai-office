import sqlite3
import json
from datetime import datetime


class Database:
    def __init__(self, path="office.db"):
        self.path = path
        self._init()

    def _init(self):
        with sqlite3.connect(self.path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    brief TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    result TEXT
                )
            """)
            conn.commit()

    def create_task(self, brief: str) -> int:
        with sqlite3.connect(self.path) as conn:
            cur = conn.execute(
                "INSERT INTO tasks (created_at, brief, status) VALUES (?, ?, 'running')",
                (datetime.now().isoformat(), brief)
            )
            conn.commit()
            return cur.lastrowid

    def update_task(self, task_id: int, result: str):
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "UPDATE tasks SET status='done', result=? WHERE id=?",
                (result, task_id)
            )
            conn.commit()

    def get_tasks(self, limit=20) -> list:
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM tasks ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

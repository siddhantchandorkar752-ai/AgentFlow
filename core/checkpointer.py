import sqlite3
import json
from utils.logger import get_logger

logger = get_logger("checkpointer")

class Checkpointer:
    def __init__(self, db_path: str = "agentflow.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    id TEXT PRIMARY KEY,
                    state TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        logger.info("Checkpointer DB initialized")

    def save(self, run_id: str, state: dict):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO checkpoints (id, state) VALUES (?, ?)",
                (run_id, json.dumps(state))
            )
        logger.info(f"State saved: {run_id}")

    def load(self, run_id: str) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT state FROM checkpoints WHERE id = ?", (run_id,)).fetchone()
        if row:
            return json.loads(row[0])
        return {}

    def list_runs(self) -> list:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT id, created_at FROM checkpoints ORDER BY created_at DESC").fetchall()
        return [{"id": r[0], "created_at": r[1]} for r in rows]
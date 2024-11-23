# File: modules/logger.py

from enum import Enum
import sqlite3
from datetime import datetime
import threading
from pathlib import Path
import json


class LogType(Enum):
    GAME = "game"  # Game events (scores, timer, etc)
    SYSTEM = "system"  # System events (startup, shutdown, etc)
    ERROR = "error"  # Errors and warnings
    POWER = "power"  # Power-related events
    NETWORK = "network"  # Network/connectivity events


class LoggerDB:
    def __init__(self, db_path="data/scoreboard.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database and tables"""
        Path(self.db_path).parent.mkdir(exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    log_type TEXT NOT NULL,
                    event TEXT NOT NULL,
                    details TEXT,
                    user TEXT
                )
            """
            )

            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_type ON logs(log_type)")

    def log(
        self, log_type: LogType, event: str, details: dict = None, user: str = None
    ):
        """Add a log entry"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        "INSERT INTO logs (timestamp, log_type, event, details, user) VALUES (?, ?, ?, ?, ?)",
                        (
                            datetime.utcnow().isoformat(),
                            log_type.value,
                            event,
                            json.dumps(details) if details else None,
                            user,
                        ),
                    )
            except Exception as e:
                print(f"Logging error: {e}")

    def get_logs(
        self,
        start_date: str = None,
        end_date: str = None,
        log_types: list = None,
        limit: int = 1000,
    ):
        """Retrieve filtered logs"""
        query = "SELECT * FROM logs WHERE 1=1"
        params = []

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)

        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)

        if log_types:
            placeholders = ",".join("?" * len(log_types))
            query += f" AND log_type IN ({placeholders})"
            params.extend(log_types)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]


# Global logger instance
logger = LoggerDB()

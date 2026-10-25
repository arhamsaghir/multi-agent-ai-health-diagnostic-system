"""SQLite database connection and initialization."""

import sqlite3
import os
from loguru import logger

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "diagnostic.db")

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    user_input TEXT,
    symptoms_json TEXT,
    image_path TEXT,
    patient_history_json TEXT,
    status TEXT DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS diagnoses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    condition_name TEXT NOT NULL,
    confidence REAL NOT NULL,
    severity TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS agent_outputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    output_json TEXT,
    execution_time_ms REAL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS patient_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    age INTEGER,
    bmi REAL,
    gender TEXT,
    heart_rate INTEGER,
    systolic_bp INTEGER,
    diastolic_bp INTEGER,
    temperature REAL,
    oxygen_saturation INTEGER,
    family_history_json TEXT,
    chronic_conditions_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE INDEX IF NOT EXISTS idx_diagnoses_session ON diagnoses(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_outputs_session ON agent_outputs(session_id);
CREATE INDEX IF NOT EXISTS idx_patient_records_session ON patient_records(session_id);
"""


def get_connection(db_path: str = None) -> sqlite3.Connection:
    """Get a SQLite connection with row factory enabled."""
    target_path = db_path if db_path is not None else DATABASE_PATH
    dirname = os.path.dirname(target_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_database(db_path: str = None):
    """Initialize the database and create all tables."""
    target_path = db_path if db_path is not None else DATABASE_PATH
    conn = get_connection(target_path)
    try:
        conn.executescript(CREATE_TABLES_SQL)
        conn.commit()
        logger.info(f"Database initialized at {target_path}")
    finally:
        conn.close()

"""Database repository — CRUD operations for diagnosis sessions."""

import json
from datetime import datetime
from typing import Optional

from src.data.database.connection import get_connection, init_database
from loguru import logger


class DiagnosisRepository:
    """Data access layer for diagnosis sessions and results."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        init_database(db_path)

    def save_session(self, session_id: str, user_input: str, symptoms: list,
                     patient_history: Optional[dict] = None, image_path: Optional[str] = None) -> str:
        """Save a new diagnostic session."""
        conn = get_connection(self.db_path)
        try:
            conn.execute(
                """INSERT INTO sessions (id, created_at, user_input, symptoms_json, image_path, patient_history_json, status)
                   VALUES (?, ?, ?, ?, ?, ?, 'completed')""",
                (
                    session_id,
                    datetime.now().isoformat(),
                    user_input,
                    json.dumps(symptoms),
                    image_path,
                    json.dumps(patient_history) if patient_history else None,
                ),
            )
            conn.commit()
            logger.info(f"Session saved: {session_id}")
            return session_id
        finally:
            conn.close()

    def save_diagnosis(self, session_id: str, condition: str, confidence: float, severity: str):
        """Save a diagnosis result."""
        conn = get_connection(self.db_path)
        try:
            conn.execute(
                """INSERT INTO diagnoses (session_id, created_at, condition_name, confidence, severity)
                   VALUES (?, ?, ?, ?, ?)""",
                (session_id, datetime.now().isoformat(), condition, confidence, severity),
            )
            conn.commit()
        finally:
            conn.close()

    def save_agent_output(self, session_id: str, agent_name: str, output: dict, execution_time_ms: float):
        """Save agent execution output for debugging/analysis."""
        conn = get_connection(self.db_path)
        try:
            conn.execute(
                """INSERT INTO agent_outputs (session_id, agent_name, output_json, execution_time_ms, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (session_id, agent_name, json.dumps(output), execution_time_ms, datetime.now().isoformat()),
            )
            conn.commit()
        finally:
            conn.close()

    def save_patient_record(self, session_id: str, patient_data: dict):
        """Save patient vitals and demographics."""
        conn = get_connection(self.db_path)
        try:
            conn.execute(
                """INSERT INTO patient_records
                   (session_id, age, bmi, gender, heart_rate, systolic_bp, diastolic_bp,
                    temperature, oxygen_saturation, family_history_json, chronic_conditions_json, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    session_id,
                    patient_data.get("age"),
                    patient_data.get("bmi"),
                    patient_data.get("gender"),
                    patient_data.get("heart_rate"),
                    patient_data.get("systolic_bp"),
                    patient_data.get("diastolic_bp"),
                    patient_data.get("temperature"),
                    patient_data.get("oxygen_saturation"),
                    json.dumps(patient_data.get("family_history", [])),
                    json.dumps(patient_data.get("chronic_conditions", [])),
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def get_session(self, session_id: str) -> Optional[dict]:
        """Retrieve a session with all related data."""
        conn = get_connection(self.db_path)
        try:
            cursor = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            if not row:
                return None

            session = dict(row)
            session["symptoms"] = json.loads(session["symptoms_json"]) if session["symptoms_json"] else []
            session["patient_history"] = json.loads(session["patient_history_json"]) if session["patient_history_json"] else {}
            session.pop("symptoms_json", None)
            session.pop("patient_history_json", None)

            # Fetch diagnoses
            cursor = conn.execute("SELECT * FROM diagnoses WHERE session_id = ?", (session_id,))
            session["diagnoses"] = [dict(r) for r in cursor.fetchall()]

            # Fetch agent outputs
            cursor = conn.execute("SELECT * FROM agent_outputs WHERE session_id = ?", (session_id,))
            agent_outputs = {}
            for r in cursor.fetchall():
                output_dict = dict(r)
                output_dict["output"] = json.loads(output_dict["output_json"]) if output_dict["output_json"] else {}
                output_dict.pop("output_json", None)
                agent_outputs[output_dict["agent_name"]] = output_dict
            session["agent_outputs"] = agent_outputs

            return session
        finally:
            conn.close()

    def list_sessions(self, limit: int = 20, offset: int = 0) -> list[dict]:
        """List recent diagnostic sessions."""
        conn = get_connection(self.db_path)
        try:
            cursor = conn.execute(
                "SELECT * FROM sessions ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            )
            sessions = []
            for row in cursor.fetchall():
                s = dict(row)
                s["symptoms"] = json.loads(s["symptoms_json"]) if s["symptoms_json"] else []
                s.pop("symptoms_json", None)
                s.pop("patient_history_json", None)
                sessions.append(s)
            return sessions
        finally:
            conn.close()

    def list_sessions_with_diagnoses(self, limit: int = 50, offset: int = 0) -> list[dict]:
        """List recent diagnostic sessions along with their top diagnoses."""
        conn = get_connection(self.db_path)
        try:
            cursor = conn.execute(
                "SELECT * FROM sessions ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            )
            sessions = []
            for row in cursor.fetchall():
                s = dict(row)
                s["symptoms"] = json.loads(s["symptoms_json"]) if s["symptoms_json"] else []
                s.pop("symptoms_json", None)
                s.pop("patient_history_json", None)

                # Fetch diagnoses for this session
                d_cursor = conn.execute(
                    "SELECT condition_name, confidence, severity FROM diagnoses WHERE session_id = ? ORDER BY confidence DESC",
                    (s["id"],)
                )
                diagnoses = [dict(d) for d in d_cursor.fetchall()]
                s["diagnoses"] = diagnoses
                if diagnoses:
                    s["primary_condition"] = diagnoses[0]["condition_name"]
                    s["severity"] = diagnoses[0]["severity"]
                    s["confidence"] = float(diagnoses[0]["confidence"])
                else:
                    s["primary_condition"] = "Undetermined"
                    s["severity"] = "low"
                    s["confidence"] = 0.0

                sessions.append(s)
            return sessions
        finally:
            conn.close()

    def get_session_count(self) -> int:
        """Return total number of sessions."""
        conn = get_connection(self.db_path)
        try:
            cursor = conn.execute("SELECT COUNT(*) as cnt FROM sessions")
            return cursor.fetchone()["cnt"]
        finally:
            conn.close()

"""Tests for the SQLite database layer."""

import os
import tempfile
import pytest
from src.data.database.connection import init_database, get_connection
from src.data.database.repository import DiagnosisRepository


@pytest.fixture
def db_path():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def repo(db_path):
    """Create a repository with temporary database."""
    return DiagnosisRepository(db_path=db_path)


class TestDatabaseConnection:
    """Test database connection and initialization."""

    def test_init_database(self, db_path):
        init_database(db_path)
        assert os.path.exists(db_path)

    def test_get_connection(self, db_path):
        init_database(db_path)
        conn = get_connection(db_path)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        assert "sessions" in tables
        assert "diagnoses" in tables
        assert "agent_outputs" in tables
        assert "patient_records" in tables
        conn.close()


class TestDiagnosisRepository:
    """Test repository CRUD operations."""

    def test_save_and_retrieve_session(self, repo):
        repo.save_session("test-001", "I have a headache", [{"symptom": "headache"}])
        session = repo.get_session("test-001")
        assert session is not None
        assert session["id"] == "test-001"
        assert session["user_input"] == "I have a headache"
        assert len(session["symptoms"]) == 1

    def test_save_diagnosis(self, repo):
        repo.save_session("test-002", "chest pain", [])
        repo.save_diagnosis("test-002", "Acute Coronary Syndrome", 0.85, "severe")
        session = repo.get_session("test-002")
        assert len(session["diagnoses"]) == 1
        assert session["diagnoses"][0]["condition_name"] == "Acute Coronary Syndrome"
        assert session["diagnoses"][0]["confidence"] == 0.85

    def test_save_agent_output(self, repo):
        repo.save_session("test-003", "test", [])
        repo.save_agent_output("test-003", "nlp_agent", {"symptoms": ["fever"]}, 150.0)
        session = repo.get_session("test-003")
        assert "nlp_agent" in session["agent_outputs"]

    def test_save_patient_record(self, repo):
        repo.save_session("test-004", "test", [])
        repo.save_patient_record("test-004", {
            "age": 45, "bmi": 27.5, "gender": "male",
            "family_history": ["diabetes"],
            "chronic_conditions": ["hypertension"],
        })
        # Verify it was saved
        conn = get_connection(repo.db_path)
        cursor = conn.execute("SELECT * FROM patient_records WHERE session_id = ?", ("test-004",))
        row = cursor.fetchone()
        assert row is not None
        assert row["age"] == 45
        assert row["gender"] == "male"
        conn.close()

    def test_list_sessions(self, repo):
        for i in range(5):
            repo.save_session(f"list-{i}", f"test input {i}", [])
        sessions = repo.list_sessions(limit=3)
        assert len(sessions) == 3

    def test_get_nonexistent_session(self, repo):
        result = repo.get_session("does-not-exist")
        assert result is None

    def test_session_count(self, repo):
        assert repo.get_session_count() == 0
        repo.save_session("count-001", "test", [])
        repo.save_session("count-002", "test", [])
        assert repo.get_session_count() == 2

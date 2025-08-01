import os
import pytest

from utils.db_manager import DBManager


@pytest.fixture
def db(tmpdir):
    db_path = os.path.join(tmpdir, "test.db")
    db = DBManager(db_path)
    yield db
    db.close()
    os.remove(db_path)


def test_save_incident(db):
    db.save_incident("test", 60.0, 30.0, "desc")
    cursor = db.conn.cursor()
    cursor.execute("SELECT * FROM incidents")
    result = cursor.fetchone()
    assert result[1] == "test"
    assert result[2] == 60.0
    assert result[3] == 30.0
    assert result[4] == "desc"


def test_save_sitrep(db):
    db.save_sitrep("test", "2023-01-01", "SRU1", "zone1", "notes1")
    cursor = db.conn.cursor()
    cursor.execute("SELECT * FROM sitrep")
    result = cursor.fetchone()
    assert result[1] == "test"
    assert result[2] == "2023-01-01"
    assert result[3] == "SRU1"
    assert result[4] == "zone1"
    assert result[5] == "notes1"

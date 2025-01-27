import sqlite3


UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"
DB_FILE = "test.db"


def table_exists(db_cursor: sqlite3.Cursor, table_name: str) -> bool:
    db_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    return db_cursor.fetchone() is not None

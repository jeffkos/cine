import sqlite3
from contextlib import contextmanager
from typing import Iterator

from config import CINE_DB, RESERVATIONS_DB


def ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    """Add the column to the table if it doesn't already exist."""
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cur.fetchall()]
    if column not in cols:
        try:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            conn.commit()
        except sqlite3.OperationalError:
            pass

@contextmanager
def get_connection(db_path: str = CINE_DB) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(db_path)

    if db_path == CINE_DB:
        ensure_column(conn, "films", "salle", "TEXT DEFAULT 'Utex'")
    elif db_path == RESERVATIONS_DB:
        ensure_column(conn, "reservations", "salle", "TEXT DEFAULT 'Utex'")

    try:
        yield conn
    finally:
        conn.close()

"""SQLite persistence for documents and their ordered tags.

Every operation opens its own connection and commits its own transaction.
"""

import sqlite3
from contextlib import closing

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    owner_id TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    archived INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS document_tags (
    document_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (document_id, position)
);
"""


_UPDATABLE_COLUMNS = {"name": "title", "body": "body"}


class DocumentRepository:
    def __init__(self, database_path: str):
        self.database_path = database_path
        with closing(self._connect()) as conn:
            conn.executescript(SCHEMA)
            conn.commit()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _tags(self, conn, doc_id: int) -> list[str]:
        rows = conn.execute(
            "SELECT tag FROM document_tags WHERE document_id = ? ORDER BY position", (doc_id,)
        ).fetchall()
        return [row["tag"] for row in rows]

    def _record(self, conn, row) -> dict:
        return {
            "id": row["id"],
            "owner_id": row["owner_id"],
            "title": row["title"],
            "body": row["body"],
            "archived": bool(row["archived"]),
            "tags": self._tags(conn, row["id"]),
        }

    def _write_tags(self, conn, doc_id: int, tags: list[str]) -> None:
        conn.execute("DELETE FROM document_tags WHERE document_id = ?", (doc_id,))
        conn.executemany(
            "INSERT INTO document_tags (document_id, position, tag) VALUES (?, ?, ?)",
            [(doc_id, position, tag) for position, tag in enumerate(tags)],
        )

    def insert_document(self, owner_id: str, title: str, body: str, tags: list[str]) -> dict:
        with closing(self._connect()) as conn:
            cursor = conn.execute(
                "INSERT INTO documents (owner_id, title, body) VALUES (?, ?, ?)",
                (owner_id, title, body),
            )
            doc_id = cursor.lastrowid
            self._write_tags(conn, doc_id, tags)
            conn.commit()
            row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
            return self._record(conn, row)

    def get_document(self, doc_id: int) -> dict | None:
        with closing(self._connect()) as conn:
            row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
            return None if row is None else self._record(conn, row)

    def update_document(self, doc_id: int, changes: dict) -> None:
        with closing(self._connect()) as conn:
            for field, value in changes.items():
                if field == "tags":
                    self._write_tags(conn, doc_id, value)
                    continue
                column = _UPDATABLE_COLUMNS.get(field)
                if column is None:
                    continue
                conn.execute(f"UPDATE documents SET {column} = ? WHERE id = ?", (value, doc_id))
            conn.commit()

    def list_documents(self, owner_id: str, limit: int, offset: int) -> list[dict]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT * FROM documents WHERE owner_id = ? AND archived = 0 "
                "ORDER BY id LIMIT ? OFFSET ?",
                (owner_id, limit, offset),
            ).fetchall()
            return [self._record(conn, row) for row in rows]

    def set_archived(self, doc_id: int, archived: bool) -> dict:
        with closing(self._connect()) as conn:
            conn.execute("UPDATE documents SET archived = ? WHERE id = ?", (int(archived), doc_id))
            row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
            record = self._record(conn, row)
            conn.commit()
            return record

    def delete_document(self, doc_id: int) -> None:
        """Remove the document and its tags in one transaction."""
        with closing(self._connect()) as conn:
            conn.execute("DELETE FROM document_tags WHERE document_id = ?", (doc_id,))
            conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            conn.commit()

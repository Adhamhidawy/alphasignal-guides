"""Shared fixtures for every evaluator suite (contract, required, extra, sensitivity).

The application under test is imported from PYTHONPATH, which the harness points at one
source tree per run. Each test gets a fresh temporary SQLite file. No server is started and
no network is used: requests go through FastAPI's in-process TestClient.
"""

import sqlite3

import pytest
from fastapi import Request
from fastapi.testclient import TestClient

NOT_FOUND = {"detail": "Document not found"}


def header_actor(request: Request) -> str:
    """Test stub for an already authenticated identity. Not production authentication."""
    return request.headers.get("X-Actor", "")


class Actor:
    """A synthetic authenticated actor (alice or bob) talking to the in-process app."""

    def __init__(self, client: TestClient, name: str):
        self.client = client
        self.name = name

    def _headers(self, kwargs):
        headers = dict(kwargs.pop("headers", {}) or {})
        headers["X-Actor"] = self.name
        return headers

    def get(self, path, **kwargs):
        return self.client.get(path, headers=self._headers(kwargs), **kwargs)

    def post(self, path, **kwargs):
        return self.client.post(path, headers=self._headers(kwargs), **kwargs)

    def patch(self, path, **kwargs):
        return self.client.patch(path, headers=self._headers(kwargs), **kwargs)

    def delete(self, path, **kwargs):
        return self.client.delete(path, headers=self._headers(kwargs), **kwargs)

    def create(self, title="Untitled", **fields):
        response = self.post("/documents", json={"title": title, **fields})
        assert response.status_code == 201, response.text
        return response.json()


class Store:
    """Reads the SQLite file through a fresh connection, independent of the app's connections."""

    def __init__(self, path: str):
        self.path = path

    def rows(self, sql, params=()):
        conn = sqlite3.connect(self.path)
        try:
            return conn.execute(sql, params).fetchall()
        finally:
            conn.close()

    def document(self, doc_id):
        found = self.rows(
            "SELECT id, owner_id, title, body, archived FROM documents WHERE id = ?", (doc_id,)
        )
        if not found:
            return None
        id_, owner_id, title, body, archived = found[0]
        return {"id": id_, "owner_id": owner_id, "title": title, "body": body, "archived": archived}

    def tags(self, doc_id):
        return [
            row[0]
            for row in self.rows(
                "SELECT tag FROM document_tags WHERE document_id = ? ORDER BY position", (doc_id,)
            )
        ]

    def count(self, table):
        return self.rows(f"SELECT COUNT(*) FROM {table}")[0][0]

    def orphan_tag_rows(self):
        return self.rows(
            "SELECT document_id, tag FROM document_tags "
            "WHERE document_id NOT IN (SELECT id FROM documents)"
        )


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "documents.sqlite3")


@pytest.fixture
def client(db_path):
    from document_api.app import create_app

    app = create_app(db_path, header_actor)
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture
def alice(client):
    return Actor(client, "alice")


@pytest.fixture
def bob(client):
    return Actor(client, "bob")


@pytest.fixture
def store(db_path, client):
    return Store(db_path)

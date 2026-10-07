"""Application factory: wires the repository, service, and routes."""

from fastapi import FastAPI

from .repository import DocumentRepository
from .routes import build_router
from .service import DocumentService


def create_app(database_path: str, actor_resolver) -> FastAPI:
    """Build the app. `actor_resolver` is a FastAPI dependency returning the authenticated actor."""
    service = DocumentService(DocumentRepository(database_path))
    app = FastAPI(title="Document API (synthetic experiment fixture)")
    app.include_router(build_router(service, actor_resolver))
    return app

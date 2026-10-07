"""HTTP routes. Maps requests to service calls and errors to documented responses."""

from fastapi import APIRouter, Depends, HTTPException, Response

from . import exports
from .fields import LIMIT_DEFAULT, OFFSET_DEFAULT, FieldError
from .models import DocumentCreate, DocumentUpdate
from .service import DocumentNotFound
from .token_messages import format_token_message

NOT_FOUND = "Document not found"


def _respond(call):
    try:
        return call()
    except DocumentNotFound:
        raise HTTPException(status_code=404, detail=NOT_FOUND)
    except FieldError as error:
        raise HTTPException(status_code=422, detail=str(error))


def build_router(service, actor_dependency) -> APIRouter:
    router = APIRouter()

    @router.post("/documents", status_code=201)
    def create_document(payload: DocumentCreate, actor: str = Depends(actor_dependency)):
        return _respond(
            lambda: service.create_document(actor, payload.title, payload.body, payload.tags)
        )

    @router.get("/documents")
    def list_documents(
        limit: int = LIMIT_DEFAULT,
        offset: int = OFFSET_DEFAULT,
        actor: str = Depends(actor_dependency),
    ):
        return _respond(lambda: service.list_documents(actor, limit, offset))

    @router.get("/documents/{doc_id}")
    def read_document(doc_id: int, actor: str = Depends(actor_dependency)):
        return _respond(lambda: service.get_document(actor, doc_id))

    @router.patch("/documents/{doc_id}")
    def update_document(
        doc_id: int, payload: DocumentUpdate, actor: str = Depends(actor_dependency)
    ):
        changes = payload.model_dump(exclude_unset=True)
        updated = _respond(lambda: service.update_document(actor, doc_id, changes))
        return {**updated, **changes}

    @router.post("/documents/{doc_id}/archive")
    def archive_document(doc_id: int, actor: str = Depends(actor_dependency)):
        return _respond(lambda: service.archive_document(actor, doc_id))

    @router.post("/documents/{doc_id}/restore")
    def restore_document(doc_id: int, actor: str = Depends(actor_dependency)):
        return _respond(lambda: service.restore_document(actor, doc_id))

    @router.delete("/documents/{doc_id}", status_code=204)
    def delete_document(doc_id: int, actor: str = Depends(actor_dependency)):
        _respond(lambda: service.delete_document(actor, doc_id))
        return Response(status_code=204)

    @router.get("/documents/{doc_id}/export")
    def export_document(doc_id: int, actor: str = Depends(actor_dependency)):
        return _respond(lambda: exports.export_document(service, actor, doc_id))

    @router.get("/exports/documents")
    def export_documents(
        limit: int = LIMIT_DEFAULT,
        offset: int = OFFSET_DEFAULT,
        actor: str = Depends(actor_dependency),
    ):
        return _respond(lambda: exports.export_documents(service, actor, limit, offset))

    @router.get("/token-message")
    def token_message(reason: str = ""):
        message = format_token_message(reason)
        if message is None:
            raise HTTPException(status_code=422, detail="Unknown reason")
        return {"message": message}

    return router

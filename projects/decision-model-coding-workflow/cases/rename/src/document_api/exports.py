"""JSON export assembly. Exports reuse the service's visibility and list contract."""

EXPORT_FORMAT = "document-export/v1"


def export_document(service, actor: str, doc_id: int) -> dict:
    record = service.get_document(actor, doc_id)
    return {"format": EXPORT_FORMAT, "document": record}


def export_documents(service, actor: str, limit: int, offset: int) -> dict:
    records = service.list_documents(actor, limit, offset)
    return {"format": EXPORT_FORMAT, "limit": limit, "offset": offset, "documents": records}

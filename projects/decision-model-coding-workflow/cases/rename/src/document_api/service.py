"""Document operations and actor-based visibility."""

from .fields import normalize_tags, normalize_title, validate_pagination


class DocumentNotFound(LookupError):
    """Raised for absent and foreign documents alike, so callers cannot tell them apart."""


class DocumentService:
    def __init__(self, repo):
        self.repo = repo

    def _visible(self, actor: str, doc_id: int) -> dict:
        record = self.repo.get_document(doc_id)
        if record is None or record["owner_id"] != actor:
            raise DocumentNotFound(doc_id)
        return record

    def create_document(self, actor: str, title: str, body: str, tags: list[str]) -> dict:
        return self.repo.insert_document(actor, normalize_title(title), body, normalize_tags(tags))

    def get_document(self, actor: str, doc_id: int) -> dict:
        return self._visible(actor, doc_id)

    def update_document(self, actor: str, doc_id: int, changes: dict) -> dict:
        self._visible(actor, doc_id)
        clean = {}
        if changes.get("title") is not None:
            clean["title"] = normalize_title(changes["title"])
        if changes.get("body") is not None:
            clean["body"] = changes["body"]
        if changes.get("tags") is not None:
            clean["tags"] = normalize_tags(changes["tags"])
        self.repo.update_document(doc_id, clean)
        return self.repo.get_document(doc_id)

    def list_documents(self, actor: str, limit: int, offset: int) -> list[dict]:
        limit, offset = validate_pagination(limit, offset)
        return self.repo.list_documents(actor, limit, offset)

    def archive_document(self, actor: str, doc_id: int) -> dict:
        self._visible(actor, doc_id)
        return self.repo.set_archived(doc_id, True)

    def restore_document(self, actor: str, doc_id: int) -> dict:
        self._visible(actor, doc_id)
        return self.repo.set_archived(doc_id, False)

    def delete_document(self, actor: str, doc_id: int) -> None:
        self._visible(actor, doc_id)
        self.repo.delete_document(doc_id)

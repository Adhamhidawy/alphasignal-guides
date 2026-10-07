"""Request fields accepted by the document API."""

from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    title: str
    body: str = ""
    tags: list[str] = Field(default_factory=list)


class DocumentUpdate(BaseModel):
    """Fields a PATCH may change. Ownership is not among them."""

    title: str | None = None
    body: str | None = None
    tags: list[str] | None = None

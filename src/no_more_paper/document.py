from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DocumentState(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"


class DocumentId(BaseModel):
    public_id: str


class DocumentOut(BaseModel):
    public_id: str
    state: DocumentState
    created_at: datetime
    title: str | None = None
    tags: list[str] = Field(default_factory=list)
    image_url: str | None = None
    index_number: int | None = None


class Document(BaseModel):
    id: int
    public_id: str
    user_id: int
    state: DocumentState
    created_at: datetime
    title: str | None = None
    tags: list[str] = Field(default_factory=list)
    image_url: str | None = None
    index_number: int | None = None

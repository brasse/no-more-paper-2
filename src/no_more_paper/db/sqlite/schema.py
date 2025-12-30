from sqlalchemy import (
    Column,
    Engine,
    Enum,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
)

from no_more_paper.document import DocumentState

metadata = MetaData()

documents = Table(
    "documents",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("public_id", String(32), nullable=False, unique=True, index=True),
    Column("user_id", Integer, nullable=False, index=True),
    Column("state", Enum(DocumentState), nullable=False),
    Column("title", Text, nullable=True),
    Column("created_at", Text, nullable=False),
    Column("image_url", Text, nullable=True),
    Column("index_number", Integer, nullable=True),
)

tags = Table(
    "tags",
    metadata,
    Column("document_id", Integer, ForeignKey("documents.id"), primary_key=True),
    Column("tag", String(32), primary_key=True),
)

document_counters = Table(
    "document_counters",
    metadata,
    Column("user_id", Integer, primary_key=True),
    Column("next_index_number", Integer, nullable=False),
)


def init_schema(engine: Engine) -> None:
    metadata.create_all(engine)

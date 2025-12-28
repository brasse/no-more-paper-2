from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import (
    Connection,
    ForeignKey,
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Text,
    Enum,
    insert,
    select,
    update,
)
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from document import DocumentDb, DocumentState

DB_PATH = Path("documents.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f"sqlite+pysqlite:///{DB_PATH}",
    future=True,
    connect_args={"check_same_thread": False},  # FastAPI friendliness
)

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


class DocumentNotFoundError(Exception): ...


class AlreadyIndexedError(Exception): ...


def init_db() -> None:
    metadata.create_all(engine)


def create_document(*, user_id: int, public_id: str) -> DocumentDb:
    stmt = (
        insert(documents)
        .values(
            user_id=user_id,
            public_id=public_id,
            state=DocumentState.DRAFT,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        .returning(*documents.c)
    )
    with engine.begin() as conn:
        row = conn.execute(stmt).mappings().one()
    return DocumentDb.model_validate(row)


def get_document_by_public_id(user_id: int, public_id: str) -> DocumentDb:
    stmt = select(documents).where(
        documents.c.user_id == user_id,
        documents.c.public_id == public_id,
    )
    with engine.connect() as conn:
        row = conn.execute(stmt).mappings().first()
    if row:
        return DocumentDb.model_validate(row)

    raise DocumentNotFoundError()


def get_all_documents(user_id: int) -> list[DocumentDb]:
    stmt = select(documents).where(documents.c.user_id == user_id)
    with engine.connect() as conn:
        rows = conn.execute(stmt).mappings().all()
    return [DocumentDb.model_validate(row) for row in rows]


def _get_index_number(conn: Connection, user_id: int) -> int:
    stmt = (
        sqlite_insert(document_counters)
        .values(user_id=user_id, next_index_number=1)
        .on_conflict_do_update(
            index_elements=[document_counters.c.user_id],
            set_={"next_index_number": document_counters.c.next_index_number + 1},
        )
        .returning(document_counters.c.next_index_number)
    )
    return conn.execute(stmt).scalar_one()


def index_document(user_id: int, public_id: str) -> DocumentDb:
    with engine.begin() as conn:
        index_number = _get_index_number(conn, user_id)
        stmt = (
            update(documents)
            .where(
                documents.c.user_id == user_id,
                documents.c.public_id == public_id,
                documents.c.index_number.is_(None),
            )
            .values(index_number=index_number)
            .returning(*documents.c)
        )
        row = conn.execute(stmt).mappings().first()
        if row:
            return DocumentDb.model_validate(row)

        check = conn.execute(
            select(documents.c.index_number)
            .where(documents.c.user_id == user_id, documents.c.public_id == public_id)
            .limit(1)
        ).first()

        if check is None:
            raise DocumentNotFoundError()
        else:
            raise AlreadyIndexedError()


def deindex_document(user_id: int, public_id: str) -> DocumentDb:
    stmt = (
        update(documents)
        .where(
            documents.c.user_id == user_id,
            documents.c.public_id == public_id,
        )
        .values(index_number=None)
        .returning(*documents.c)
    )
    with engine.begin() as conn:
        row = conn.execute(stmt).mappings().first()
    if row:
        return DocumentDb.model_validate(row)

    raise DocumentNotFoundError()

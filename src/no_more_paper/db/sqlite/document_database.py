from datetime import UTC, datetime

from sqlalchemy import (
    Connection,
    Engine,
    insert,
    select,
    update,
)
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from no_more_paper.db.document_database import (
    AlreadyIndexedError,
    DocumentDatabase,
    DocumentNotFoundError,
)
from no_more_paper.db.sqlite.schema import document_counters, documents
from no_more_paper.document import Document, DocumentState


class SqliteDocumentDatabase(DocumentDatabase):
    def __init__(self, engine: Engine):
        self.engine = engine

    def create_document(self, user_id: int, public_id: str) -> Document:
        stmt = (
            insert(documents)
            .values(
                user_id=user_id,
                public_id=public_id,
                state=DocumentState.DRAFT,
                created_at=datetime.now(UTC).isoformat(),
            )
            .returning(*documents.c)
        )
        with self.engine.begin() as conn:
            row = conn.execute(stmt).mappings().one()
        return Document.model_validate(row)

    def get_document_by_public_id(self, user_id: int, public_id: str) -> Document:
        stmt = select(documents).where(
            documents.c.user_id == user_id,
            documents.c.public_id == public_id,
        )
        with self.engine.connect() as conn:
            row = conn.execute(stmt).mappings().first()
        if row:
            return Document.model_validate(row)

        raise DocumentNotFoundError()

    def get_all_documents(self, user_id: int) -> list[Document]:
        stmt = select(documents).where(documents.c.user_id == user_id)
        with self.engine.connect() as conn:
            rows = conn.execute(stmt).mappings().all()
        return [Document.model_validate(row) for row in rows]

    def _get_index_number(self, conn: Connection, user_id: int) -> int:
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

    def index_document(self, user_id: int, public_id: str) -> Document:
        with self.engine.begin() as conn:
            index_number = self._get_index_number(conn, user_id)
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
                return Document.model_validate(row)

            check = conn.execute(
                select(documents.c.index_number)
                .where(
                    documents.c.user_id == user_id, documents.c.public_id == public_id
                )
                .limit(1)
            ).first()

            if check is None:
                raise DocumentNotFoundError()
            else:
                raise AlreadyIndexedError()

    def deindex_document(self, user_id: int, public_id: str) -> Document:
        stmt = (
            update(documents)
            .where(
                documents.c.user_id == user_id,
                documents.c.public_id == public_id,
            )
            .values(index_number=None)
            .returning(*documents.c)
        )
        with self.engine.begin() as conn:
            row = conn.execute(stmt).mappings().first()
        if row:
            return Document.model_validate(row)

        raise DocumentNotFoundError()

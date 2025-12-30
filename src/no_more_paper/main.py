from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from no_more_paper.api.documents import router as documents_router
from no_more_paper.db.sqlite_document_database import SqliteDocumentDatabase

DB_PATH = Path("documents.db")


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201
    db = SqliteDocumentDatabase(DB_PATH)
    app.state.document_db = db
    yield
    db.close()


app = FastAPI(lifespan=lifespan)

app.include_router(documents_router)

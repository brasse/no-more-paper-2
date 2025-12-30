from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from no_more_paper.api.documents import router as documents_router
from no_more_paper.db.sqlite.document_database import SqliteDocumentDatabase
from no_more_paper.db.sqlite.engine import create_engine

DB_PATH = Path("documents.db")


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201
    engine = create_engine(DB_PATH)
    db = SqliteDocumentDatabase(engine)
    app.state.document_db = db
    yield
    engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(documents_router)

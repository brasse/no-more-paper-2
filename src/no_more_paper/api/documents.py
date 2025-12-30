import random
from typing import Annotated, Any

from fastapi import APIRouter, Header, HTTPException, Path, status

from no_more_paper.db import sqlite_database
from no_more_paper.document import DocumentId, DocumentOut

router = APIRouter(prefix="/documents")

sqlite_database.init_db()


def base62Id(n: int) -> str:
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join([random.choice(chars) for _ in range(n)])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_document(x_user_id: Annotated[int, Header()]) -> DocumentId:
    doc = sqlite_database.create_document(user_id=x_user_id, public_id=base62Id(16))
    return DocumentId(public_id=doc.public_id)


@router.get("/", response_model=list[DocumentOut], response_model_exclude_none=True)
async def get_documents(x_user_id: Annotated[int, Header()]) -> list[Any]:
    return sqlite_database.get_all_documents(x_user_id)


@router.get("/{id}", response_model=DocumentOut, response_model_exclude_none=True)
async def get_document(
    _id: Annotated[str, Path(alias="id")], x_user_id: Annotated[int, Header()]
) -> Any:
    try:
        return sqlite_database.get_document_by_public_id(x_user_id, _id)
    except sqlite_database.DocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e


@router.post(
    "/{id}/index", response_model=DocumentOut, response_model_exclude_none=True
)
async def index_document(
    _id: Annotated[str, Path(alias="id")], x_user_id: Annotated[int, Header()]
) -> Any:
    try:
        return sqlite_database.index_document(x_user_id, _id)
    except sqlite_database.DocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e
    except sqlite_database.AlreadyIndexedError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from e


@router.delete(
    "/{id}/index", response_model=DocumentOut, response_model_exclude_none=True
)
async def deindex_document(
    _id: Annotated[str, Path(alias="id")], x_user_id: Annotated[int, Header()]
) -> Any:
    try:
        return sqlite_database.deindex_document(x_user_id, _id)
    except sqlite_database.DocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e

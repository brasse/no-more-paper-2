import random
from typing import Annotated

from fastapi import FastAPI, HTTPException, Header, Path, status

import store
from document import Document, DocumentId

app = FastAPI()


def base62Id(n: int):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join([random.choice(chars) for _ in range(n)])


store.init_db()


@app.post("/documents/", status_code=status.HTTP_201_CREATED)
async def create_document(x_user_id: Annotated[int, Header()]) -> DocumentId:
    doc = store.create_document(user_id=x_user_id, public_id=base62Id(16))
    return DocumentId(public_id=doc.public_id)


@app.get("/documents/", response_model=list[Document], response_model_exclude_none=True)
async def get_documents(x_user_id: Annotated[int, Header()]):
    return store.get_all_documents(x_user_id)


@app.get("/documents/{id}", response_model=Document, response_model_exclude_none=True)
async def get_document(
    _id: Annotated[str, Path(alias="id")], x_user_id: Annotated[int, Header()]
):
    try:
        return store.get_document_by_public_id(x_user_id, _id)
    except store.DocumentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.post(
    "/documents/{id}/index", response_model=Document, response_model_exclude_none=True
)
async def index_document(
    _id: Annotated[str, Path(alias="id")], x_user_id: Annotated[int, Header()]
):
    try:
        return store.index_document(x_user_id, _id)
    except store.DocumentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except store.AlreadyIndexedError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@app.delete(
    "/documents/{id}/index", response_model=Document, response_model_exclude_none=True
)
async def deindex_document(
    _id: Annotated[str, Path(alias="id")], x_user_id: Annotated[int, Header()]
):
    try:
        return store.deindex_document(x_user_id, _id)
    except store.DocumentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

import random
from typing import Annotated, Any

from fastapi import FastAPI, Header, HTTPException, Path, status

from no_more_paper import store
from no_more_paper.document import Document, DocumentId

app = FastAPI()


def base62Id(n: int) -> str:
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join([random.choice(chars) for _ in range(n)])


store.init_db()


@app.post("/documents/", status_code=status.HTTP_201_CREATED)
async def create_document(x_user_id: Annotated[int, Header()]) -> DocumentId:
    doc = store.create_document(user_id=x_user_id, public_id=base62Id(16))
    return DocumentId(public_id=doc.public_id)


@app.get("/documents/", response_model=list[Document], response_model_exclude_none=True)
async def get_documents(x_user_id: Annotated[int, Header()]) -> list[Any]:
    return store.get_all_documents(x_user_id)


@app.get("/documents/{id}", response_model=Document, response_model_exclude_none=True)
async def get_document(
    _id: Annotated[str, Path(alias="id")], x_user_id: Annotated[int, Header()]
) -> Any:
    try:
        return store.get_document_by_public_id(x_user_id, _id)
    except store.DocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e


@app.post(
    "/documents/{id}/index", response_model=Document, response_model_exclude_none=True
)
async def index_document(
    _id: Annotated[str, Path(alias="id")], x_user_id: Annotated[int, Header()]
) -> Any:
    try:
        return store.index_document(x_user_id, _id)
    except store.DocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e
    except store.AlreadyIndexedError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from e


@app.delete(
    "/documents/{id}/index", response_model=Document, response_model_exclude_none=True
)
async def deindex_document(
    _id: Annotated[str, Path(alias="id")], x_user_id: Annotated[int, Header()]
) -> Any:
    try:
        return store.deindex_document(x_user_id, _id)
    except store.DocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e

from fastapi import FastAPI

from no_more_paper.api.documents import router as documents_router

app = FastAPI()

app.include_router(documents_router)

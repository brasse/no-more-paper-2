from fastapi import Request

from no_more_paper.db.document_database import DocumentDatabase


def get_document_database(request: Request) -> DocumentDatabase:
    return request.app.state.document_db

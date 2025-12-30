from abc import ABC, abstractmethod

from no_more_paper.document import Document


class DocumentNotFoundError(Exception): ...


class AlreadyIndexedError(Exception): ...


class DocumentDatabase(ABC):
    @abstractmethod
    def create_document(self, user_id: int, public_id: str) -> Document: ...

    @abstractmethod
    def get_document_by_public_id(self, user_id: int, public_id: str) -> Document: ...

    @abstractmethod
    def get_all_documents(self, user_id: int) -> list[Document]: ...

    @abstractmethod
    def index_document(self, user_id: int, public_id: str) -> Document: ...

    @abstractmethod
    def deindex_document(self, user_id: int, public_id: str) -> Document: ...

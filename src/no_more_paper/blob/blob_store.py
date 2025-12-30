from abc import ABC, abstractmethod


class BlobNotFoundError(Exception): ...


class BlobStore(ABC):
    @abstractmethod
    async def put(
        self,
        namespace: str,
        blob_id: bytes,
        blob: bytes,
        *,
        variant: str | None = None,
        ext: str | None = None,
    ) -> None: ...

    @abstractmethod
    async def get(
        self,
        namespace: str,
        blob_id: bytes,
        *,
        variant: str | None = None,
        ext: str | None = None,
    ) -> bytes:
        """
        Retrieve a blob.

        Raises:
            BlobNotFoundError: if the blob does not exist.
        """
        ...

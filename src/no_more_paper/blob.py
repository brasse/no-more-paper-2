import asyncio
import re
from abc import ABC, abstractmethod
from pathlib import Path

NAME_PATTERN = re.compile(r"[a-z0-9_-]+")
EXT_PATTERN = re.compile(r"[a-z0-9]+")


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


class FileSystemBlobStore(BlobStore):
    def __init__(self, root: Path, shard_depth: int, *, create_root: bool = False):
        if shard_depth < 0 or shard_depth > 4:
            raise ValueError("shard_depth must be >= 0 and <= 4")

        self.root = root
        self.shard_depth = shard_depth

        if root.exists():
            if not root.is_dir():
                raise ValueError(f"blob store root is not a directory: {root}")
        else:
            if create_root:
                root.mkdir(parents=True, exist_ok=True)
            else:
                raise FileNotFoundError(f"blob store root does not exist: {root}")

    async def put(
        self,
        namespace: str,
        blob_id: bytes,
        blob: bytes,
        *,
        variant: str | None = None,
        ext: str | None = None,
    ) -> None:
        """
        Store blob under:
          root/<namespace>/shard/<hex_id>[-<variant>][.<ext>]

        Shards are computed from the first `shard_depth` bytes of blob_id.
        Each shard directory is one byte rendered as two hex chars.

        Example:
          shard_depth = 2
          namespace = "foo"
          id = bytes.fromhex("123456")
          variant = "w320"
          ext = "jpg"

        Stored at:
          root/foo/12/34/123456-w320.jpg
        """
        path = self._path(namespace, blob_id, variant=variant, ext=ext)
        await asyncio.to_thread(path.parent.mkdir, parents=True, exist_ok=True)
        await asyncio.to_thread(path.write_bytes, blob)

    async def get(
        self,
        namespace: str,
        blob_id: bytes,
        *,
        variant: str | None = None,
        ext: str | None = None,
    ) -> bytes:
        path = self._path(namespace, blob_id, variant=variant, ext=ext)
        try:
            return await asyncio.to_thread(path.read_bytes)
        except FileNotFoundError as e:
            raise BlobNotFoundError(f"{path}") from e

    def _path(
        self,
        namespace: str,
        blob_id: bytes,
        *,
        variant: str | None = None,
        ext: str | None = None,
    ) -> Path:
        if len(blob_id) < self.shard_depth:
            raise ValueError(f"blob_id must be at least {self.shard_depth} bytes long")

        if not NAME_PATTERN.fullmatch(namespace):
            raise ValueError(f"malformed namespace: {namespace!r}")
        if variant is not None and not NAME_PATTERN.fullmatch(variant):
            raise ValueError(f"malformed variant: {variant!r}")
        if ext is not None and not EXT_PATTERN.fullmatch(ext):
            raise ValueError(f"malformed ext: {ext!r}")

        shard_bytes = blob_id[: self.shard_depth]
        shard_parts = [f"{b:02x}" for b in shard_bytes]

        name = blob_id.hex()
        if variant:
            name += f"-{variant}"
        if ext:
            name += f".{ext}"

        return self.root / namespace / Path(*shard_parts) / name

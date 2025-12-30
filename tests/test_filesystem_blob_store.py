from pathlib import Path

import pytest

from no_more_paper.blob.filesystem_blob_store import (
    BlobNotFoundError,
    FileSystemBlobStore,
)


@pytest.fixture
def store(tmp_path):
    return FileSystemBlobStore(tmp_path, 2)


@pytest.mark.asyncio
async def test_put_and_get_default(store: FileSystemBlobStore, tmp_path: Path):
    namespace = "thumbs"
    blob_id = b"\xaa\xbb\x12\x34"
    payload = b"hello"

    await store.put(namespace, blob_id, payload)
    blob = await store.get(namespace, blob_id)

    assert blob == payload

    expected_path = tmp_path / namespace / "aa" / "bb" / "aabb1234"
    assert expected_path.is_file()


@pytest.mark.asyncio
async def test_put_and_get_with_variant_and_ext(
    store: FileSystemBlobStore, tmp_path: Path
):
    namespace = "thumbs"
    blob_id = b"\xaa\xbb\x12\x34"
    variant = "w320"
    ext = "png"
    payload = b"hello"

    await store.put(namespace, blob_id, payload, variant=variant, ext=ext)
    blob = await store.get(namespace, blob_id, variant=variant, ext=ext)

    assert blob == payload

    expected_path = tmp_path / namespace / "aa" / "bb" / "aabb1234-w320.png"
    assert expected_path.is_file()


@pytest.mark.asyncio
async def test_put_replaces_existing_blob(store: FileSystemBlobStore):
    namespace = "thumbs"
    blob_id = b"\xaa\xbb\x12\x34"
    payload0 = b"hello"
    payload1 = b"bye"

    await store.put(namespace, blob_id, payload0)
    await store.put(namespace, blob_id, payload1)
    blob = await store.get(namespace, blob_id)

    assert blob == payload1


@pytest.mark.asyncio
async def test_get_missing_blob_raises(store: FileSystemBlobStore):
    with pytest.raises(BlobNotFoundError):
        await store.get("thumbs", b"\x01\x02")


@pytest.mark.asyncio
async def test_malformed_namespace_raises(store: FileSystemBlobStore):
    with pytest.raises(ValueError):
        await store.get("THUMBS", b"\x01\x02")


@pytest.mark.asyncio
async def test_malformed_variant_raises(store: FileSystemBlobStore):
    with pytest.raises(ValueError):
        await store.get("thumbs", b"\x01\x02", variant="W320")


@pytest.mark.asyncio
async def test_malformed_ext_raises(store: FileSystemBlobStore):
    with pytest.raises(ValueError):
        await store.get("thumbs", b"\x01\x02", ext=".png")


@pytest.mark.asyncio
async def test_too_short_blob_id_raises(store: FileSystemBlobStore):
    with pytest.raises(ValueError):
        await store.get("thumbs", b"\x01")

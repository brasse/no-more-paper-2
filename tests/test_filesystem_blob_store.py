from pathlib import Path

import pytest

from no_more_paper.blob import BlobNotFoundError, FileSystemBlobStore


@pytest.fixture
def store(tmp_path):
    return FileSystemBlobStore(tmp_path, 2)


@pytest.mark.asyncio
async def test_put_and_get_default(store: FileSystemBlobStore, tmp_path: Path):
    namespace = "ns"
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
    namespace = "ns"
    blob_id = b"\xaa\xbb\x12\x34"
    variant = "thumb"
    ext = "png"
    payload = b"hello"

    await store.put(namespace, blob_id, payload, variant=variant, ext=ext)
    blob = await store.get(namespace, blob_id, variant=variant, ext=ext)

    assert blob == payload

    expected_path = tmp_path / namespace / "aa" / "bb" / "aabb1234-thumb.png"
    assert expected_path.is_file()


@pytest.mark.asyncio
async def test_put_replaces_existing_blob(store: FileSystemBlobStore, tmp_path: Path):
    namespace = "ns"
    blob_id = b"\xaa\xbb\x12\x34"
    payload0 = b"hello"
    payload1 = b"bye"

    await store.put(namespace, blob_id, payload0)
    await store.put(namespace, blob_id, payload1)
    blob = await store.get(namespace, blob_id)

    assert blob == payload1


@pytest.mark.asyncio
async def test_get_missing_blob_raises(store: FileSystemBlobStore, tmp_path: Path):
    with pytest.raises(BlobNotFoundError):
        await store.get("ns", b"\x01\x02")

"""Pluggable storage service: local filesystem (dev) or Azure Blob (prod)."""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from pathlib import Path

import aiofiles

from app.core.config import settings
from app.core.exceptions import StorageError
from app.utils.helpers import new_uuid


class StorageBackend(ABC):
    @abstractmethod
    async def save(self, *, content: bytes, filename: str) -> str: ...

    @abstractmethod
    async def load(self, path: str) -> bytes: ...

    @abstractmethod
    async def delete(self, path: str) -> None: ...


class LocalStorage(StorageBackend):
    def __init__(self, base_path: str) -> None:
        self.base = Path(base_path).resolve()
        self.base.mkdir(parents=True, exist_ok=True)

    async def save(self, *, content: bytes, filename: str) -> str:
        safe = f"{new_uuid()}_{os.path.basename(filename)}"
        target = self.base / safe
        async with aiofiles.open(target, "wb") as f:
            await f.write(content)
        return str(target.relative_to(self.base))

    async def load(self, path: str) -> bytes:
        target = (self.base / path).resolve()
        if not str(target).startswith(str(self.base)):
            raise StorageError("Path traversal detected.")
        async with aiofiles.open(target, "rb") as f:
            return await f.read()

    async def delete(self, path: str) -> None:
        target = (self.base / path).resolve()
        if target.exists():
            target.unlink()


class AzureBlobStorage(StorageBackend):
    def __init__(self, connection_string: str, container: str) -> None:
        from azure.storage.blob.aio import BlobServiceClient  # local import to keep dev lightweight

        if not connection_string:
            raise StorageError("AZURE_STORAGE_CONNECTION_STRING is not configured.")
        self._svc = BlobServiceClient.from_connection_string(connection_string)
        self._container = container

    async def save(self, *, content: bytes, filename: str) -> str:
        blob_name = f"{new_uuid()}_{os.path.basename(filename)}"
        async with self._svc:
            container = self._svc.get_container_client(self._container)
            try:
                await container.create_container()
            except Exception:
                pass
            await container.upload_blob(name=blob_name, data=content, overwrite=False)
        return blob_name

    async def load(self, path: str) -> bytes:
        async with self._svc:
            blob = self._svc.get_blob_client(container=self._container, blob=path)
            stream = await blob.download_blob()
            return await stream.readall()

    async def delete(self, path: str) -> None:
        async with self._svc:
            blob = self._svc.get_blob_client(container=self._container, blob=path)
            await blob.delete_blob()


_singleton: StorageBackend | None = None


def get_storage() -> StorageBackend:
    global _singleton
    if _singleton is not None:
        return _singleton

    if settings.STORAGE_BACKEND == "azure_blob":
        _singleton = AzureBlobStorage(
            connection_string=settings.AZURE_STORAGE_CONNECTION_STRING,
            container=settings.AZURE_STORAGE_CONTAINER,
        )
    else:
        _singleton = LocalStorage(settings.LOCAL_STORAGE_PATH)
    return _singleton

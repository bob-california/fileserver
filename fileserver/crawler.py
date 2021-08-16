import hashlib
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from celery import chain

from . import sqlite
from .app import celery_app


def iter_files(path: Path) -> Iterable[Tuple[str]]:
    """Yield file path in a serializable way for celery task.

    Args:
        path: path of folder to be crawled

    Yields:
        file path
    """
    for file in path.glob("**/*"):
        if not file.is_file():
            continue
        yield (str(file),)


@celery_app.task()
def process_file(file: str) -> Optional[Tuple[str, str, str]]:
    """Generate SHA256 of file

    Args:
        file: path to the file

    Returns:
        SHA256 and path of file
    """
    sha256 = hashlib.sha256()
    byte_array = bytearray(128 * 1024)
    memory_view = memoryview(byte_array)
    with open(file, "rb", buffering=0) as f:
        for n in iter(lambda: f.readinto(memory_view), 0):  # type: ignore
            sha256.update(memory_view[:n])
    return (sha256.hexdigest(), file, file)


@celery_app.task
def upsert_in_db(results: List[Tuple[str, ...]]) -> None:
    """Bulk upsert into DB results from celery tasks.

    Args:
        results: celery tasks results
    """
    query = "INSERT INTO files (hash, path) VALUES (?, ?) ON CONFLICT (hash) DO UPDATE SET path = ?"
    sqlite.bulk_write(query, results)


@celery_app.task()
def crawl(path: str) -> None:
    """Crawl recursively folder to generate SHA of files.

    Args:
        path: path of folder to crawl
    """
    chunk_files = process_file.chunks(iter_files(Path(path)), 100)
    chain(chunk_files.group(), upsert_in_db.s())()

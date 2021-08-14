import hashlib
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from loguru import logger

from . import sqlite


def process_file(file: Path) -> Optional[Dict[str, str]]:
    """Generate SHA256 of file

    Args:
        file: path to the file

    Returns:
        SHA256 and path of file
    """
    if not file.is_file():
        return None
    sha256 = hashlib.sha256()
    byte_array = bytearray(128 * 1024)
    memory_view = memoryview(byte_array)
    with file.open("rb", buffering=0) as f:
        for n in iter(lambda: f.readinto(memory_view), 0):  # type: ignore
            sha256.update(memory_view[:n])
    sha256.update(bytes(file.name, encoding="utf-8"))
    return dict(hash=sha256.hexdigest(), path=str(file))


def crawl(path: Path) -> None:
    """Crawl recursively folder to generate SHA of files.

    Args:
        path: path of folder to crawl
    """
    logger.info(f"Start crawling: {path}")

    query = "INSERT INTO files (hash, path) VALUES (?, ?) ON CONFLICT (hash) DO UPDATE SET path = ?"

    buffer: List[Tuple[str, ...]] = []
    with ThreadPoolExecutor(
        max_workers=int(os.environ.get("NUM_WORKERS", 4))
    ) as executor:
        for result in executor.map(process_file, path.glob("**/*")):
            if result is None:
                continue

            buffer.append((result["hash"], result["path"], result["path"]))

            if len(buffer) == 100:
                sqlite.bulk_write(query, buffer)
                buffer.clear()

    sqlite.bulk_write(query, buffer)
    logger.info("Finish crawling")

from pathlib import Path
from typing import Dict, List

import pydantic
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse

from . import sqlite
from .crawler import crawl

app = FastAPI()


@app.on_event("startup")
async def startup():
    sqlite.write(
        """
        CREATE TABLE IF NOT EXISTS files(
            hash CHAR(64) PRIMARY KEY NOT NULL,
            path TEXT NOT NULL
        )
        """,
    )


@app.get("/files")
def get_files() -> List[Dict[str, str]]:
    return sqlite.read("SELECT * FROM files LIMIT 100")


@app.get("/files/{file_hash}")
def get_file(file_hash: str) -> FileResponse:
    file = sqlite.read_one("SELECT * FROM files WHERE hash = ?", (file_hash,))
    if file is None:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file["path"])


class CrawlRequest(pydantic.BaseModel):
    path: Path


@app.post("/crawl", status_code=200)
async def start_crawl(
    crawl_request: CrawlRequest,
    background_tasks: BackgroundTasks,
) -> None:
    background_tasks.add_task(crawl, crawl_request.path)

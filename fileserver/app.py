import os
from typing import Dict, List

import pydantic
from celery import Celery
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from . import sqlite

celery_app = Celery(
    "celery",
    broker=os.getenv("CELERY_RESULT_BACKEND"),
    backend=os.getenv("CELERY_BROKER_URL"),
)

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
    path: str


@app.post("/crawl", status_code=200)
async def start_crawl(crawl_request: CrawlRequest) -> None:
    celery_app.send_task("fileserver.crawler.crawl", args=[crawl_request.path])

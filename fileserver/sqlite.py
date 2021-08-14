import os
import sqlite3
from typing import Dict, List, Optional, Tuple

from loguru import logger


def dict_factory(cursor: sqlite3.Cursor, row: Tuple[str, ...]) -> Dict[str, str]:
    """Format sqlite result into dictionary"""
    dict_ = {}
    for idx, col in enumerate(cursor.description):
        dict_[col[0]] = row[idx]
    return dict_


def db_connect() -> sqlite3.Connection:
    """Connect to SQLite database."""
    conn = sqlite3.connect(os.environ.get("DB_PATH", "/db/file_hash.db"))
    conn.row_factory = dict_factory
    return conn


def read(query: str, params: Tuple[str, ...] = None) -> List[Dict[str, str]]:
    """Read operation on database."""
    results = []
    try:
        conn = db_connect()
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        results = cur.fetchall()
    except sqlite3.Error as error:
        logger.error(f"SQLITE3 error: {error}")
    finally:
        conn.close()
    return results


def read_one(query: str, params: Tuple[str, ...]) -> Optional[Dict[str, str]]:
    """Read operation on database and return only first result."""
    result = None
    try:
        conn = db_connect()
        cur = conn.cursor()
        cur.execute(query, params)
        result = cur.fetchone()
    except sqlite3.Error as error:
        logger.error(f"SQLITE3 error: {error}")
    finally:
        conn.close()
    return result


def write(query: str, params: List[Tuple[str, ...]] = None):
    """Write operation on database."""
    try:
        conn = db_connect()
        cur = conn.cursor()
        if params is None:
            cur.execute(query)
        else:
            cur.execute(query, params)
        conn.commit()
    except sqlite3.Error as error:
        logger.error(f"SQLITE3 error: {error}")
    finally:
        conn.close()


def bulk_write(query: str, params: List[Tuple[str, ...]]):
    """Bulk write operation on database."""
    try:
        conn = db_connect()
        cur = conn.cursor()
        cur.executemany(query, params)
        conn.commit()
    except sqlite3.Error as error:
        logger.error(f"SQLITE3 error: {error}")
    finally:
        conn.close()

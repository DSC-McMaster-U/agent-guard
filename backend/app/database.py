import os
import psycopg
from fastapi import HTTPException

def get_database_url() -> str:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url or not database_url.strip():
        raise HTTPException(status_code=503, detail="Database unavailable")
    return database_url

def get_connection():
    database_url = get_database_url()
    try:
        connection = psycopg.connect(database_url)
    except psycopg.Error:
        raise HTTPException(status_code=503, detail="Database unavailable") from None
    try:
        yield connection
    finally:
        connection.close()
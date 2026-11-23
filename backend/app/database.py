import os
import psycopg
from fastapi import HTTPException

def get_database_url() -> str:
    database_url = os.environ.get("DATABASE_URL")
    if database_url is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return database_url

def get_connection():
    database_url = get_database_url()
    try:
        connection = psycopg.connect(database_url)
    except psycopg.OperationalError:
        raise HTTPException(status_code=503, detail="Database unavailable") from None
    try:
        yield connection
    finally:
        connection.close()
from pathlib import Path

from sqlalchemy import Engine
from sqlalchemy import create_engine as create_sqlite_engine


def create_engine(db_file: Path) -> Engine:
    return create_sqlite_engine(
        f"sqlite+pysqlite:///{db_file}",
        future=True,
        connect_args={"check_same_thread": False},  # FastAPI friendliness
    )

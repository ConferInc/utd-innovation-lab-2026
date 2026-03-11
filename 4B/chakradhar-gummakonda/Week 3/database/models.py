# database/models.py

import os
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def _get_database_url() -> str:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")


    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return db_url


convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

engine = create_engine(
    _get_database_url(),
    pool_pre_ping=True,
    pool_size=5,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Import schema so all models are registered with Base.metadata
    from database import schema

    Base.metadata.create_all(bind=engine)

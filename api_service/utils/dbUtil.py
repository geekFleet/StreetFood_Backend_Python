from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from functools import lru_cache
import config


# 1. using Pydantic to load configuration
@lru_cache()
def setting():
    return config.Settings()


def database_pgsql_url_config():
    """
    Create a database URL for SQLAlchemy
    """
    return str(
        setting().DB_CONNECTION
        + "://"
        + setting().DB_USERNAME
        + ":"
        + setting().DB_PASSWORD
        + "@"
        + setting().DB_HOST
        + ":"
        + setting().DB_PORT
        + "/"
        + setting().DB_DATABASE
    )


# Create the SQLAlchemy engine
engine = create_engine(database_pgsql_url_config())

# Create a SessionLocal class whose instances are a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create a Base class from which will inherit classes that will be used to create database models (the ORM models)
Base = declarative_base()


def get_db():
    try:
        # Will be used in a single request, and then close it once the request is finished
        db = SessionLocal()
        yield db
    finally:
        db.close()

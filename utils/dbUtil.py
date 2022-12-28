from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import URL
import pyodbc
import os


connection_string = os.environ["CONNECTION_STRING"]

cnxn = pyodbc.connect(connection_string)
cursor = cnxn.cursor()

connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})

# # Create the SQLAlchemy engine
engine = create_engine(connection_url)


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

"""
Database connection setup for the AI Expense Analyzer.

This module reads MySQL credentials from environment variables (.env)
and creates a SQLAlchemy engine + session that the rest of the backend
will use to talk to the database.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load variables from the .env file into the environment
load_dotenv()
MYSQL_SSL_CA = os.getenv("MYSQL_SSL_CA")  # path to Aiven's CA cert - only set in production
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "expense_analyzer")

# Build the connection URL that SQLAlchemy understands
# Format: mysql+mysqlconnector://user:password@host:port/database
DATABASE_URL = (
    f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

# The "engine" manages the actual connections to MySQL
connect_args = {"ssl_ca": MYSQL_SSL_CA} if MYSQL_SSL_CA else {}
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)

# SessionLocal is a factory that creates new database sessions
# (a "session" is a temporary workspace for talking to the DB)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is what our future SQLAlchemy models will inherit from
Base = declarative_base()


def get_db():
    """
    Dependency function for FastAPI routes.
    Opens a database session, hands it to the route function,
    and guarantees it gets closed afterward - even if an error happens.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

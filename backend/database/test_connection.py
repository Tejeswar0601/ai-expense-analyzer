"""
Quick standalone script to test that FastAPI can reach MySQL
using the credentials in .env.

Run with: python backend/database/test_connection.py
"""

from sqlalchemy import text
from connection import engine

try:
    with engine.connect() as conn:
        result = conn.execute(text("SHOW TABLES;"))
        tables = [row[0] for row in result]
        print("✅ Connected to MySQL successfully!")
        print("Tables found in 'expense_analyzer':", tables)
except Exception as e:
    print("❌ Connection failed.")
    print("Error:", e)

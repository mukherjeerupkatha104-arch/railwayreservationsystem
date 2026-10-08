from sqlalchemy import inspect, text
from app.database import engine

def migrate():
    # Small SQLite migration so an existing Level-1 railway.db keeps working.
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if "users" in tables:
        columns = {c["name"] for c in inspector.get_columns("users")}
        if "role" not in columns:
            with engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'CUSTOMER'"
                ))

    if "trains" in tables:
        columns = {c["name"] for c in inspector.get_columns("trains")}
        if "is_active" not in columns:
            with engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE trains ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1"
                ))

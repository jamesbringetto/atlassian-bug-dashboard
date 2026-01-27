"""
Migration script to add AI triage columns to the bugs table.
Run this script after updating to add triage functionality.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


def add_triage_columns():
    """Add AI triage columns to bugs table."""
    print("Adding triage columns to bugs table...")

    # SQL statements to add new columns (IF NOT EXISTS for idempotency)
    alter_statements = [
        "ALTER TABLE bugs ADD COLUMN IF NOT EXISTS triage_category VARCHAR(50)",
        "ALTER TABLE bugs ADD COLUMN IF NOT EXISTS triage_priority VARCHAR(20)",
        "ALTER TABLE bugs ADD COLUMN IF NOT EXISTS triage_urgency VARCHAR(20)",
        "ALTER TABLE bugs ADD COLUMN IF NOT EXISTS triage_team VARCHAR(50)",
        "ALTER TABLE bugs ADD COLUMN IF NOT EXISTS triage_tags VARCHAR(100)[]",
        "ALTER TABLE bugs ADD COLUMN IF NOT EXISTS triage_confidence FLOAT",
        "ALTER TABLE bugs ADD COLUMN IF NOT EXISTS triage_reasoning TEXT",
        "ALTER TABLE bugs ADD COLUMN IF NOT EXISTS triaged_at TIMESTAMP WITH TIME ZONE",
    ]

    # Create indexes for commonly queried triage fields
    index_statements = [
        "CREATE INDEX IF NOT EXISTS idx_bugs_triage_category ON bugs(triage_category)",
        "CREATE INDEX IF NOT EXISTS idx_bugs_triage_team ON bugs(triage_team)",
        "CREATE INDEX IF NOT EXISTS idx_bugs_triage_priority ON bugs(triage_priority)",
    ]

    with engine.connect() as conn:
        for stmt in alter_statements:
            try:
                conn.execute(text(stmt))
                print(f"  ✓ {stmt.split('ADD COLUMN IF NOT EXISTS ')[1].split()[0]}")
            except Exception as e:
                print(f"  ⚠ Warning: {e}")

        for stmt in index_statements:
            try:
                conn.execute(text(stmt))
                idx_name = stmt.split("INDEX IF NOT EXISTS ")[1].split()[0]
                print(f"  ✓ Index: {idx_name}")
            except Exception as e:
                print(f"  ⚠ Warning: {e}")

        conn.commit()

    print("\n✅ Triage columns migration complete!")


if __name__ == "__main__":
    add_triage_columns()

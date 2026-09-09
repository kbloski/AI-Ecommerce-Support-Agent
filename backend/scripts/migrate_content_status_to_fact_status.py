"""Rename content_status to fact_status and migrate its values in app.db."""

import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "app.db"

TABLES = {
    "knowledge_insights": (
        "ix_knowledge_insights_content_status",
        "ix_knowledge_insight_knowledge_type_status",
        "ix_knowledge_insights_fact_status",
        "CREATE INDEX ix_knowledge_insight_knowledge_type_fact_status "
        "ON knowledge_insights (knowledge_id, type, fact_status)",
    ),
    "target_audiences": (
        "ix_target_audiences_content_status",
        "ix_target_audience_knowledge_status",
        "ix_target_audiences_fact_status",
        "CREATE INDEX ix_target_audience_knowledge_fact_status "
        "ON target_audiences (knowledge_id, fact_status)",
    ),
}

VALUE_MAPPING = {
    "approved": "verified",
    "suggested": "unverified",
    "rejected": "disputed",
}


def column_names(cursor: sqlite3.Cursor, table: str) -> set[str]:
    return {row[1] for row in cursor.execute(f'PRAGMA table_info("{table}")')}


def main() -> None:
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()
        cursor.execute("BEGIN IMMEDIATE")

        for table, (old_single, old_composite, new_single, create_composite) in TABLES.items():
            columns = column_names(cursor, table)

            if "content_status" in columns:
                cursor.execute(
                    f'ALTER TABLE "{table}" RENAME COLUMN content_status TO fact_status'
                )
            elif "fact_status" not in columns:
                raise RuntimeError(f"Neither status column exists in {table}")

            for old_value, new_value in VALUE_MAPPING.items():
                cursor.execute(
                    f'UPDATE "{table}" SET fact_status = ? WHERE fact_status = ?',
                    (new_value, old_value),
                )

            invalid = cursor.execute(
                f'SELECT DISTINCT fact_status FROM "{table}" '
                "WHERE fact_status NOT IN ('verified', 'unverified', 'disputed')"
            ).fetchall()
            if invalid:
                raise RuntimeError(f"Unsupported fact_status values in {table}: {invalid}")

            cursor.execute(f'DROP INDEX IF EXISTS "{old_single}"')
            cursor.execute(f'DROP INDEX IF EXISTS "{old_composite}"')
            cursor.execute(
                f'CREATE INDEX IF NOT EXISTS "{new_single}" '
                f'ON "{table}" (fact_status)'
            )
            cursor.execute(create_composite.replace("CREATE INDEX ", "CREATE INDEX IF NOT EXISTS "))

        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    main()

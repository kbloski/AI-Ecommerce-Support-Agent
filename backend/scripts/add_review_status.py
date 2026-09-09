"""Add review_status to insights and target audiences in app.db."""

import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "app.db"
TABLES = ("target_audiences",)


def main() -> None:
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()
        cursor.execute("BEGIN IMMEDIATE")

        for table in TABLES:
            columns = {row[1] for row in cursor.execute(f'PRAGMA table_info("{table}")')}
            if "review_status" not in columns:
                cursor.execute(
                    f'ALTER TABLE "{table}" ADD COLUMN review_status '
                    "VARCHAR(20) NOT NULL DEFAULT 'pending'"
                )

            invalid = cursor.execute(
                f'SELECT DISTINCT review_status FROM "{table}" '
                "WHERE review_status NOT IN ('pending', 'approved', 'rejected')"
            ).fetchall()
            if invalid:
                raise RuntimeError(f"Unsupported review_status values in {table}: {invalid}")

            cursor.execute(
                f'CREATE INDEX IF NOT EXISTS "ix_{table}_review_status" '
                f'ON "{table}" (review_status)'
            )

        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    main()

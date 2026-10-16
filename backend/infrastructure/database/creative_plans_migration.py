import json

from sqlalchemy import MetaData, inspect, text

from domain.models.ad.ad_creative_plan import AdCreativePlan
from infrastructure.database.db import Base


def _legacy_plan_text(value):
    """Preserve all legacy section fields without inventing or discarding content."""
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (ValueError, TypeError):
            return value
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return "" if value is None else str(value)


def migrate_creative_plan_content(engine):
    """Replace legacy sections with plan and format without losing records."""
    if "ad_creative_plans" not in inspect(engine).get_table_names():
        return
    columns = {column["name"] for column in inspect(engine).get_columns("ad_creative_plans")}
    if {"format", "plan"} <= columns and "sections" not in columns:
        return
    if engine.dialect.name != "sqlite":
        raise RuntimeError("Creative plan content migration currently supports SQLite")

    with engine.connect() as conn:
        foreign_keys = conn.exec_driver_sql("PRAGMA foreign_keys").scalar()
        conn.commit()
        conn.exec_driver_sql("PRAGMA foreign_keys=OFF")
        conn.commit()
        try:
            conn.exec_driver_sql("BEGIN")
            metadata = MetaData()
            for table in Base.metadata.sorted_tables:
                table.to_metadata(metadata)
            temporary = AdCreativePlan.__table__.to_metadata(metadata, name="ad_creative_plans_migrated")
            temporary.indexes.clear()
            temporary.create(conn)
            if "is_favorite" in columns:
                conn.execute(text("ALTER TABLE ad_creative_plans_migrated ADD COLUMN is_favorite BOOLEAN NOT NULL DEFAULT 0"))
            concepts = dict(conn.execute(text("SELECT id, format FROM ad_concepts")).all()) if "ad_concepts" in inspect(conn).get_table_names() else {}
            for row in conn.execute(text("SELECT * FROM ad_creative_plans")).mappings().all():
                values = {column.name: row[column.name] for column in temporary.columns if column.name in row}
                values["plan"] = row.get("plan") or _legacy_plan_text(row.get("sections"))
                # Prefer the linked concept format. Legacy standalone plans were
                # scene plans, so default those to video and require review.
                values["format"] = row.get("format") or concepts.get(row.get("ad_concept_id")) or "video"
                if not row.get("format"):
                    values["is_reviewed"] = False
                if "is_favorite" in columns:
                    values["is_favorite"] = row["is_favorite"]
                names = ", ".join('"' + key + '"' for key in values)
                placeholders = ", ".join(":" + key for key in values)
                conn.execute(text(f"INSERT INTO ad_creative_plans_migrated ({names}) VALUES ({placeholders})"), values)
            conn.execute(text("DROP TABLE ad_creative_plans"))
            conn.execute(text("ALTER TABLE ad_creative_plans_migrated RENAME TO ad_creative_plans"))
            for index in AdCreativePlan.__table__.indexes:
                index.create(conn, checkfirst=True)
            if conn.exec_driver_sql("PRAGMA foreign_key_check").all():
                raise RuntimeError("Creative plan migration failed foreign key validation")
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.exec_driver_sql(f"PRAGMA foreign_keys={int(foreign_keys)}")
            conn.commit()

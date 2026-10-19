import json
from pathlib import Path

from sqlalchemy import inspect, text

from domain.models.page.page_blueprint_section import PageBlueprintSection


def migrate_page_blueprint_sections(engine):
    """Convert section requirements into independent, repeatable blueprint sections."""
    if engine.dialect.name != "sqlite":
        raise RuntimeError("Page blueprint sections migration currently supports SQLite")
    catalog_path = Path(__file__).resolve().parents[1] / "pages" / "page_section_types.json"
    catalog = {item["id"]: item for item in json.loads(catalog_path.read_text(encoding="utf-8"))}
    with engine.connect() as conn:
        conn.exec_driver_sql("BEGIN IMMEDIATE")
        try:
            tables = set(inspect(conn).get_table_names())
            if "page_blueprint" not in tables:
                conn.commit()
                return
            previous_violations = set(conn.exec_driver_sql("PRAGMA foreign_key_check").all())
            columns = {column["name"] for column in inspect(conn).get_columns("page_blueprint")}
            if "description" not in columns:
                conn.execute(text("ALTER TABLE page_blueprint ADD COLUMN description TEXT NOT NULL DEFAULT ''"))
            PageBlueprintSection.__table__.create(conn, checkfirst=True)
            if "page_section_requirement" in tables:
                if conn.execute(text("SELECT COUNT(*) FROM page_blueprint_sections")).scalar():
                    raise RuntimeError("Both old requirements and new blueprint sections exist; no data was overwritten")
                rows = conn.execute(text("""
                    SELECT * FROM page_section_requirement
                    WHERE requirement_type != 'excluded'
                    ORDER BY page_blueprint_id, position IS NULL, position, id
                """)).mappings().all()
                positions = {}
                for row in rows:
                    owner = row["page_blueprint_id"]
                    positions[owner] = positions.get(owner, 0) + 1
                    section_type = row["page_section_type_id"]
                    reference = catalog.get(section_type, {})
                    conn.execute(text("""
                        INSERT INTO page_blueprint_sections
                            (id, page_blueprint_id, type, name, purpose, position, is_optional, created_at, updated_at)
                        VALUES (:id, :owner, :type, :name, :purpose, :position, :is_optional,
                            COALESCE(:created_at, CURRENT_TIMESTAMP), COALESCE(:updated_at, CURRENT_TIMESTAMP))
                    """), {
                        "id": row["id"], "owner": owner, "type": section_type,
                        "name": reference.get("name", section_type),
                        "purpose": reference.get("description", section_type),
                        "position": positions[owner], "is_optional": row["requirement_type"] == "optional",
                        "created_at": row.get("created_at"), "updated_at": row.get("updated_at"),
                    })
                conn.execute(text("DROP TABLE page_section_requirement"))
            if set(conn.exec_driver_sql("PRAGMA foreign_key_check").all()) - previous_violations:
                raise RuntimeError("Blueprint sections migration failed foreign key validation")
            conn.commit()
        except Exception:
            conn.rollback()
            raise

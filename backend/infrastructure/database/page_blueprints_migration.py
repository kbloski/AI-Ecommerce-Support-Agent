from sqlalchemy import inspect, text

from domain.models.offer.offer_profile import OfferProfile


RETIRED_PAGE_OUTPUT_TABLES = ("page_copy", "page_content_plan")


def migrate_page_blueprints_to_profiles(engine):
    """Replace the old output pipeline with profile-owned section blueprints."""
    tables = set(inspect(engine).get_table_names())
    legacy_requirements = "page_requirements" in tables
    legacy_blueprint = "page_blueprint" in tables and "offer_profile_id" not in {
        column["name"] for column in inspect(engine).get_columns("page_blueprint")
    }
    if not legacy_requirements and not legacy_blueprint and not tables.intersection(RETIRED_PAGE_OUTPUT_TABLES):
        return
    if engine.dialect.name != "sqlite":
        raise RuntimeError("Page blueprint ownership migration currently supports SQLite")

    with engine.connect() as conn:
        foreign_keys = conn.exec_driver_sql("PRAGMA foreign_keys").scalar()
        previous_violations = set(conn.exec_driver_sql("PRAGMA foreign_key_check").all())
        conn.commit()
        conn.exec_driver_sql("PRAGMA foreign_keys=OFF")
        conn.commit()
        try:
            conn.exec_driver_sql("BEGIN IMMEDIATE")
            # A second development-server process may have completed the migration
            # while this connection was waiting for the SQLite write lock.
            tables = set(inspect(conn).get_table_names())
            legacy_requirements = "page_requirements" in tables
            legacy_blueprint = "page_blueprint" in tables and "offer_profile_id" not in {
                column["name"] for column in inspect(conn).get_columns("page_blueprint")
            }
            owners = {}
            rows = []
            section_rows = []
            if legacy_requirements:
                if "page_blueprint" in tables and not legacy_blueprint:
                    raise RuntimeError("Both legacy requirements and profile blueprints exist; migration rolled back")
                OfferProfile.__table__.create(conn, checkfirst=True)
                rows = conn.execute(text("SELECT * FROM page_requirements")).mappings().all()
                profiles_by_source = {}
                for row in rows:
                    source_id = conn.execute(text("""
                        SELECT b.offer_source_id FROM page_strategy p
                        JOIN message_strategy m ON p.message_strategy_id=m.id
                        JOIN offer_strategy o ON m.offer_strategy_id=o.id
                        JOIN marketing_strategy s ON o.marketing_strategy_id=s.id
                        JOIN brand_marketing b ON s.brand_marketing_id=b.id
                        WHERE p.id=:id
                    """), {"id": row["page_strategy_id"]}).scalar_one_or_none()
                    if source_id is None:
                        raise RuntimeError(f"Cannot resolve profile for Page Requirements {row['id']}; migration rolled back")
                    if source_id not in profiles_by_source:
                        profiles = conn.execute(text(
                            "SELECT id FROM offer_profiles WHERE offer_source_id=:id ORDER BY id"
                        ), {"id": source_id}).scalars().all()
                        if len(profiles) == 1:
                            profiles_by_source[source_id] = profiles[0]
                        else:
                            # Preserve requirements without arbitrarily assigning one of several profiles.
                            created = conn.execute(OfferProfile.__table__.insert().values(
                                offer_source_id=source_id, name="Migrated page blueprints"
                            ))
                            profiles_by_source[source_id] = created.inserted_primary_key[0]
                    owners[row["id"]] = profiles_by_source[source_id]
                if "page_section_requirement" in tables:
                    section_rows = conn.execute(text("SELECT * FROM page_section_requirement")).mappings().all()

            for table in RETIRED_PAGE_OUTPUT_TABLES:
                if table in tables:
                    conn.execute(text(f'DROP TABLE "{table}"'))
            if legacy_blueprint:
                conn.execute(text("DROP TABLE page_blueprint"))

            if legacy_requirements:
                conn.execute(text("""
                    CREATE TABLE page_blueprint (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR NOT NULL,
                        offer_profile_id INTEGER NOT NULL REFERENCES offer_profiles(id) ON DELETE CASCADE,
                        is_favorite BOOLEAN NOT NULL DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                for row in rows:
                    values = dict(row)
                    values["name"] = values.get("name") or f"Page blueprint #{row['id']}"
                    values["offer_profile_id"] = owners[row["id"]]
                    values["is_favorite"] = values.get("is_favorite", 0)
                    conn.execute(text("""
                        INSERT INTO page_blueprint (id, name, offer_profile_id, is_favorite, created_at, updated_at)
                        VALUES (:id, :name, :offer_profile_id, :is_favorite, :created_at, :updated_at)
                    """), {**values, "created_at": values.get("created_at"), "updated_at": values.get("updated_at")})
                if "page_section_requirement" in tables:
                    conn.execute(text("DROP TABLE page_section_requirement"))
                conn.execute(text("""
                    CREATE TABLE page_section_requirement (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        page_blueprint_id INTEGER NOT NULL REFERENCES page_blueprint(id) ON DELETE CASCADE,
                        page_section_type_id VARCHAR NOT NULL,
                        requirement_type VARCHAR NOT NULL,
                        position INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                for row in section_rows:
                    values = dict(row)
                    values["page_blueprint_id"] = row["page_requirements_id"]
                    values["page_section_type_id"] = values.get("page_section_type_id", values.get("page_section_type"))
                    conn.execute(text("""
                        INSERT INTO page_section_requirement
                            (id, page_blueprint_id, page_section_type_id, requirement_type, position, created_at, updated_at)
                        VALUES (:id, :page_blueprint_id, :page_section_type_id, :requirement_type, :position, :created_at, :updated_at)
                    """), {**values, "created_at": values.get("created_at"), "updated_at": values.get("updated_at")})
                conn.execute(text("DROP TABLE page_requirements"))
            if set(conn.exec_driver_sql("PRAGMA foreign_key_check").all()) - previous_violations:
                raise RuntimeError("Page blueprint migration failed foreign key validation")
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.exec_driver_sql(f"PRAGMA foreign_keys={int(foreign_keys)}")
            conn.commit()

from sqlalchemy import inspect, text
from .db import Base, engine
from domain.models import models

def init_db():
    _migrate_app_ollama_settings_to_app_properties()
    _migrate_offers_to_offers_raw()
    _rename_offer_raw_details_column()
    _migrate_offer_profile_to_offer_profiles()
    _repair_offer_profile_additional_contexts_key()
    _migrate_offer_profiles_to_offer_sources()
    _remove_obsolete_offer_source_columns()
    _migrate_checklists_to_offer_sources()
    _migrate_ad_execution_to_ad_setup()
    _migrate_creative_execution_to_generate_ad()
    _migrate_creative_execution_setups()
    _add_missing_favorite_columns()
    _add_missing_is_reviewed_columns()
    _add_missing_ad_strategy_name_column()
    _add_missing_page_strategy_name_column()
    _add_missing_page_requirements_name_column()
    _add_missing_page_content_plan_name_column()
    _add_missing_page_blueprint_columns()
    _rename_page_section_requirement_column()
    _migrate_offer_facts_optional_evidence()
    _migrate_target_audiences_to_offer_profiles()
    _remove_obsolete_target_audience_columns()
    _add_target_audience_desires()
    _add_marketing_angle_fields()
    _add_ad_concept_marketing_angle()
    Base.metadata.create_all(bind=engine)


def _add_ad_concept_marketing_angle():
    with engine.begin() as conn:
        if "ad_concepts" not in inspect(conn).get_table_names():
            return
        columns = {column["name"] for column in inspect(conn).get_columns("ad_concepts")}
        if "marketing_angle_id" not in columns:
            conn.execute(text(
                "ALTER TABLE ad_concepts ADD COLUMN marketing_angle_id INTEGER "
                "REFERENCES marketing_angles(id) ON DELETE SET NULL"
            ))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_ad_concepts_marketing_angle_id "
            "ON ad_concepts(marketing_angle_id)"
        ))


def _add_marketing_angle_fields():
    with engine.begin() as conn:
        if "marketing_angles" not in inspect(conn).get_table_names():
            return
        existing = {column["name"] for column in inspect(conn).get_columns("marketing_angles")}
        for column in ("core_message", "value_proposition", "pain_point", "desire", "emotional_driver"):
            if column not in existing:
                conn.execute(text(f'ALTER TABLE marketing_angles ADD COLUMN "{column}" TEXT NOT NULL DEFAULT \'\''))
        for column in ("supporting_arguments", "proof_points"):
            if column not in existing:
                conn.execute(text(f'ALTER TABLE marketing_angles ADD COLUMN "{column}" JSON NOT NULL DEFAULT \'[]\''))

def _migrate_ad_execution_to_ad_setup():
    """Rename the Ad Execution aggregate without losing existing setup data."""
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    with engine.begin() as conn:
        if "ad_execution" in tables and "ad_setup" in tables:
            legacy_count = conn.execute(
                text('SELECT COUNT(*) FROM "ad_execution"')
            ).scalar_one()
            new_count = conn.execute(
                text('SELECT COUNT(*) FROM "ad_setup"')
            ).scalar_one()

            if legacy_count and new_count:
                raise RuntimeError(
                    "Both legacy 'ad_execution' and new 'ad_setup' tables contain data; "
                    "migration requires manual resolution."
                )

            if legacy_count:
                conn.execute(text('DROP TABLE "ad_setup"'))
                conn.execute(text('ALTER TABLE "ad_execution" RENAME TO "ad_setup"'))
            else:
                conn.execute(text('DROP TABLE "ad_execution"'))
        elif "ad_execution" in tables:
            conn.execute(text('ALTER TABLE "ad_execution" RENAME TO "ad_setup"'))

        if "generate_ads" not in tables:
            return

        columns = {
            column["name"]
            for column in inspect(conn).get_columns("generate_ads")
        }
        if "ad_execution_id" in columns and "ad_setup_id" not in columns:
            conn.execute(
                text(
                    'ALTER TABLE "generate_ads" '
                    'RENAME COLUMN "ad_execution_id" TO "ad_setup_id"'
                )
            )

def _migrate_creative_execution_to_generate_ad():
    """Rename Creative Execution tables and relation keys to Generate Ad."""
    tables = set(inspect(engine).get_table_names())

    def rename_table(conn, legacy_name: str, new_name: str) -> None:
        if legacy_name not in tables:
            return
        if new_name not in tables:
            conn.execute(text(f'ALTER TABLE "{legacy_name}" RENAME TO "{new_name}"'))
            return

        legacy_count = conn.execute(text(f'SELECT COUNT(*) FROM "{legacy_name}"')).scalar_one()
        new_count = conn.execute(text(f'SELECT COUNT(*) FROM "{new_name}"')).scalar_one()
        if legacy_count and new_count:
            raise RuntimeError(
                f"Both legacy '{legacy_name}' and new '{new_name}' tables contain data; "
                "migration requires manual resolution."
            )
        if legacy_count:
            conn.execute(text(f'DROP TABLE "{new_name}"'))
            conn.execute(text(f'ALTER TABLE "{legacy_name}" RENAME TO "{new_name}"'))
        else:
            conn.execute(text(f'DROP TABLE "{legacy_name}"'))

    with engine.begin() as conn:
        rename_table(conn, "generate_ad_setups", "creative_execution_setups")
        rename_table(conn, "creative_executions", "generate_ads")

        current_tables = set(inspect(conn).get_table_names())
        if "creative_execution_setups" in current_tables:
            setup_columns = {
                column["name"]
                for column in inspect(conn).get_columns("creative_execution_setups")
            }
            if "ad_execution_id" in setup_columns and "ad_setup_id" not in setup_columns:
                conn.execute(text(
                    'ALTER TABLE "creative_execution_setups" '
                    'RENAME COLUMN "ad_execution_id" TO "ad_setup_id"'
                ))

        if "generate_ads" in current_tables:
            columns = {column["name"] for column in inspect(conn).get_columns("generate_ads")}
            if "ad_execution_id" in columns and "ad_setup_id" not in columns:
                conn.execute(text(
                    'ALTER TABLE "generate_ads" '
                    'RENAME COLUMN "ad_execution_id" TO "ad_setup_id"'
                ))
                columns = {column["name"] for column in inspect(conn).get_columns("generate_ads")}
            if "generate_ad_setup_id" in columns and "creative_execution_setup_id" not in columns:
                conn.execute(text(
                    'ALTER TABLE "generate_ads" '
                    'RENAME COLUMN "generate_ad_setup_id" TO "creative_execution_setup_id"'
                ))

def _migrate_creative_execution_setups():
    """Persist generation options and attach legacy executions to a default setup."""
    tables = set(inspect(engine).get_table_names())
    if "ad_setup" not in tables:
        return

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS creative_execution_setups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad_setup_id INTEGER NOT NULL REFERENCES ad_setup(id) ON DELETE CASCADE,
                name VARCHAR NOT NULL,
                duration_seconds INTEGER,
                number_of_slides INTEGER,
                ad_framework_id VARCHAR,
                creative_angle_id VARCHAR,
                execution_style_id VARCHAR,
                additional_instructions TEXT,
                is_favorite BOOLEAN NOT NULL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))

        setup_columns = {
            column["name"]
            for column in inspect(conn).get_columns("creative_execution_setups")
        }
        if "configuration_json" in setup_columns:
            conn.execute(text(
                'ALTER TABLE "creative_execution_setups" DROP COLUMN "configuration_json"'
            ))
            setup_columns.remove("configuration_json")

        missing_setup_columns = {
            "duration_seconds": "INTEGER",
            "number_of_slides": "INTEGER",
            "ad_framework_id": "VARCHAR",
            "creative_angle_id": "VARCHAR",
            "execution_style_id": "VARCHAR",
            "additional_instructions": "TEXT",
            "is_favorite": "BOOLEAN NOT NULL DEFAULT 0",
            "created_at": "DATETIME",
            "updated_at": "DATETIME",
        }
        for column_name, definition in missing_setup_columns.items():
            if column_name not in setup_columns:
                conn.execute(text(
                    f'ALTER TABLE "creative_execution_setups" '
                    f'ADD COLUMN "{column_name}" {definition}'
                ))

        conn.execute(text("""
            INSERT INTO creative_execution_setups (
                ad_setup_id, name, duration_seconds, number_of_slides,
                is_favorite
            )
            SELECT
                setup.id,
                'Default setup',
                CASE WHEN setup.creative_type = 'video' THEN 15 ELSE NULL END,
                CASE WHEN setup.creative_type = 'carousel' THEN 5 ELSE NULL END,
                0
            FROM ad_setup AS setup
            WHERE NOT EXISTS (
                SELECT 1 FROM creative_execution_setups AS execution_setup
                WHERE execution_setup.ad_setup_id = setup.id
            )
        """))

        if "generate_ads" not in tables:
            return

        generate_ad_columns = {
            column["name"]: column
            for column in inspect(conn).get_columns("generate_ads")
        }
        columns = set(generate_ad_columns)
        if "creative_execution_setup_id" not in columns:
            conn.execute(text(
                'ALTER TABLE "generate_ads" '
                'ADD COLUMN creative_execution_setup_id INTEGER '
                'REFERENCES creative_execution_setups(id) ON DELETE CASCADE'
            ))

        if "name" not in columns:
            conn.execute(text(
                'ALTER TABLE "generate_ads" ADD COLUMN name VARCHAR'
            ))

        if "ad_setup_id" in columns:
            conn.execute(text("""
                UPDATE generate_ads
                SET creative_execution_setup_id = (
                    SELECT MIN(execution_setup.id)
                    FROM creative_execution_setups AS execution_setup
                    WHERE execution_setup.ad_setup_id = generate_ads.ad_setup_id
                )
                WHERE creative_execution_setup_id IS NULL
            """))

        conn.execute(text("""
            UPDATE generate_ads
            SET name = 'Generated Ad ' || id
            WHERE name IS NULL OR TRIM(name) = ''
        """))

        generate_ad_columns = {
            column["name"]: column
            for column in inspect(conn).get_columns("generate_ads")
        }
        columns = set(generate_ad_columns)

        # SQLite cannot make the newly introduced relation NOT NULL or remove the
        # legacy ad_setup_id safely with ALTER COLUMN. Rebuild the table once all
        # legacy rows have been attached to their default execution setup.
        needs_generate_ads_rebuild = (
            "ad_setup_id" in columns
            or generate_ad_columns.get("creative_execution_setup_id", {}).get("nullable", True)
            or generate_ad_columns.get("name", {}).get("nullable", True)
        )
        if needs_generate_ads_rebuild:
            unmapped_count = conn.execute(text("""
                SELECT COUNT(*)
                FROM generate_ads
                WHERE creative_execution_setup_id IS NULL
            """)).scalar_one()
            if unmapped_count:
                raise RuntimeError(
                    f"Cannot migrate generate_ads: {unmapped_count} rows have no Creative Execution Setup"
                )

            current_tables = set(inspect(conn).get_table_names())
            if "generate_ads_migrated" in current_tables:
                raise RuntimeError(
                    "Temporary table generate_ads_migrated already exists; migration requires manual resolution."
                )

            conn.execute(text("""
                CREATE TABLE generate_ads_migrated (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    creative_execution_setup_id INTEGER NOT NULL
                        REFERENCES creative_execution_setups(id) ON DELETE CASCADE,
                    name VARCHAR NOT NULL,
                    content_json JSON NOT NULL,
                    is_favorite BOOLEAN NOT NULL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("""
                INSERT INTO generate_ads_migrated (
                    id, creative_execution_setup_id, name, content_json,
                    is_favorite, created_at, updated_at
                )
                SELECT
                    id, creative_execution_setup_id, name, content_json,
                    COALESCE(is_favorite, 0), created_at, updated_at
                FROM generate_ads
            """))
            conn.execute(text('DROP TABLE "generate_ads"'))
            conn.execute(text(
                'ALTER TABLE "generate_ads_migrated" RENAME TO "generate_ads"'
            ))

def _migrate_offers_to_offers_raw():
    """Migrate the retired Offer schema before SQLAlchemy creates offers_raw.

    Offer records (and their OfferSource references) are preserved. Offer items,
    insights, and pricing are intentionally removed with this feature.
    """
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    if "offers" not in tables:
        return
    if "offers_raw" in tables:
        raise RuntimeError("Both legacy 'offers' and new 'offers_raw' tables exist; migration requires manual resolution.")

    with engine.begin() as conn:
        for table in ("offer_items", "offer_insights"):
            if table in tables:
                conn.execute(text(f'DROP TABLE "{table}"'))
        conn.execute(text('ALTER TABLE "offers" RENAME TO "offers_raw"'))
        columns = {column["name"] for column in inspect(conn).get_columns("offers_raw")}
        for column in ("buying_price", "selling_price"):
            if column in columns:
                conn.execute(text(f'ALTER TABLE "offers_raw" DROP COLUMN "{column}"'))

def _rename_offer_raw_details_column():
    """Preserve legacy OfferRaw descriptions while adopting the API field name."""
    inspector = inspect(engine)
    if "offers_raw" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("offers_raw")}
    if "details" in columns and "description" not in columns:
        with engine.begin() as conn:
            conn.execute(text('ALTER TABLE "offers_raw" RENAME COLUMN details TO description'))

def _migrate_offer_profile_to_offer_profiles():
    """Preserve the profile graph while renaming the aggregate and its keys."""
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    with engine.begin() as conn:
        for retired_table in ("knowledge_insights", "offer_profile_insights"):
            if retired_table in tables:
                conn.execute(text(f'DROP TABLE "{retired_table}"'))

        if "offer_profiles" not in tables:
            for legacy_table in ("knowledge", "knowledges", "offer_profile"):
                if legacy_table in tables:
                    conn.execute(text(f'ALTER TABLE "{legacy_table}" RENAME TO "offer_profiles"'))
                    break

        if "knowledge_analysis" in tables and "offer_profile_analysis" not in tables:
            conn.execute(text('ALTER TABLE "knowledge_analysis" RENAME TO "offer_profile_analysis"'))

        for table in ("target_audiences", "brand_marketing", "offer_profile_analysis"):
            if table not in tables and not (table == "offer_profile_analysis" and "knowledge_analysis" in tables):
                continue
            columns = {column["name"] for column in inspect(conn).get_columns(table)}
            if "knowledge_id" in columns and "offer_profile_id" not in columns:
                conn.execute(text(f'ALTER TABLE "{table}" RENAME COLUMN knowledge_id TO offer_profile_id'))

def _add_missing_favorite_columns():
    """Additive migration: adds `is_favorite` to tables that already existed
    before this column was introduced (create_all only creates missing
    tables, it never alters existing ones)."""
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    for table in Base.metadata.tables.values():
        if table.name not in existing_tables:
            continue

        columns = {c["name"] for c in inspector.get_columns(table.name)}
        if "is_favorite" not in columns:
            with engine.begin() as conn:
                conn.execute(
                    text(f'ALTER TABLE "{table.name}" ADD COLUMN is_favorite BOOLEAN NOT NULL DEFAULT 0')
                )

def _add_missing_is_reviewed_columns():
    """Add the boolean review marker and preserve values from the retired status field."""
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    for table in ("offer_source_elements", "target_audiences", "checklist_item", "analysis_questions", "ugc_creatives"):
        if table not in existing_tables:
            continue

        columns = {column["name"] for column in inspector.get_columns(table)}
        if "is_reviewed" not in columns:
            with engine.begin() as conn:
                conn.execute(
                    text(
                        f"ALTER TABLE {table} "
                        "ADD COLUMN is_reviewed BOOLEAN NOT NULL DEFAULT 0"
                    )
                )
                if "review_status" in columns:
                    conn.execute(
                        text(
                            f"UPDATE {table} "
                            "SET is_reviewed = CASE "
                        "WHEN review_status = 'pending' THEN 0 ELSE 1 END"
                        )
                    )

def _add_missing_ad_strategy_name_column():
    """Add the generated Ad Strategy name to databases created before this field."""
    inspector = inspect(engine)
    if "ad_strategy" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("ad_strategy")}
    if "name" not in columns:
        with engine.begin() as conn:
            conn.execute(text('ALTER TABLE ad_strategy ADD COLUMN name VARCHAR'))

def _add_missing_page_strategy_name_column():
    """Add a required display name and derive names for existing strategies."""
    inspector = inspect(engine)
    if "page_strategy" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("page_strategy")}
    with engine.begin() as conn:
        if "name" not in columns:
            conn.execute(text(
                "ALTER TABLE page_strategy "
                "ADD COLUMN name VARCHAR NOT NULL DEFAULT 'Page Strategy'"
            ))
        conn.execute(text("""
            UPDATE page_strategy
            SET name = CASE
                WHEN goal IS NOT NULL AND TRIM(goal) != '' THEN SUBSTR(goal, 1, 255)
                ELSE 'Page Strategy ' || id
            END
            WHERE name IS NULL OR TRIM(name) = '' OR name = 'Page Strategy'
        """))

def _add_missing_page_requirements_name_column():
    """Add a required display name and derive one for existing requirements."""
    inspector = inspect(engine)
    if "page_requirements" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("page_requirements")}
    with engine.begin() as conn:
        if "name" not in columns:
            conn.execute(text(
                "ALTER TABLE page_requirements "
                "ADD COLUMN name VARCHAR NOT NULL DEFAULT 'Page Requirements'"
            ))
        conn.execute(text("""
            UPDATE page_requirements
            SET name = 'Page Requirements ' || id
            WHERE name IS NULL OR TRIM(name) = '' OR name = 'Page Requirements'
        """))

def _add_missing_page_content_plan_name_column():
    """Add a required display name and derive one for existing content plans."""
    inspector = inspect(engine)
    if "page_content_plan" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("page_content_plan")}
    with engine.begin() as conn:
        if "name" not in columns:
            conn.execute(text(
                "ALTER TABLE page_content_plan "
                "ADD COLUMN name VARCHAR NOT NULL DEFAULT 'Page Content Plan'"
            ))
        conn.execute(text("""
            UPDATE page_content_plan
            SET name = 'Page Content Plan ' || id
            WHERE name IS NULL OR TRIM(name) = '' OR name = 'Page Content Plan'
        """))

def _add_missing_page_blueprint_columns():
    """Additive migration: adds `page_requirements_id` to `page_blueprint`
    rows created before the PAGE_REQUIREMENTS stage existed. Nullable so
    existing rows (still linked via `page_strategy_id`) stay valid."""
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    if "page_blueprint" not in existing_tables:
        return

    columns = {c["name"] for c in inspector.get_columns("page_blueprint")}
    if "page_requirements_id" not in columns:
        with engine.begin() as conn:
            conn.execute(
                text('ALTER TABLE "page_blueprint" ADD COLUMN page_requirements_id INTEGER')
            )

def _rename_page_section_requirement_column():
    """Renames `page_section_type` to `page_section_type_id` on
    `page_section_requirement` rows created before the field was renamed."""
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    if "page_section_requirement" not in existing_tables:
        return

    columns = {c["name"] for c in inspector.get_columns("page_section_requirement")}
    if "page_section_type" in columns and "page_section_type_id" not in columns:
        with engine.begin() as conn:
            conn.execute(
                text(
                    'ALTER TABLE "page_section_requirement" '
                    'RENAME COLUMN page_section_type TO page_section_type_id'
                )
            )

def _migrate_checklists_to_offer_sources():
    """Replace the retired analysis_checklist link with checklist.offer_source_id."""
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    if "checklist" not in tables:
        return

    columns = {column["name"] for column in inspector.get_columns("checklist")}
    with engine.begin() as conn:
        if "offer_source_id" not in columns:
            conn.execute(text('ALTER TABLE "checklist" ADD COLUMN offer_source_id INTEGER'))

        if {"analysis_checklist", "offer_source_analysis"}.issubset(tables):
            conn.execute(text("""
                UPDATE checklist
                SET offer_source_id = (
                    SELECT offer_source_analysis.offer_source_id
                    FROM analysis_checklist
                    JOIN offer_source_analysis
                      ON offer_source_analysis.analysis_id = analysis_checklist.analysis_id
                    WHERE analysis_checklist.checklist_id = checklist.id
                    LIMIT 1
                )
                WHERE offer_source_id IS NULL
            """))
            conn.execute(text('DROP TABLE "analysis_checklist"'))


def _migrate_app_ollama_settings_to_app_properties():
    """Preserve existing Ollama overrides when renaming application properties."""
    with engine.begin() as conn:
        tables = set(inspect(conn).get_table_names())
        if "app_ollama_settings" not in tables:
            return

        if "app_properties" in tables:
            legacy_count = conn.execute(
                text('SELECT COUNT(*) FROM "app_ollama_settings"')
            ).scalar_one()
            new_count = conn.execute(
                text('SELECT COUNT(*) FROM "app_properties"')
            ).scalar_one()
            if legacy_count and new_count:
                raise RuntimeError(
                    "Both 'app_ollama_settings' and 'app_properties' contain data; "
                    "migration requires manual resolution."
                )
            if not legacy_count:
                conn.execute(text('DROP TABLE "app_ollama_settings"'))
                return
            conn.execute(text('DROP TABLE "app_properties"'))

        conn.execute(text(
            'ALTER TABLE "app_ollama_settings" RENAME TO "app_properties"'
        ))


def _migrate_offer_profiles_to_offer_sources():
    """Rename source tables and relation columns without losing the offer graph."""
    renames = (
        ("offer_profiles", "offer_sources"),
        ("offer_profile_elements", "offer_source_elements"),
        ("offer_profile_analysis", "offer_source_analysis"),
    )
    with engine.begin() as conn:
        tables = set(inspect(conn).get_table_names())
        if "offer_profiles" in tables:
            profile_columns = {column["name"] for column in inspect(conn).get_columns("offer_profiles")}
            if "offer_source_id" in profile_columns and "offer_id" not in profile_columns:
                renames = tuple(pair for pair in renames if pair[0] != "offer_profiles")
        # Check all collisions before changing any table.
        for old, new in renames:
            if old in tables and new in tables:
                raise RuntimeError(
                    f"Both '{old}' and '{new}' exist; migration requires manual resolution."
                )
        for table in tables:
            columns = {column["name"] for column in inspect(conn).get_columns(table)}
            if {"offer_profile_id", "offer_source_id"} <= columns:
                raise RuntimeError(
                    f"Both offer_profile_id and offer_source_id exist in '{table}'."
                )
        for old, new in renames:
            if old in tables:
                conn.execute(text(f'ALTER TABLE "{old}" RENAME TO "{new}"'))
        for table in inspect(conn).get_table_names():
            columns = {column["name"] for column in inspect(conn).get_columns(table)}
            if "offer_profile_id" in columns:
                profile_reference = any(
                    foreign_key["referred_table"] == "offer_profiles"
                    and "offer_profile_id" in foreign_key["constrained_columns"]
                    for foreign_key in inspect(conn).get_foreign_keys(table)
                )
                if profile_reference:
                    continue
                if "offer_source_id" in columns:
                    raise RuntimeError(
                        f"Both offer_profile_id and offer_source_id exist in '{table}'."
                    )
                conn.execute(text(
                    f'ALTER TABLE "{table}" RENAME COLUMN "offer_profile_id" TO "offer_source_id"'
                ))


def _remove_obsolete_offer_source_columns():
    """Remove category and value proposition from existing offer sources."""
    with engine.begin() as conn:
        if "offer_sources" not in inspect(conn).get_table_names():
            return
        columns = {column["name"] for column in inspect(conn).get_columns("offer_sources")}
        for column in ("category", "value_proposition"):
            if column in columns:
                conn.execute(text(f'ALTER TABLE "offer_sources" DROP COLUMN "{column}"'))


def _migrate_offer_facts_optional_evidence():
    """Drop source_field and allow facts without evidence, preserving existing rows."""
    from domain.models.offer.offer_fact import OfferFact

    with engine.begin() as conn:
        if "offer_facts" not in inspect(conn).get_table_names():
            return
        columns = {column["name"]: column for column in inspect(conn).get_columns("offer_facts")}
        if "source_field" not in columns and columns["evidence"]["nullable"]:
            return
        if conn.dialect.name != "sqlite":
            if "source_field" in columns:
                conn.execute(text('ALTER TABLE "offer_facts" DROP COLUMN "source_field"'))
            conn.execute(text('ALTER TABLE "offer_facts" ALTER COLUMN "evidence" DROP NOT NULL'))
            return
        if "offer_facts_migrated" in inspect(conn).get_table_names():
            raise RuntimeError("Temporary offer_facts_migrated table already exists")
        conn.execute(text("""
            CREATE TABLE offer_facts_migrated (
                id INTEGER PRIMARY KEY,
                offer_source_id INTEGER NOT NULL REFERENCES offer_sources(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                evidence TEXT,
                is_reviewed BOOLEAN NOT NULL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        fields = "id, offer_source_id, name, description, evidence, is_reviewed, created_at, updated_at"
        conn.execute(text(f"INSERT INTO offer_facts_migrated ({fields}) SELECT {fields} FROM offer_facts"))
        conn.execute(text('DROP TABLE "offer_facts"'))
        conn.execute(text('ALTER TABLE "offer_facts_migrated" RENAME TO "offer_facts"'))
        for index in OfferFact.__table__.indexes:
            index.create(conn, checkfirst=True)


def _repair_offer_profile_additional_contexts_key():
    """Restore the profile relation mistakenly renamed by the legacy migration."""
    table = "offer_profile_additional_contexts"
    with engine.begin() as conn:
        inspector = inspect(conn)
        if table not in inspector.get_table_names():
            return
        columns = {column["name"] for column in inspector.get_columns(table)}
        if "offer_profile_id" in columns or "offer_source_id" not in columns:
            return
        if not any(
            foreign_key["referred_table"] == "offer_profiles"
            and "offer_source_id" in foreign_key["constrained_columns"]
            for foreign_key in inspector.get_foreign_keys(table)
        ):
            raise RuntimeError("Unexpected additional context relation; cannot restore profile key")
        conn.execute(text(
            'ALTER TABLE "offer_profile_additional_contexts" '
            'RENAME COLUMN "offer_source_id" TO "offer_profile_id"'
        ))


def _migrate_target_audiences_to_offer_profiles():
    """Preserve source audiences while moving ownership to offer profiles."""
    from sqlalchemy import MetaData
    from domain.models.audience.target_audience import TargetAudience
    from domain.models.offer.offer_profile import OfferProfile

    with engine.begin() as conn:
        inspector = inspect(conn)
        if "target_audiences" not in inspector.get_table_names():
            return
        columns = {column["name"] for column in inspector.get_columns("target_audiences")}
        if "offer_source_id" not in columns:
            return
        if "offer_profile_id" in columns:
            raise RuntimeError("Both source and profile audience columns exist; manual resolution required")
        if conn.dialect.name != "sqlite":
            raise RuntimeError("Audience ownership migration currently supports SQLite")
        OfferProfile.__table__.create(conn, checkfirst=True)
        source_ids = conn.execute(text("SELECT DISTINCT offer_source_id FROM target_audiences WHERE offer_source_id IS NOT NULL")).scalars().all()
        mapping = {}
        for source_id in source_ids:
            profiles = conn.execute(text("SELECT id FROM offer_profiles WHERE offer_source_id = :source_id ORDER BY id"), {"source_id": source_id}).scalars().all()
            if len(profiles) == 1:
                mapping[source_id] = profiles[0]
            else:
                result = conn.execute(OfferProfile.__table__.insert().values(offer_source_id=source_id, name="Przeniesione grupy docelowe"))
                mapping[source_id] = result.inserted_primary_key[0]
        metadata = MetaData()
        for table in Base.metadata.sorted_tables:
            table.to_metadata(metadata)
        temporary = TargetAudience.__table__.to_metadata(metadata, name="target_audiences_migrated")
        temporary.indexes.clear()
        if "target_audiences_migrated" in inspect(conn).get_table_names():
            raise RuntimeError("Temporary audience migration table already exists")
        temporary.create(conn)
        common = [column.name for column in TargetAudience.__table__.columns if column.name in columns]
        expressions = [f'"{name}"' for name in common]
        common.append("offer_profile_id")
        cases = " ".join(f"WHEN {int(source_id)} THEN {int(profile_id)}" for source_id, profile_id in mapping.items())
        expressions.append(f'CASE "offer_source_id" {cases} ELSE NULL END' if cases else "NULL")
        names = ", ".join(f'"{name}"' for name in common)
        conn.execute(text(f'INSERT INTO target_audiences_migrated ({names}) SELECT {", ".join(expressions)} FROM target_audiences'))
        conn.execute(text('DROP TABLE "target_audiences"'))
        conn.execute(text('ALTER TABLE "target_audiences_migrated" RENAME TO "target_audiences"'))
        for index in TargetAudience.__table__.indexes:
            index.create(conn, checkfirst=True)


def _remove_obsolete_target_audience_columns():
    """Remove obsolete audience evaluation and marketing fields."""
    removed = {"message_angles", "marketing_channels", "score", "confidence", "awareness_level", "reason", "decision_time", "research_level", "price_sensitivity", "location", "objections", "purchasing_power"}
    with engine.begin() as conn:
        inspector = inspect(conn)
        if "target_audiences" not in inspector.get_table_names():
            return
        columns = {column["name"] for column in inspector.get_columns("target_audiences")}
        quote = conn.dialect.identifier_preparer.quote
        for index in inspector.get_indexes("target_audiences"):
            if removed.intersection(index["column_names"]):
                conn.execute(text(f'DROP INDEX {quote(index["name"])}'))
        for column in sorted(removed.intersection(columns)):
            conn.execute(text(f'ALTER TABLE "target_audiences" DROP COLUMN {quote(column)}'))


def _add_target_audience_desires():
    with engine.begin() as conn:
        inspector = inspect(conn)
        if "target_audiences" not in inspector.get_table_names():
            return
        columns = {column["name"] for column in inspector.get_columns("target_audiences")}
        if "desires" not in columns:
            conn.execute(text("ALTER TABLE target_audiences ADD COLUMN desires JSON DEFAULT '[]'"))

from sqlalchemy import inspect, text
from .db import Base, engine
from domain.models import models

def init_db():
    from .retired_ad_strategy_migration import remove_retired_ad_strategy
    remove_retired_ad_strategy(engine)
    _remove_retired_offer_elements()
    _migrate_app_ollama_settings_to_app_properties()
    _migrate_offers_to_offers_raw()
    _rename_offer_raw_details_column()
    _migrate_offer_profile_to_offer_profiles()
    _repair_offer_profile_additional_contexts_key()
    _migrate_offer_profiles_to_offer_sources()
    _remove_obsolete_offer_source_columns()
    _rename_offer_source_summary_column()
    _migrate_checklists_to_offer_sources()
    from .research_migration import migrate_research_to_offer_profiles
    migrate_research_to_offer_profiles(engine)
    _add_missing_favorite_columns()
    _add_missing_is_reviewed_columns()
    _add_missing_page_requirements_name_column()
    _rename_page_section_requirement_column()
    _migrate_offer_facts_optional_evidence()
    _migrate_target_audiences_to_offer_profiles()
    _remove_obsolete_target_audience_columns()
    _add_target_audience_desires()
    _add_marketing_angle_fields()
    _migrate_ad_concept_modes_and_angles()
    _drop_offer_profile_notes()
    _add_note_pinned_column()
    _add_chat_message_token_columns()
    from .creative_plans_migration import migrate_creative_plan_content
    migrate_creative_plan_content(engine)
    from .ugc_profile_migration import migrate_ugc_to_offer_profiles
    migrate_ugc_to_offer_profiles(engine)
    from .page_blueprints_migration import migrate_page_blueprints_to_profiles
    migrate_page_blueprints_to_profiles(engine)
    from .page_blueprint_sections_migration import migrate_page_blueprint_sections
    migrate_page_blueprint_sections(engine)
    from .retired_brand_marketing_migration import remove_retired_brand_marketing_pipeline
    remove_retired_brand_marketing_pipeline(engine)
    _add_brand_style_text_color()
    Base.metadata.create_all(bind=engine)


def _add_brand_style_text_color():
    with engine.begin() as conn:
        if "brand_styles" not in inspect(conn).get_table_names():
            return
        columns = {column["name"] for column in inspect(conn).get_columns("brand_styles")}
        if "text_color" not in columns:
            conn.execute(text(
                "ALTER TABLE brand_styles ADD COLUMN text_color VARCHAR(7) "
                "NOT NULL DEFAULT '#000000'"
            ))


def _remove_retired_offer_elements():
    """Remove storage for the retired offer elements feature, including its old name."""
    with engine.begin() as conn:
        tables = set(inspect(conn).get_table_names())
        for table in ("offer_source_elements", "offer_profile_elements"):
            if table in tables:
                conn.execute(text(f'DROP TABLE "{table}"'))


def _migrate_ad_concept_modes_and_angles():
    with engine.begin() as conn:
        if "ad_concepts" not in inspect(conn).get_table_names():
            return
        columns = {column["name"] for column in inspect(conn).get_columns("ad_concepts")}
        if "generation_mode" not in columns:
            conn.execute(text(
                "ALTER TABLE ad_concepts ADD COLUMN generation_mode VARCHAR(16) "
                "NOT NULL DEFAULT 'standard'"
            ))
        conn.execute(text(
            "CREATE TABLE IF NOT EXISTS ad_concept_marketing_angles ("
            "ad_concept_id INTEGER NOT NULL REFERENCES ad_concepts(id) ON DELETE CASCADE, "
            "marketing_angle_id INTEGER NOT NULL REFERENCES marketing_angles(id) ON DELETE CASCADE, "
            "PRIMARY KEY (ad_concept_id, marketing_angle_id))"
        ))
        if "marketing_angle_id" in columns:
            conn.execute(text(
                "INSERT INTO ad_concept_marketing_angles (ad_concept_id, marketing_angle_id) "
                "SELECT c.id, c.marketing_angle_id FROM ad_concepts AS c "
                "WHERE c.marketing_angle_id IS NOT NULL "
                "AND EXISTS (SELECT 1 FROM marketing_angles AS m WHERE m.id = c.marketing_angle_id) "
                "AND NOT EXISTS (SELECT 1 FROM ad_concept_marketing_angles AS link "
                "WHERE link.ad_concept_id = c.id AND link.marketing_angle_id = c.marketing_angle_id)"
            ))
            if conn.dialect.name == "sqlite":
                conn.execute(text("DROP INDEX IF EXISTS ix_ad_concepts_marketing_angle_id"))
            conn.execute(text("ALTER TABLE ad_concepts DROP COLUMN marketing_angle_id"))


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

    for table in ("target_audiences", "checklist_item", "analysis_questions", "ugc_creatives", "ad_copies"):
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
    if "offer_profile_id" in columns:
        return
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
        ("offer_profile_analysis", "offer_source_analysis"),
    )
    with engine.begin() as conn:
        tables = set(inspect(conn).get_table_names())
        if "offer_profiles" in tables:
            profile_columns = {column["name"] for column in inspect(conn).get_columns("offer_profiles")}
            if "offer_source_id" in profile_columns and "offer_id" not in profile_columns:
                renames = tuple(pair for pair in renames if pair[0] not in {"offer_profiles", "offer_profile_analysis"})
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


def _add_chat_message_token_columns():
    """Store exact token counts reported by the model for chat answers."""
    with engine.begin() as conn:
        if "chat_messages" not in inspect(conn).get_table_names():
            return
        columns = {column["name"] for column in inspect(conn).get_columns("chat_messages")}
        for column in ("prompt_tokens", "completion_tokens"):
            if column not in columns:
                conn.execute(text(f'ALTER TABLE "chat_messages" ADD COLUMN "{column}" INTEGER'))


def _drop_offer_profile_notes():
    """Notes are no longer linked to offer profiles; the notes themselves are kept."""
    with engine.begin() as conn:
        if "offer_profile_notes" in inspect(conn).get_table_names():
            conn.execute(text('DROP TABLE "offer_profile_notes"'))


def _add_note_pinned_column():
    with engine.begin() as conn:
        if "notes" not in inspect(conn).get_table_names():
            return
        columns = {column["name"] for column in inspect(conn).get_columns("notes")}
        if "is_pinned" not in columns:
            conn.execute(text('ALTER TABLE "notes" ADD COLUMN is_pinned BOOLEAN NOT NULL DEFAULT 0'))


def _rename_offer_source_summary_column():
    """Rename offer_summary to offer_details, preserving existing content."""
    with engine.begin() as conn:
        if "offer_sources" not in inspect(conn).get_table_names():
            return
        columns = {column["name"] for column in inspect(conn).get_columns("offer_sources")}
        if "offer_summary" not in columns:
            return
        if "offer_details" in columns:
            raise RuntimeError("Both offer_summary and offer_details exist in 'offer_sources'.")
        conn.execute(text(
            'ALTER TABLE "offer_sources" RENAME COLUMN "offer_summary" TO "offer_details"'
        ))


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

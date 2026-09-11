from sqlalchemy import inspect, text
from .db import Base, engine
from domain.models import models

def init_db():
    _migrate_offers_to_offers_raw()
    _rename_offer_raw_details_column()
    _migrate_offer_profile_to_offer_profiles()
    _migrate_checklists_to_offer_profiles()
    _add_missing_favorite_columns()
    _add_missing_is_reviewed_columns()
    _add_missing_page_blueprint_columns()
    _rename_page_section_requirement_column()
    Base.metadata.create_all(bind=engine)

def _migrate_offers_to_offers_raw():
    """Migrate the retired Offer schema before SQLAlchemy creates offers_raw.

    Offer records (and their OfferProfile references) are preserved. Offer items,
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

    for table in ("offer_profile_elements", "target_audiences", "checklist_item", "analysis_questions"):
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

def _migrate_checklists_to_offer_profiles():
    """Replace the retired analysis_checklist link with checklist.offer_profile_id."""
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    if "checklist" not in tables:
        return

    columns = {column["name"] for column in inspector.get_columns("checklist")}
    with engine.begin() as conn:
        if "offer_profile_id" not in columns:
            conn.execute(text('ALTER TABLE "checklist" ADD COLUMN offer_profile_id INTEGER'))

        if {"analysis_checklist", "offer_profile_analysis"}.issubset(tables):
            conn.execute(text("""
                UPDATE checklist
                SET offer_profile_id = (
                    SELECT offer_profile_analysis.offer_profile_id
                    FROM analysis_checklist
                    JOIN offer_profile_analysis
                      ON offer_profile_analysis.analysis_id = analysis_checklist.analysis_id
                    WHERE analysis_checklist.checklist_id = checklist.id
                    LIMIT 1
                )
                WHERE offer_profile_id IS NULL
            """))
            conn.execute(text('DROP TABLE "analysis_checklist"'))

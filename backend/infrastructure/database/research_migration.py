from sqlalchemy import MetaData, inspect, text

from domain.models.analysis.offer_profile_analysis import OfferProfileAnalysis
from domain.models.checklist.checklist import Checklist
from domain.models.checklist.checklist_item import ChecklistItem
from domain.models.offer.offer_profile import OfferProfile
from infrastructure.database.db import Base


def migrate_research_to_offer_profiles(engine):
    """Move research ownership without losing analysis answers or checklist items."""
    tables = set(inspect(engine).get_table_names())
    legacy_checklists = "checklist" in tables and "offer_source_id" in {
        column["name"] for column in inspect(engine).get_columns("checklist")
    }
    if "offer_source_analysis" not in tables and not legacy_checklists:
        return
    if engine.dialect.name != "sqlite":
        raise RuntimeError("Research ownership migration currently supports SQLite")

    # Rebuilding the checklist parent with FK enforcement enabled would cascade
    # delete its items. Disable it only on this migration connection, then check
    # all foreign keys before committing the transaction and restore the setting.
    with engine.connect() as conn:
        foreign_keys = conn.exec_driver_sql("PRAGMA foreign_keys").scalar()
        conn.commit()
        conn.exec_driver_sql("PRAGMA foreign_keys=OFF")
        conn.commit()
        try:
            conn.exec_driver_sql("BEGIN")
            OfferProfile.__table__.create(conn, checkfirst=True)
            OfferProfileAnalysis.__table__.create(conn, checkfirst=True)
            sources = set()
            if "offer_source_analysis" in tables:
                sources.update(conn.execute(text("SELECT DISTINCT offer_source_id FROM offer_source_analysis")).scalars())
            if legacy_checklists:
                sources.update(conn.execute(text("SELECT DISTINCT offer_source_id FROM checklist")).scalars())
            if None in sources:
                raise RuntimeError("Research without an offer source requires manual ownership resolution")
            mapping = {}
            for source_id in sorted(sources):
                profiles = conn.execute(text("SELECT id FROM offer_profiles WHERE offer_source_id = :id ORDER BY id"), {"id": source_id}).scalars().all()
                if len(profiles) == 1:
                    mapping[source_id] = profiles[0]
                else:
                    result = conn.execute(OfferProfile.__table__.insert().values(
                        offer_source_id=source_id, name="Przeniesiony research",
                    ))
                    mapping[source_id] = result.inserted_primary_key[0]

            if "offer_source_analysis" in tables:
                for source_id, profile_id in mapping.items():
                    conn.execute(text("""
                        INSERT OR IGNORE INTO offer_profile_analysis (offer_profile_id, analysis_id)
                        SELECT :profile_id, analysis_id FROM offer_source_analysis
                        WHERE offer_source_id = :source_id
                    """), {"profile_id": profile_id, "source_id": source_id})
                conn.execute(text("DROP TABLE offer_source_analysis"))

            if legacy_checklists:
                metadata = MetaData()
                for table in Base.metadata.sorted_tables:
                    table.to_metadata(metadata)
                temporary = Checklist.__table__.to_metadata(metadata, name="checklist_research_migrated")
                temporary.indexes.clear()
                temporary.create(conn)
                columns = {column["name"] for column in inspect(conn).get_columns("checklist")}
                common = [column.name for column in Checklist.__table__.columns if column.name in columns]
                expressions = [f'"{name}"' for name in common]
                cases = " ".join(f"WHEN {int(source)} THEN {int(profile)}" for source, profile in mapping.items())
                expressions.append(f'CASE "offer_source_id" {cases} ELSE NULL END' if cases else "NULL")
                names = ", ".join(f'"{name}"' for name in [*common, "offer_profile_id"])
                conn.execute(text(f'INSERT INTO checklist_research_migrated ({names}) SELECT {", ".join(expressions)} FROM checklist'))
                conn.execute(text("DROP TABLE checklist"))
                conn.execute(text("ALTER TABLE checklist_research_migrated RENAME TO checklist"))
                for index in Checklist.__table__.indexes:
                    index.create(conn, checkfirst=True)
                if "checklist_item" in tables:
                    item_table = ChecklistItem.__table__.to_metadata(metadata, name="checklist_item_research_migrated")
                    item_table.indexes.clear()
                    item_table.create(conn)
                    old_columns = {column["name"] for column in inspect(conn).get_columns("checklist_item")}
                    item_columns = ", ".join(f'"{column.name}"' for column in ChecklistItem.__table__.columns if column.name in old_columns)
                    conn.execute(text(f'INSERT INTO checklist_item_research_migrated ({item_columns}) SELECT {item_columns} FROM checklist_item'))
                    conn.execute(text("DROP TABLE checklist_item"))
                    conn.execute(text("ALTER TABLE checklist_item_research_migrated RENAME TO checklist_item"))
                    for index in ChecklistItem.__table__.indexes:
                        index.create(conn, checkfirst=True)
            if conn.exec_driver_sql("PRAGMA foreign_key_check").fetchall():
                raise RuntimeError("Research migration failed foreign key validation")
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.exec_driver_sql(f"PRAGMA foreign_keys={int(foreign_keys)}")
            conn.commit()

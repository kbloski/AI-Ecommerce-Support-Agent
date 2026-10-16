from sqlalchemy import MetaData, inspect, text

from domain.models.creative.ugc_creative import UgcCreative
from domain.models.offer.offer_profile import OfferProfile
from infrastructure.database.db import Base


def migrate_ugc_to_offer_profiles(engine):
    if "ugc_creatives" not in inspect(engine).get_table_names():
        return
    columns = {column["name"] for column in inspect(engine).get_columns("ugc_creatives")}
    if "message_strategy_id" not in columns:
        return
    if engine.dialect.name != "sqlite":
        raise RuntimeError("UGC ownership migration currently supports SQLite")
    with engine.connect() as conn:
        foreign_keys = conn.exec_driver_sql("PRAGMA foreign_keys").scalar()
        conn.commit()
        conn.exec_driver_sql("PRAGMA foreign_keys=OFF")
        conn.commit()
        try:
            conn.exec_driver_sql("BEGIN")
            OfferProfile.__table__.create(conn, checkfirst=True)
            rows = conn.execute(text("SELECT * FROM ugc_creatives")).mappings().all()
            mapping = {}
            owners = {}
            for row in rows:
                strategy_id = row["message_strategy_id"]
                source_id = conn.execute(text("""
                    SELECT b.offer_source_id FROM message_strategy m
                    JOIN offer_strategy o ON m.offer_strategy_id=o.id
                    JOIN marketing_strategy s ON o.marketing_strategy_id=s.id
                    JOIN brand_marketing b ON s.brand_marketing_id=b.id
                    WHERE m.id=:id
                """), {"id": strategy_id}).scalar_one_or_none()
                if source_id is None:
                    raise RuntimeError(f"Cannot resolve source for UGC {row['id']}; migration rolled back")
                if source_id not in mapping:
                    profiles = conn.execute(text("SELECT id FROM offer_profiles WHERE offer_source_id=:id ORDER BY id"), {"id": source_id}).scalars().all()
                    if len(profiles) == 1:
                        mapping[source_id] = profiles[0]
                    else:
                        result = conn.execute(OfferProfile.__table__.insert().values(offer_source_id=source_id, name="Migrated UGC"))
                        mapping[source_id] = result.inserted_primary_key[0]
                owners[row["id"]] = mapping[source_id]
            metadata = MetaData()
            for table in Base.metadata.sorted_tables:
                table.to_metadata(metadata)
            temporary = UgcCreative.__table__.to_metadata(metadata, name="ugc_creatives_profile_migrated")
            temporary.indexes.clear()
            temporary.create(conn)
            for row in rows:
                values = {column.name: row[column.name] for column in temporary.columns if column.name in row}
                values["offer_profile_id"] = owners[row["id"]]
                names = ", ".join('"' + key + '"' for key in values)
                placeholders = ", ".join(":" + key for key in values)
                conn.execute(text(f"INSERT INTO ugc_creatives_profile_migrated ({names}) VALUES ({placeholders})"), values)
            conn.execute(text("DROP TABLE ugc_creatives"))
            conn.execute(text("ALTER TABLE ugc_creatives_profile_migrated RENAME TO ugc_creatives"))
            for index in UgcCreative.__table__.indexes:
                index.create(conn, checkfirst=True)
            if conn.exec_driver_sql("PRAGMA foreign_key_check").all():
                raise RuntimeError("UGC migration failed foreign key validation")
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.exec_driver_sql(f"PRAGMA foreign_keys={int(foreign_keys)}")
            conn.commit()

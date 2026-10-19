from sqlalchemy import inspect, text


RETIRED_TABLES = (
    "page_strategy",
    "message_strategy",
    "offer_strategy",
    "marketing_strategy",
    "brand_marketing",
)


def remove_retired_brand_marketing_pipeline(engine):
    """Remove the legacy strategy chain after profile-owned UGC and pages migrate."""
    if engine.dialect.name != "sqlite":
        raise RuntimeError("Retired Brand Marketing migration currently supports SQLite")

    with engine.connect() as conn:
        foreign_keys = conn.exec_driver_sql("PRAGMA foreign_keys").scalar()
        previous_violations = set(conn.exec_driver_sql("PRAGMA foreign_key_check").all())
        conn.commit()
        conn.exec_driver_sql("PRAGMA foreign_keys=OFF")
        conn.commit()
        try:
            conn.exec_driver_sql("BEGIN IMMEDIATE")
            inspector = inspect(conn)
            tables = set(inspector.get_table_names())
            retired = tables.intersection(RETIRED_TABLES)
            for table in tables - retired:
                if any(key["referred_table"] in retired for key in inspector.get_foreign_keys(table)):
                    raise RuntimeError(f"Cannot retire strategy pipeline: {table} still references it")
            for table in RETIRED_TABLES:
                if table in retired:
                    conn.execute(text(f'DROP TABLE "{table}"'))
            if set(conn.exec_driver_sql("PRAGMA foreign_key_check").all()) - previous_violations:
                raise RuntimeError("Retired strategy migration failed foreign key validation")
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.exec_driver_sql(f"PRAGMA foreign_keys={int(foreign_keys)}")
            conn.commit()

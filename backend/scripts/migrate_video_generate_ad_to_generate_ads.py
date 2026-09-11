"""
One-off migration: renames the video_generate_ad table to
generate_ads and collapses its six JSON columns (hook_strategy,
structure, scenes, asset_requirements, production_notes, cta) into a single
content_json column. duration_seconds is dropped (it stays a generation
input only, no longer persisted). Run once against app.db.
"""

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "app.db"


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='video_generate_ad'"
    )
    old_table_exists = cur.fetchone() is not None

    old_rows = []
    if old_table_exists:
        cur.execute(
            "SELECT id, ad_setup_id, hook_strategy, structure, scenes, "
            "asset_requirements, production_notes, cta, created_at, updated_at "
            "FROM video_generate_ad"
        )
        old_rows = cur.fetchall()
        print(f"Found {len(old_rows)} existing video_generate_ad rows")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS generate_ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad_setup_id INTEGER NOT NULL REFERENCES ad_setup(id) ON DELETE CASCADE,
            content_json JSON NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    for row in old_rows:
        (id_, ad_setup_id, hook_strategy, structure, scenes,
         asset_requirements, production_notes, cta, created_at, updated_at) = row

        content_json = {
            "hook_strategy": json.loads(hook_strategy) if hook_strategy else None,
            "structure": json.loads(structure) if structure else None,
            "scenes": json.loads(scenes) if scenes else None,
            "asset_requirements": json.loads(asset_requirements) if asset_requirements else None,
            "production_notes": json.loads(production_notes) if production_notes else None,
            "cta": json.loads(cta) if cta else None,
        }

        cur.execute(
            """
            INSERT INTO generate_ads
                (id, ad_setup_id, content_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                id_,
                ad_setup_id,
                json.dumps(content_json, ensure_ascii=False),
                created_at,
                updated_at,
            ),
        )

    if old_rows:
        print(f"Inserted {len(old_rows)} generate_ads rows")

    if old_table_exists:
        cur.execute("DROP TABLE video_generate_ad")
        print("Dropped old video_generate_ad table")

    conn.commit()

    cur.execute("SELECT count(*) FROM generate_ads")
    print(f"generate_ads now has {cur.fetchone()[0]} rows")

    conn.close()


if __name__ == "__main__":
    main()

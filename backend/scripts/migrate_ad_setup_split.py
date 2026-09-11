"""
One-off migration: splits the old monolithic ad_setup table (which stored
generated video production content directly) into the new lightweight
ad_setup "recipe" table plus a new video_generate_ad table holding
the previously-generated content. Run once against app.db.
"""

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "app.db"

DEFAULT_CREATIVE_TYPE = "video"
DEFAULT_PLATFORM = "Meta Ads"
DEFAULT_FORMAT = "Vertical Video 9:16"
DEFAULT_DURATION_SECONDS = 15


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "SELECT id, creative_strategy_id, name, hook_strategy, structure, scenes, "
        "asset_requirements, production_notes, cta, created_at, updated_at FROM ad_setup"
    )
    old_rows = cur.fetchall()
    print(f"Found {len(old_rows)} existing ad_setup rows")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS video_generate_ad (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad_setup_id INTEGER NOT NULL REFERENCES ad_setup(id) ON DELETE CASCADE,
            duration_seconds INTEGER,
            hook_strategy JSON,
            structure JSON,
            scenes JSON,
            asset_requirements JSON,
            production_notes JSON,
            cta JSON,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    for row in old_rows:
        (ad_setup_id, _csi, _name, hook_strategy, structure, scenes,
         asset_requirements, production_notes, cta, created_at, updated_at) = row

        cur.execute(
            """
            INSERT INTO video_generate_ad
                (ad_setup_id, duration_seconds, hook_strategy, structure,
                 scenes, asset_requirements, production_notes, cta, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ad_setup_id,
                DEFAULT_DURATION_SECONDS,
                hook_strategy,
                structure,
                scenes,
                asset_requirements,
                production_notes,
                cta,
                created_at,
                updated_at,
            ),
        )

    print(f"Inserted {len(old_rows)} video_generate_ad rows")

    cur.execute("""
        CREATE TABLE ad_setup_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creative_strategy_id INTEGER NOT NULL REFERENCES creative_strategy(id) ON DELETE CASCADE,
            name VARCHAR,
            creative_type VARCHAR NOT NULL,
            platform VARCHAR,
            format VARCHAR,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    for row in old_rows:
        (ad_setup_id, creative_strategy_id, name, *_rest, created_at, updated_at) = row

        cur.execute(
            """
            INSERT INTO ad_setup_new
                (id, creative_strategy_id, name, creative_type, platform, format, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ad_setup_id,
                creative_strategy_id,
                name,
                DEFAULT_CREATIVE_TYPE,
                DEFAULT_PLATFORM,
                DEFAULT_FORMAT,
                created_at,
                updated_at,
            ),
        )

    cur.execute("DROP TABLE ad_setup")
    cur.execute("ALTER TABLE ad_setup_new RENAME TO ad_setup")

    conn.commit()

    cur.execute("SELECT count(*) FROM ad_setup")
    print(f"ad_setup now has {cur.fetchone()[0]} rows")
    cur.execute("SELECT count(*) FROM video_generate_ad")
    print(f"video_generate_ad now has {cur.fetchone()[0]} rows")

    conn.close()


if __name__ == "__main__":
    main()

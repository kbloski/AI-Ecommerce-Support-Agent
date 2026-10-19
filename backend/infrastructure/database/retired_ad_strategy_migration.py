from sqlalchemy import inspect, text


# Children first, including table names used by earlier versions of the branch.
RETIRED_AD_STRATEGY_TABLES = (
    "generate_ads",
    "video_generate_ad",
    "creative_execution",
    "creative_executions",
    "generate_ad_setups",
    "creative_execution_setups",
    "ad_setup",
    "ad_execution",
    "creative_strategy",
    "ad_strategy",
)


def remove_retired_ad_strategy(engine):
    """Remove the retired message-strategy advertising branch and its data."""
    with engine.begin() as conn:
        tables = set(inspect(conn).get_table_names())
        for table in RETIRED_AD_STRATEGY_TABLES:
            if table in tables:
                conn.execute(text(f'DROP TABLE "{table}"'))

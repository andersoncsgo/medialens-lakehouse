"""Compara os dois snapshots mais recentes de votos de cada filme TMDb."""

import re


def vote_changes_query(snapshots, movies):
    return f"""
        WITH ranked AS (
            SELECT
                source, tmdb_id, run_id, observed_at, vote_count,
                LEAD(run_id) OVER by_movie AS previous_run_id,
                LEAD(observed_at) OVER by_movie AS previous_observed_at,
                LEAD(vote_count) OVER by_movie AS previous_vote_count,
                ROW_NUMBER() OVER by_movie AS position
            FROM {snapshots}
            WINDOW by_movie AS (
                PARTITION BY source, tmdb_id
                ORDER BY observed_at DESC, run_id DESC
            )
        )
        SELECT
            r.source, r.tmdb_id, m.title,
            r.previous_run_id, r.run_id AS current_run_id,
            r.previous_observed_at, r.observed_at AS current_observed_at,
            r.previous_vote_count, r.vote_count AS current_vote_count,
            r.vote_count - r.previous_vote_count AS vote_count_change
        FROM ranked r
        JOIN {movies} m
          ON r.source = m.source AND r.tmdb_id = m.tmdb_id
        WHERE r.position = 1 AND r.previous_run_id IS NOT NULL
    """


def quality_query(candidate, snapshots):
    return f"""
        WITH checked AS (
            SELECT *, COUNT(*) OVER (PARTITION BY source, tmdb_id) AS key_count
            FROM {candidate}
        ), eligible AS (
            SELECT source, tmdb_id FROM {snapshots}
            GROUP BY source, tmdb_id HAVING COUNT(DISTINCT run_id) >= 2
        ), summary AS (
            SELECT
                COUNT(*) AS row_count,
                COUNT(CASE WHEN key_count > 1 THEN 1 END) AS duplicate_rows,
                COUNT(CASE WHEN
                    source IS NULL OR tmdb_id IS NULL OR tmdb_id <= 0
                    OR previous_run_id IS NULL OR current_run_id IS NULL
                    OR previous_run_id = current_run_id
                    OR previous_observed_at IS NULL OR current_observed_at IS NULL
                    OR previous_observed_at > current_observed_at
                    OR vote_count_change IS DISTINCT FROM (current_vote_count - previous_vote_count)
                    THEN 1 END) AS invalid_rows
            FROM checked
        )
        SELECT summary.*, coverage.expected_rows
        FROM summary CROSS JOIN (SELECT COUNT(*) AS expected_rows FROM eligible) AS coverage
    """


def rebuild_tmdb_vote_changes(spark, catalog, silver_schema, gold_schema):
    for name in (catalog, silver_schema, gold_schema):
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            raise ValueError(f"Identificador inválido: {name!r}")
    if silver_schema.lower() == gold_schema.lower():
        raise ValueError("Silver e Gold precisam usar schemas diferentes.")

    silver = f"`{catalog}`.`{silver_schema}`"
    gold = f"`{catalog}`.`{gold_schema}`"
    table = f"{gold}.`tmdb_vote_changes`"

    def versioned(table_name, alias):
        qualified = f"{silver}.`{table_name}`"
        version = spark.sql(f"DESCRIBE HISTORY {qualified} LIMIT 1").first()["version"]
        return f"(SELECT * FROM {qualified} VERSION AS OF {version}) AS {alias}"

    snapshots = versioned("tmdb_rating_snapshots", "snapshots")
    movies = versioned("tmdb_movies", "movies")
    candidate = "_medialens_tmdb_gold_candidate"
    spark.sql(vote_changes_query(snapshots, movies)).createOrReplaceTempView(candidate)
    try:
        metrics = spark.sql(quality_query(candidate, snapshots)).first().asDict()
        if (
            metrics["duplicate_rows"] or metrics["invalid_rows"]
            or metrics["row_count"] != metrics["expected_rows"]
        ):
            raise RuntimeError(f"Falha na qualidade da Gold: {metrics}")
        print(f"Qualidade da Gold: {metrics}")
        spark.sql(f"CREATE SCHEMA IF NOT EXISTS {gold}").collect()
        spark.sql(f"""
            CREATE OR REPLACE TABLE {table} USING DELTA AS SELECT * FROM {candidate}
        """).collect()
    finally:
        spark.catalog.dropTempView(candidate)
    return metrics["row_count"]

"""Reconstrói a Silver de filmes TMDb a partir do histórico Bronze."""

import re

from pyspark.sql import Window, functions as F

RESPONSE_SCHEMA = """
    results ARRAY<STRUCT<
        id: BIGINT, title: STRING, original_title: STRING,
        original_language: STRING, release_date: STRING,
        vote_average: DOUBLE, vote_count: BIGINT, popularity: DOUBLE,
        genre_ids: ARRAY<BIGINT>
    >>
"""


def _classify_movies(bronze):
    movies = (
        bronze.withColumn("response", F.from_json("response_json", RESPONSE_SCHEMA))
        .withColumn("movie", F.explode_outer("response.results"))
        .selectExpr(
            "source", "run_id", "page", "language",
            "try_cast(ingested_at AS TIMESTAMP) AS observed_at",
            "movie.id AS tmdb_id", "movie.title AS title",
            "movie.original_title AS original_title",
            "movie.original_language AS original_language",
            "movie.release_date AS release_date_raw",
            "try_cast(movie.release_date AS DATE) AS release_date",
            "movie.vote_average AS vote_average", "movie.vote_count AS vote_count",
            "movie.popularity AS popularity", "movie.genre_ids AS genre_ids",
        )
    )
    rules = [
        ("tmdb_id IS NULL OR tmdb_id <= 0", "ID ausente ou inválido"),
        ("title IS NULL OR trim(title) = ''", "Título ausente"),
        ("observed_at IS NULL", "Data de coleta inválida"),
        ("run_id IS NULL OR trim(run_id) = ''", "Identificador da carga ausente"),
        ("vote_count < 0", "Quantidade de votos negativa"),
        ("isnan(vote_average) OR vote_average NOT BETWEEN 0 AND 10", "Nota fora da faixa 0–10"),
        (
            "trim(release_date_raw) <> '' AND release_date IS NULL",
            "Data de lançamento malformada",
        ),
    ]
    return movies.withColumn(
        "rejection_reason",
        F.concat_ws("; ", *(F.when(F.expr(rule), F.lit(reason)) for rule, reason in rules)),
    )


def _first_per_key(df, *keys):
    window = Window.partitionBy(*keys).orderBy(
        F.col("observed_at").desc(), F.col("run_id").desc(),
        F.col("page").asc_nulls_last(), F.col("language").asc_nulls_last(),
        F.to_json(F.struct(*df.columns)).asc(),
    )
    return df.withColumn("_rank", F.row_number().over(window)).where("_rank = 1").drop("_rank")


def rebuild_tmdb_silver(spark, catalog, bronze_schema, silver_schema):
    """Materializa catálogo, observações por coleta e rejeições em Delta."""
    for name in (catalog, bronze_schema, silver_schema):
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            raise ValueError(f"Identificador inválido: {name!r}")
    if bronze_schema.lower() == silver_schema.lower():
        raise ValueError("Bronze e Silver precisam usar schemas diferentes.")

    bronze = f"`{catalog}`.`{bronze_schema}`.`tmdb_api_responses`"
    silver = f"`{catalog}`.`{silver_schema}`"
    version = spark.sql(f"DESCRIBE HISTORY {bronze} LIMIT 1").first()["version"]
    classified = _classify_movies(spark.sql(f"SELECT * FROM {bronze} VERSION AS OF {version}"))
    valid = classified.where("rejection_reason = ''")

    tables = {
        "tmdb_movies": _first_per_key(valid, "source", "tmdb_id").select(
            "source", "tmdb_id", "title", "original_title", "original_language",
            "release_date", "genre_ids", "observed_at", "run_id", "page", "language",
        ),
        "tmdb_rating_snapshots": _first_per_key(valid, "source", "tmdb_id", "run_id").select(
            "source", "tmdb_id", "observed_at", "run_id", "page", "language",
            "vote_average", "vote_count", F.lit(0).alias("scale_min"), F.lit(10).alias("scale_max"),
        ),
        "tmdb_rejects": classified.where("rejection_reason <> ''"),
    }
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {silver}")
    for name, df in tables.items():
        df.createOrReplaceTempView("_medialens_tmdb_silver_stage")
        spark.sql(f"""
            CREATE OR REPLACE TABLE {silver}.`{name}` USING DELTA
            AS SELECT * FROM _medialens_tmdb_silver_stage
        """).collect()
    return {name: spark.table(f"{silver}.`{name}`").count() for name in tables}

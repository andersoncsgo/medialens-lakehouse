"""Testes SQL do MovieLens no Databricks, somente com CTEs e dados sintéticos."""

import argparse
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "src/medialens/pipelines/movielens"
FIXTURES = ROOT / "tests/fixtures"
RELATIONS = {
    "workspace.medialens_bronze.movielens_movies_raw": "raw_movies",
    "workspace.medialens_bronze.movielens_links_raw": "raw_links",
    "workspace.medialens_bronze.movielens_ratings_raw": "raw_ratings",
    "workspace.medialens_silver.movielens_movies": "ml_movies",
    "workspace.medialens_silver.movielens_external_ids": "ml_links",
    "movielens_rating_candidates": "ml_candidates",
    "movielens_rating_events": "ml_events",
    "workspace.medialens_silver.movielens_ratings": "ml_ratings",
    "workspace.medialens_silver.movielens_rating_rejects": "ml_rejects",
    "workspace.medialens_gold.movielens_movie_ratings": "ml_gold",
    "workspace.medialens_gold.movielens_tmdb_coverage": "ml_coverage",
    "workspace.medialens_silver.tmdb_movies": "tmdb_movies",
    "workspace.medialens_silver.tmdb_rating_snapshots": "tmdb_snapshots",
}
FLOW = (
    ("ml_movies", "silver_movies"),
    ("ml_links", "silver_links"),
    ("ml_candidates", "silver_rating_candidates"),
    ("ml_events", "silver_rating_events"),
    ("ml_ratings", "silver_ratings"),
    ("ml_rejects", "silver_rating_rejects"),
    ("ml_gold", "gold_movie_ratings"),
    ("ml_coverage", "gold_tmdb_coverage"),
    ("ml_quality", "gold_quality"),
)
EXPECTED_ERROR = "MEDIALENS_TEST_INVALID_MOVIE"
EXPECTED_BALANCE_ERROR = "MEDIALENS_TEST_GOLD_BALANCE"


def source_sql(name):
    return (SQL / f"{name}.sql").read_text(encoding="utf-8")


def select_body(name):
    _, body = source_sql(name).split("AS\n", maxsplit=1)
    for relation, fixture in RELATIONS.items():
        body = re.sub(rf"(?<![\w.]){re.escape(relation)}(?![\w.])", fixture, body)
    return body.strip().removesuffix(";")


def build_queries():
    fixtures = (FIXTURES / "movielens.sql").read_text(encoding="utf-8").strip()
    checks = (FIXTURES / "movielens_checks.sql").read_text(encoding="utf-8").strip()
    ctes = [fixtures] + [f"{alias} AS (\n{select_body(name)}\n)" for alias, name in FLOW]
    validation = "WITH " + ",\n".join(ctes) + "\n" + checks
    movie_rule = re.search(
        r"CONSTRAINT valid_movie EXPECT \(([^\n]+)\)", source_sql("silver_movies")
    ).group(1)
    failure = f"""
        WITH invalid_movie AS (SELECT CAST(NULL AS BIGINT) AS movie_id, 'Filme inválido' AS title)
        SELECT assert_true({movie_rule}, '{EXPECTED_ERROR}') FROM invalid_movie
    """
    gold_rule = re.search(
        r"CONSTRAINT silver_gold_balance EXPECT \(([^\n]+)\)", source_sql("gold_quality")
    ).group(1)
    imbalance = f"""
        WITH missing_gold_event AS (SELECT 3 AS silver_events, 2 AS gold_events)
        SELECT assert_true({gold_rule}, '{EXPECTED_BALANCE_ERROR}') FROM missing_gold_event
    """
    return validation, failure, imbalance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    args = parser.parse_args()
    result = subprocess.run(
        ["databricks", "experimental", "aitools", "tools", "query", "--concurrency", "1",
         "--output", "json", "--profile", args.profile, *build_queries()],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    try:
        checks, failure, imbalance = json.loads(result.stdout)
    except (TypeError, ValueError) as error:
        raise SystemExit(f"Falha ao executar a suíte: {result.stderr or result.stdout}") from error

    if checks.get("state") != "SUCCEEDED":
        raise SystemExit(f"Consulta de testes falhou: {checks.get('error')}")
    rows = checks.get("rows") or []
    if not rows:
        raise SystemExit("A consulta de testes não devolveu verificações.")
    failed = [label for label, passed in rows if str(passed).lower() != "true"]
    if failed:
        raise SystemExit("Verificações reprovadas: " + ", ".join(failed))
    for query, marker in ((failure, EXPECTED_ERROR), (imbalance, EXPECTED_BALANCE_ERROR)):
        if query.get("state") != "FAILED" or marker not in str(query.get("error")):
            raise SystemExit(f"O erro de qualidade {marker} não foi observado: {query.get('error')}")
    for label, _ in rows:
        print(f"OK: {label}")
    print(f"OK: erro intencional de qualidade ({EXPECTED_ERROR})")
    print(f"OK: erro intencional de reconciliação ({EXPECTED_BALANCE_ERROR})")
    print(f"{len(rows) + 2} verificações passaram.")


if __name__ == "__main__":
    main()

CREATE OR REFRESH MATERIALIZED VIEW workspace.medialens_gold.movielens_quality (
    CONSTRAINT nonempty_bronze EXPECT (bronze_rows > 0) ON VIOLATION FAIL UPDATE,
    CONSTRAINT bronze_silver_balance EXPECT (bronze_rows = silver_source_rows + rejected_rows)
        ON VIOLATION FAIL UPDATE,
    CONSTRAINT silver_gold_balance EXPECT (silver_events = gold_events) ON VIOLATION FAIL UPDATE,
    CONSTRAINT coverage_grain EXPECT (coverage_rows = tmdb_films AND coverage_rows = coverage_distinct_ids)
        ON VIOLATION FAIL UPDATE
)
COMMENT 'Reconciliação da edição MovieLens e cobertura do catálogo TMDB na atualização atual.'
AS
WITH bronze AS (
    SELECT count(*) AS bronze_rows FROM workspace.medialens_bronze.movielens_ratings_raw
), silver AS (
    SELECT count(*) AS silver_events, coalesce(sum(source_row_count), 0) AS silver_source_rows
    FROM workspace.medialens_silver.movielens_ratings
), rejects AS (
    SELECT coalesce(sum(source_row_count), 0) AS rejected_rows
    FROM workspace.medialens_silver.movielens_rating_rejects
), gold AS (
    SELECT count(*) AS gold_films, coalesce(sum(rating_count), 0) AS gold_events
    FROM workspace.medialens_gold.movielens_movie_ratings
), catalog AS (
    SELECT count(*) AS tmdb_films FROM workspace.medialens_silver.tmdb_movies WHERE source = 'tmdb'
), coverage AS (
    SELECT count(*) AS coverage_rows,
           count(DISTINCT tmdb_id) AS coverage_distinct_ids,
           count_if(link_status = 'matched') AS matched_films,
           count_if(link_status = 'ambiguous') AS ambiguous_films,
           count_if(link_status = 'matched_without_ratings') AS linked_without_ratings,
           count_if(link_status = 'unmatched') AS unmatched_films
    FROM workspace.medialens_gold.movielens_tmdb_coverage
)
SELECT 'ml-latest-2023-07-20' AS dataset_version,
       bronze_rows, silver_source_rows, silver_events, rejected_rows,
       silver_source_rows - silver_events AS exact_duplicate_rows,
       gold_films, gold_events, tmdb_films, coverage_rows, coverage_distinct_ids,
       matched_films, ambiguous_films, linked_without_ratings, unmatched_films,
       round(100.0 * try_divide(matched_films, tmdb_films), 2) AS coverage_pct
FROM bronze CROSS JOIN silver CROSS JOIN rejects CROSS JOIN gold CROSS JOIN catalog CROSS JOIN coverage;

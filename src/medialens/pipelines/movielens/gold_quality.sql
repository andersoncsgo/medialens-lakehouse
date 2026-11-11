CREATE OR REFRESH MATERIALIZED VIEW workspace.medialens_gold.movielens_quality (
    CONSTRAINT nonempty_bronze EXPECT (bronze_rows > 0) ON VIOLATION FAIL UPDATE,
    CONSTRAINT bronze_silver_balance EXPECT (bronze_rows = silver_source_rows + rejected_rows)
        ON VIOLATION FAIL UPDATE,
    CONSTRAINT silver_gold_balance EXPECT (silver_events = gold_events) ON VIOLATION FAIL UPDATE,
    CONSTRAINT history_balance EXPECT (silver_events = history_events) ON VIOLATION FAIL UPDATE
)
COMMENT 'Reconciliação das avaliações MovieLens por camada e saída Gold.'
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
), history AS (
    SELECT count(*) AS history_rows, coalesce(sum(rating_count), 0) AS history_events
    FROM workspace.medialens_gold.movielens_movie_rating_history
)
SELECT 'ml-latest-2023-07-20' AS dataset_version,
       bronze_rows, silver_source_rows, silver_events, rejected_rows,
       silver_source_rows - silver_events AS exact_duplicate_rows,
       gold_films, gold_events, history_rows, history_events
FROM bronze CROSS JOIN silver CROSS JOIN rejects CROSS JOIN gold CROSS JOIN history;

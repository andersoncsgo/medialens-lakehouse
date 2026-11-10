CREATE OR REFRESH MATERIALIZED VIEW workspace.medialens_silver.movielens_rating_rejects
AS
SELECT source, dataset_version, user_id_raw, movie_id_raw, rated_epoch_raw, rating_raw,
       CAST(NULL AS DOUBLE) AS min_rating, CAST(NULL AS DOUBLE) AS max_rating,
       CAST(1 AS BIGINT) AS source_row_count, source_file, source_file_modified_at, rejection_reason
FROM movielens_rating_candidates
WHERE rejection_reason IS NOT NULL
UNION ALL
SELECT source, dataset_version, CAST(user_id AS STRING), CAST(movie_id AS STRING),
       CAST(rated_epoch AS STRING), CAST(NULL AS STRING), min_rating, max_rating,
       source_row_count, source_file, source_file_modified_at, 'conflicting_event'
FROM movielens_rating_events
WHERE min_rating <> max_rating;

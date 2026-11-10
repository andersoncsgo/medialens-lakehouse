CREATE OR REFRESH MATERIALIZED VIEW workspace.medialens_silver.movielens_ratings
AS
SELECT source, dataset_version, user_id, movie_id, rated_epoch,
       timestamp_seconds(rated_epoch) AS rated_at,
       CAST(min_rating AS DECIMAL(2, 1)) AS rating,
       CAST(0.5 AS DECIMAL(2, 1)) AS scale_min, CAST(5.0 AS DECIMAL(2, 1)) AS scale_max,
       source_row_count, source_file, source_file_modified_at
FROM movielens_rating_events
WHERE min_rating = max_rating;

CREATE TEMPORARY VIEW movielens_rating_candidates AS
WITH typed AS (
    SELECT source, dataset_version, source_file, source_file_modified_at,
           userId AS user_id_raw, movieId AS movie_id_raw,
           rating AS rating_raw, `timestamp` AS rated_epoch_raw,
           try_cast(userId AS BIGINT) AS user_id,
           try_cast(movieId AS BIGINT) AS movie_id,
           try_cast(rating AS DOUBLE) AS rating,
           try_cast(`timestamp` AS BIGINT) AS rated_epoch
    FROM workspace.medialens_bronze.movielens_ratings_raw
)
SELECT t.*,
       CASE
           WHEN t.user_id IS NULL OR t.user_id <= 0 THEN 'invalid_user_id'
           WHEN t.movie_id IS NULL OR t.movie_id <= 0 THEN 'invalid_movie_id'
           WHEN t.rating IS NULL OR t.rating NOT BETWEEN 0.5 AND 5.0
                OR t.rating * 2 <> floor(t.rating * 2) THEN 'invalid_rating'
           WHEN t.rated_epoch IS NULL OR t.rated_epoch NOT BETWEEN 0 AND 253402300799
                THEN 'invalid_timestamp'
           WHEN m.movie_id IS NULL THEN 'unknown_movie_id'
       END AS rejection_reason
FROM typed t
LEFT JOIN workspace.medialens_silver.movielens_movies m
  ON m.dataset_version = t.dataset_version AND m.movie_id = t.movie_id;

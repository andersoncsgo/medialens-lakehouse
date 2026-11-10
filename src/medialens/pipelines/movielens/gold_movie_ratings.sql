CREATE OR REFRESH MATERIALIZED VIEW workspace.medialens_gold.movielens_movie_ratings
AS
WITH metrics AS (
    SELECT dataset_version, source, movie_id, scale_min, scale_max,
           count(*) AS rating_count,
           avg(rating) AS average_rating,
           min(rated_at) AS first_rated_at,
           max(rated_at) AS last_rated_at
    FROM workspace.medialens_silver.movielens_ratings
    GROUP BY dataset_version, source, movie_id, scale_min, scale_max
)
SELECT r.*, m.title, m.genres, l.tmdb_id, l.tmdb_link_status
FROM metrics r
JOIN workspace.medialens_silver.movielens_movies m USING (dataset_version, movie_id)
JOIN workspace.medialens_silver.movielens_external_ids l USING (dataset_version, movie_id);

CREATE OR REFRESH MATERIALIZED VIEW workspace.medialens_gold.movielens_tmdb_coverage
COMMENT 'Cobertura do catálogo TMDB atual no MovieLens e métricas de cada provedor lado a lado.'
AS
WITH links AS (
    SELECT * FROM workspace.medialens_silver.movielens_external_ids
    WHERE dataset_version = 'ml-latest-2023-07-20'
),
ambiguous AS (
    SELECT DISTINCT explode(tmdb_candidate_ids) AS tmdb_id
    FROM links WHERE tmdb_link_status = 'ambiguous'
)
SELECT m.tmdb_id, m.title,
       m.source AS tmdb_source,
       t.vote_average AS tmdb_average_rating, t.vote_count AS tmdb_vote_count,
       t.scale_min AS tmdb_scale_min, t.scale_max AS tmdb_scale_max,
       t.observed_at AS tmdb_observed_at, t.run_id AS tmdb_run_id,
       'movielens' AS movielens_source, 'ml-latest-2023-07-20' AS movielens_dataset_version,
       l.movie_id AS movielens_movie_id,
       r.average_rating AS movielens_average_rating, r.rating_count AS movielens_rating_count,
       r.scale_min AS movielens_scale_min, r.scale_max AS movielens_scale_max,
       r.first_rated_at AS movielens_first_rated_at, r.last_rated_at AS movielens_last_rated_at,
       CASE WHEN r.movie_id IS NOT NULL THEN 'matched'
            WHEN l.movie_id IS NOT NULL THEN 'matched_without_ratings'
            WHEN a.tmdb_id IS NOT NULL THEN 'ambiguous'
            ELSE 'unmatched' END AS link_status
FROM workspace.medialens_silver.tmdb_movies m
LEFT JOIN workspace.medialens_silver.tmdb_rating_snapshots t
  ON t.source = m.source AND t.tmdb_id = m.tmdb_id AND t.run_id = m.run_id
LEFT JOIN links l ON l.tmdb_id = m.tmdb_id AND l.tmdb_link_status = 'matched'
LEFT JOIN ambiguous a ON a.tmdb_id = m.tmdb_id
LEFT JOIN workspace.medialens_gold.movielens_movie_ratings r
  ON r.dataset_version = l.dataset_version AND r.movie_id = l.movie_id
WHERE m.source = 'tmdb';

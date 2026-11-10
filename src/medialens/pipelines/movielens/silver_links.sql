CREATE OR REFRESH MATERIALIZED VIEW workspace.medialens_silver.movielens_external_ids
COMMENT 'Mapa de candidatos por ID externo. Somente os vínculos um a um são resolvidos.'
AS
WITH parsed AS (
    SELECT DISTINCT dataset_version, source_file, try_cast(movieId AS BIGINT) AS movie_id,
           CASE WHEN trim(imdbId) RLIKE '^[0-9]+$' THEN concat('tt', trim(imdbId)) END AS imdb_id,
           try_cast(tmdbId AS BIGINT) AS tmdb_id
    FROM workspace.medialens_bronze.movielens_links_raw
),
pairs AS (
    SELECT DISTINCT p.dataset_version, p.movie_id, p.tmdb_id
    FROM parsed p
    JOIN workspace.medialens_silver.movielens_movies m
      ON m.dataset_version = p.dataset_version AND m.movie_id = p.movie_id
    WHERE p.tmdb_id > 0
),
reverse_counts AS (
    SELECT dataset_version, tmdb_id, count(*) AS movies_per_tmdb_id
    FROM pairs GROUP BY dataset_version, tmdb_id
),
tmdb_links AS (
    SELECT p.dataset_version, p.movie_id, sort_array(collect_set(p.tmdb_id)) AS tmdb_candidate_ids,
           max(r.movies_per_tmdb_id) AS max_movies_per_tmdb_id
    FROM pairs p JOIN reverse_counts r USING (dataset_version, tmdb_id)
    GROUP BY p.dataset_version, p.movie_id
),
imdb_links AS (
    SELECT dataset_version, movie_id, sort_array(collect_set(imdb_id)) AS imdb_candidate_ids,
           sort_array(collect_set(source_file)) AS link_source_files
    FROM parsed GROUP BY dataset_version, movie_id
)
SELECT m.dataset_version, m.movie_id,
       coalesce(i.imdb_candidate_ids, CAST(array() AS ARRAY<STRING>)) AS imdb_candidate_ids,
       coalesce(t.tmdb_candidate_ids, CAST(array() AS ARRAY<BIGINT>)) AS tmdb_candidate_ids,
       CASE WHEN size(t.tmdb_candidate_ids) = 1 AND t.max_movies_per_tmdb_id = 1
            THEN get(t.tmdb_candidate_ids, 0) END AS tmdb_id,
       CASE WHEN t.tmdb_candidate_ids IS NULL THEN 'missing'
            WHEN size(t.tmdb_candidate_ids) = 1 AND t.max_movies_per_tmdb_id = 1 THEN 'matched'
            ELSE 'ambiguous' END AS tmdb_link_status,
       i.link_source_files
FROM workspace.medialens_silver.movielens_movies m
LEFT JOIN imdb_links i USING (dataset_version, movie_id)
LEFT JOIN tmdb_links t USING (dataset_version, movie_id);

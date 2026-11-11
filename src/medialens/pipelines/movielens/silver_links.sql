CREATE OR REFRESH MATERIALIZED VIEW workspace.medialens_silver.movielens_external_ids
COMMENT 'Candidatos IMDb fornecidos pelo MovieLens. Vínculos confirmados são um para um.'
AS
WITH parsed AS (
    SELECT dataset_version, source_file, try_cast(movieId AS BIGINT) AS movie_id,
           CASE WHEN trim(imdbId) RLIKE '^[0-9]+$' THEN concat('tt', trim(imdbId)) END AS imdb_id
    FROM workspace.medialens_bronze.movielens_links_raw
), pairs AS (
    SELECT DISTINCT p.dataset_version, p.movie_id, p.imdb_id
    FROM parsed p
    JOIN workspace.medialens_silver.movielens_movies m USING (dataset_version, movie_id)
    WHERE p.imdb_id IS NOT NULL
), reverse_counts AS (
    SELECT dataset_version, imdb_id, count(*) AS movies_per_id
    FROM pairs GROUP BY dataset_version, imdb_id
), candidates AS (
    SELECT dataset_version, movie_id, sort_array(collect_set(imdb_id)) AS imdb_candidate_ids,
           max(movies_per_id) AS max_movies_per_id
    FROM pairs JOIN reverse_counts USING (dataset_version, imdb_id)
    GROUP BY dataset_version, movie_id
), provenance AS (
    SELECT dataset_version, movie_id, sort_array(collect_set(source_file)) AS link_source_files
    FROM parsed GROUP BY dataset_version, movie_id
)
SELECT m.dataset_version, m.movie_id,
       coalesce(c.imdb_candidate_ids, CAST(array() AS ARRAY<STRING>)) AS imdb_candidate_ids,
       CASE WHEN size(c.imdb_candidate_ids) = 1 AND c.max_movies_per_id = 1
            THEN get(c.imdb_candidate_ids, 0) END AS imdb_id,
       CASE WHEN c.imdb_candidate_ids IS NULL THEN 'missing'
            WHEN size(c.imdb_candidate_ids) = 1 AND c.max_movies_per_id = 1 THEN 'matched'
            ELSE 'ambiguous' END AS imdb_link_status,
       p.link_source_files
FROM workspace.medialens_silver.movielens_movies m
LEFT JOIN candidates c USING (dataset_version, movie_id)
LEFT JOIN provenance p USING (dataset_version, movie_id);

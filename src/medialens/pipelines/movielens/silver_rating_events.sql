CREATE OR REFRESH PRIVATE MATERIALIZED VIEW movielens_rating_events
COMMENT 'Uma chave de evento por release, usuário, filme e segundo UTC.'
AS
SELECT source, dataset_version, user_id, movie_id, rated_epoch,
       min(rating) AS min_rating, max(rating) AS max_rating,
       count(*) AS source_row_count,
       min(source_file) AS source_file,
       max(source_file_modified_at) AS source_file_modified_at
FROM movielens_rating_candidates
WHERE rejection_reason IS NULL
GROUP BY source, dataset_version, user_id, movie_id, rated_epoch;

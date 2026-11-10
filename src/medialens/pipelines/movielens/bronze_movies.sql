CREATE OR REFRESH MATERIALIZED VIEW workspace.medialens_bronze.movielens_movies_raw
COMMENT 'MovieLens Latest Full, release de 2023-07-20. Colunas do CSV preservadas como texto.'
AS
SELECT movieId, title, genres,
       'movielens' AS source,
       'ml-latest-2023-07-20' AS dataset_version,
       _metadata.file_path AS source_file,
       _metadata.file_modification_time AS source_file_modified_at
FROM read_files(
    '/Volumes/workspace/medialens_bronze/movielens_landing/ml-latest-2023-07-20/movies.csv',
    format => 'csv',
    schema => 'movieId STRING, title STRING, genres STRING',
    header => true,
    enforceSchema => false,
    escape => '"',
    mode => 'FAILFAST'
);

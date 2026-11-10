CREATE OR REFRESH MATERIALIZED VIEW workspace.medialens_bronze.movielens_ratings_raw
COMMENT 'MovieLens Latest Full, release de 2023-07-20. Colunas do CSV preservadas como texto.'
AS
SELECT userId, movieId, rating, `timestamp`,
       'movielens' AS source,
       'ml-latest-2023-07-20' AS dataset_version,
       _metadata.file_path AS source_file,
       _metadata.file_modification_time AS source_file_modified_at
FROM read_files(
    '/Volumes/workspace/medialens_bronze/movielens_landing/ml-latest-2023-07-20/ratings.csv',
    format => 'csv',
    schema => 'userId STRING, movieId STRING, rating STRING, timestamp STRING',
    header => true,
    enforceSchema => false,
    escape => '"',
    mode => 'FAILFAST'
);

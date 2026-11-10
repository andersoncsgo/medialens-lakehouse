CREATE OR REFRESH MATERIALIZED VIEW workspace.medialens_bronze.movielens_links_raw
COMMENT 'MovieLens Latest Full, release de 2023-07-20. Colunas do CSV preservadas como texto.'
AS
SELECT movieId, imdbId, tmdbId,
       'movielens' AS source,
       'ml-latest-2023-07-20' AS dataset_version,
       _metadata.file_path AS source_file,
       _metadata.file_modification_time AS source_file_modified_at
FROM read_files(
    '/Volumes/workspace/medialens_bronze/movielens_landing/ml-latest-2023-07-20/links.csv',
    format => 'csv',
    schema => 'movieId STRING, imdbId STRING, tmdbId STRING',
    header => true,
    enforceSchema => false,
    escape => '"',
    mode => 'FAILFAST'
);

CREATE OR REFRESH MATERIALIZED VIEW workspace.medialens_silver.movielens_movies (
    CONSTRAINT valid_movie EXPECT (movie_id IS NOT NULL AND movie_id > 0 AND title IS NOT NULL)
        ON VIOLATION FAIL UPDATE,
    CONSTRAINT unique_movie EXPECT (movie_variants = 1) ON VIOLATION FAIL UPDATE
)
AS
WITH normalized AS (
    SELECT DISTINCT dataset_version, source, try_cast(movieId AS BIGINT) AS movie_id,
           nullif(trim(title), '') AS title,
           CASE WHEN genres = '(no genres listed)' THEN CAST(array() AS ARRAY<STRING>)
                ELSE split(genres, '[|]') END AS genres,
           source_file
    FROM workspace.medialens_bronze.movielens_movies_raw
)
SELECT *, count(*) OVER (PARTITION BY dataset_version, movie_id) AS movie_variants
FROM normalized;

raw_movies AS (
    SELECT *, 'movielens' AS source, 'ml-latest-2023-07-20' AS dataset_version,
           'synthetic/movies.csv' AS source_file
    FROM VALUES ('1', 'Mesmo título', 'Drama'), ('2', 'Mesmo título', 'Comedy'),
                ('3', 'Terceiro', 'Drama'), ('4', 'Quarto', '(no genres listed)'),
                ('5', 'Quinto', 'Drama'), ('6', 'Sexto', 'Drama') AS v(movieId, title, genres)
),
raw_links AS (
    SELECT *, 'ml-latest-2023-07-20' AS dataset_version, 'synthetic/links.csv' AS source_file
    FROM VALUES ('1', '0000100', '10'), ('2', '0000200', '20'), ('3', '0000300', '20'),
                ('4', NULL, NULL), ('5', NULL, '50'), ('5', NULL, '51'), ('6', NULL, '60')
    AS v(movieId, imdbId, tmdbId)
),
raw_ratings AS (
    SELECT *, 'movielens' AS source, 'ml-latest-2023-07-20' AS dataset_version,
           'synthetic/ratings.csv' AS source_file,
           TIMESTAMP '2023-07-20 00:00:00' AS source_file_modified_at
    FROM VALUES ('1', '1', '4.0', '100'), ('1', '1', '4.0', '100'), ('2', '1', '5.0', '101'),
                ('3', '1', '2.0', '102'), ('3', '1', '3.0', '102'),
                ('4', '1', '5.5', '103'), ('4', '1', '4.3', '104'), ('4', '1', 'NaN', '105'),
                ('bad', '1', '3.0', '106'), ('4', '1', '3.0', '-1'),
                ('4', '99', '3.0', '107'), ('5', '2', '0.5', '108')
    AS v(userId, movieId, rating, `timestamp`)
),
tmdb_movies AS (
    SELECT * FROM VALUES ('tmdb', 10, 'Confirmado', 'r1'), ('tmdb', 20, 'Ambíguo', 'r1'),
                         ('tmdb', 40, 'Sem vínculo', 'r1'), ('tmdb', 60, 'Sem notas', 'r1')
    AS v(source, tmdb_id, title, run_id)
),
tmdb_snapshots AS (
    SELECT * FROM VALUES ('tmdb', 10, 'r1', 8.0, 200, 0, 10, TIMESTAMP '2026-11-09 00:00:00'),
                         ('tmdb', 10, 'r0', 7.0, 100, 0, 10, TIMESTAMP '2026-11-08 00:00:00')
    AS v(source, tmdb_id, run_id, vote_average, vote_count, scale_min, scale_max, observed_at)
)

raw_movies AS (
    SELECT *, 'movielens' AS source, 'ml-latest-2023-07-20' AS dataset_version,
           'synthetic/movies.csv' AS source_file
    FROM VALUES ('1', 'Mesmo título', 'Drama'), ('2', 'Mesmo título', 'Comedy'),
                ('3', 'Terceiro', 'Drama'), ('4', 'Quarto', '(no genres listed)'),
                ('5', 'Quinto', 'Drama'), ('6', 'Sexto', 'Drama') AS v(movieId, title, genres)
),
raw_links AS (
    SELECT *, 'ml-latest-2023-07-20' AS dataset_version, 'synthetic/links.csv' AS source_file
    FROM VALUES ('1', '0000100', '10'), ('2', '0000200', '20'), ('3', '0000200', '20'),
                ('4', NULL, NULL), ('5', '0000500', '50'), ('5', '0000501', '51'), ('6', NULL, '60')
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
                ('4', '99', '3.0', '107'), ('5', '2', '0.5', '108'), ('6', '1', '3.0', '2678400')
    AS v(userId, movieId, rating, `timestamp`)
)

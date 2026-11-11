SELECT 'homonimos preservados' AS check_name,
       (SELECT count(*) FROM ml_movies WHERE title = 'Mesmo título') = 2 AS passed
UNION ALL SELECT 'IMDb com zeros preservados',
       (SELECT get(imdb_candidate_ids, 0) FROM ml_links WHERE movie_id = 1) = 'tt0000100'
UNION ALL SELECT 'vinculos ausentes e ambiguos',
       (SELECT count(*) FROM ml_links WHERE imdb_link_status = 'missing' AND imdb_id IS NULL) = 2
       AND (SELECT count(*) FROM ml_links WHERE imdb_link_status = 'ambiguous' AND imdb_id IS NULL) = 3
UNION ALL SELECT 'duplicata exata consolidada',
       (SELECT count(*) FROM ml_ratings WHERE user_id = 1 AND movie_id = 1) = 1
       AND (SELECT max(source_row_count) FROM ml_ratings WHERE user_id = 1 AND movie_id = 1) = 2
UNION ALL SELECT 'notas invalidas e NaN rejeitados',
       (SELECT count(*) FROM ml_rejects WHERE rejection_reason = 'invalid_rating') = 3
UNION ALL SELECT 'usuario, timestamp e filme desconhecido rejeitados',
       (SELECT count(DISTINCT rejection_reason) FROM ml_rejects WHERE rejection_reason IN
        ('invalid_user_id', 'invalid_timestamp', 'unknown_movie_id')) = 3
UNION ALL SELECT 'evento conflitante preserva as duas linhas de origem',
       (SELECT count(*) FROM ml_rejects WHERE rejection_reason = 'conflicting_event'
        AND source_row_count = 2 AND min_rating = 2.0 AND max_rating = 3.0) = 1
       AND (SELECT count(*) FROM ml_ratings WHERE user_id = 3) = 0
UNION ALL SELECT 'reconciliacao Bronze e Silver',
       (SELECT count(*) FROM raw_ratings) = (SELECT sum(source_row_count) FROM ml_ratings)
                                         + (SELECT sum(source_row_count) FROM ml_rejects)
UNION ALL SELECT 'media Gold usa eventos validos',
       (SELECT count(*) FROM ml_gold WHERE movie_id = 1 AND average_rating = 4.0 AND rating_count = 3) = 1
UNION ALL SELECT 'historico usa o mes UTC e pondera pelo numero de eventos',
       (SELECT count(*) FROM ml_history WHERE movie_id = 1) = 2
       AND (SELECT count(*) FROM ml_history WHERE movie_id = 1 AND rating_month = DATE '1970-01-01'
            AND monthly_average_rating = 4.5 AND cumulative_rating_count = 2) = 1
       AND (SELECT count(*) FROM ml_history WHERE movie_id = 1 AND rating_month = DATE '1970-02-01'
            AND monthly_average_rating = 3.0 AND cumulative_average_rating = 4.0
            AND cumulative_rating_count = 3 AND rating_count = 1) = 1
UNION ALL SELECT 'auditoria reconcilia as duas saidas Gold',
       (SELECT count(*) FROM ml_quality WHERE bronze_rows = 13 AND silver_source_rows = 5
        AND silver_events = 4 AND rejected_rows = 8 AND exact_duplicate_rows = 1
        AND gold_events = 4 AND gold_films = 2 AND history_events = 4 AND history_rows = 3) = 1;

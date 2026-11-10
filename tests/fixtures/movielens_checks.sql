SELECT 'homonimos preservados' AS check_name,
       (SELECT count(*) FROM ml_movies WHERE title = 'Mesmo título') = 2 AS passed
UNION ALL SELECT 'IMDb com zeros preservados',
       (SELECT get(imdb_candidate_ids, 0) FROM ml_links WHERE movie_id = 1) = 'tt0000100'
UNION ALL SELECT 'vinculos ausentes e ambiguos',
       (SELECT count(*) FROM ml_links WHERE tmdb_link_status = 'missing' AND tmdb_id IS NULL) = 1
       AND (SELECT count(*) FROM ml_links WHERE tmdb_link_status = 'ambiguous' AND tmdb_id IS NULL) = 3
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
       (SELECT count(*) FROM ml_gold WHERE movie_id = 1 AND average_rating = 4.5 AND rating_count = 2) = 1
UNION ALL SELECT 'metricas separadas e snapshot TMDB correto',
       (SELECT count(*) FROM ml_coverage WHERE link_status = 'matched' AND tmdb_id = 10
        AND movielens_rating_count = 2 AND movielens_scale_min = 0.5 AND movielens_scale_max = 5
        AND tmdb_vote_count = 200 AND tmdb_scale_min = 0 AND tmdb_scale_max = 10) = 1
UNION ALL SELECT 'cobertura sem fan-out, com status distintos',
       (SELECT count(*) FROM ml_coverage) = 4
       AND (SELECT count(DISTINCT link_status) FROM ml_coverage) = 4
       AND (SELECT count(*) FROM ml_coverage WHERE tmdb_id = 20 AND link_status = 'ambiguous'
            AND movielens_movie_id IS NULL) = 1
       AND (SELECT count(*) FROM ml_coverage WHERE tmdb_id = 40 AND link_status = 'unmatched') = 1
       AND (SELECT count(*) FROM ml_coverage WHERE tmdb_id = 60 AND link_status = 'matched_without_ratings'
            AND movielens_rating_count IS NULL) = 1
UNION ALL SELECT 'auditoria reconcilia eventos e calcula cobertura',
       (SELECT count(*) FROM ml_quality WHERE bronze_rows = 12 AND silver_source_rows = 4
        AND silver_events = 3 AND rejected_rows = 8 AND exact_duplicate_rows = 1
        AND gold_events = 3 AND gold_films = 2 AND tmdb_films = 4 AND coverage_distinct_ids = 4
        AND coverage_pct = 25.0) = 1

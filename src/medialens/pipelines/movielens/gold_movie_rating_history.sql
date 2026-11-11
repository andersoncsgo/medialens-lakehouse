CREATE OR REFRESH MATERIALIZED VIEW workspace.medialens_gold.movielens_movie_rating_history
COMMENT 'Uma linha por filme, edição e mês UTC com avaliações válidas.'
AS
WITH monthly AS (
    SELECT dataset_version, source, movie_id, scale_min, scale_max,
           trunc(date_from_unix_date(CAST(FLOOR(rated_epoch / 86400) AS INT)), 'MONTH') AS rating_month,
           count(*) AS rating_count, sum(rating) AS rating_sum
    FROM workspace.medialens_silver.movielens_ratings
    GROUP BY dataset_version, source, movie_id, scale_min, scale_max, rating_month
), cumulative AS (
    SELECT *, sum(rating_count) OVER history AS cumulative_rating_count,
           sum(rating_sum) OVER history AS cumulative_rating_sum
    FROM monthly
    WINDOW history AS (
        PARTITION BY dataset_version, source, movie_id, scale_min, scale_max
        ORDER BY rating_month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )
)
SELECT dataset_version, source, movie_id, scale_min, scale_max, rating_month, rating_count,
       try_divide(rating_sum, rating_count) AS monthly_average_rating,
       cumulative_rating_count,
       try_divide(cumulative_rating_sum, cumulative_rating_count) AS cumulative_average_rating
FROM cumulative;

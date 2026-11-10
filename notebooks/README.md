# Notebooks Databricks

- `01_bronze_tmdb_popular_movies.py` configura o lote e lê o segredo da TMDB.
- `03_silver_tmdb_movies.py` reconstrói catálogo, snapshots e rejeições.
- `04_gold_tmdb_vote_changes.py` valida e publica a métrica do painel.

As tarefas recebem o caminho do código pelo bundle. A lógica reutilizável está em `src/medialens/`.

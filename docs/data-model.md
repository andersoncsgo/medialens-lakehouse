# Modelo de dados

| Camada | Saída | Grão |
| --- | --- | --- |
| Bronze | `movielens_movies_raw`, `movielens_links_raw`, `movielens_ratings_raw` | Uma linha do CSV com edição e arquivo de origem. |
| Silver | `movielens_movies`, `movielens_external_ids` | Um filme por edição. O mapa preserva os IDs IMDb candidatos e classifica o vínculo. |
| Silver | `movielens_ratings` | Uma avaliação válida por edição, usuário, filme e segundo UTC. |
| Silver | `movielens_rating_rejects` | Uma entrada inválida ou um grupo de eventos conflitantes, com contagem de linhas de origem. |
| Gold | `movielens_movie_ratings` | Um filme por edição, fonte e escala, com nota, contagem e período observado. |
| Gold | `movielens_movie_rating_history` | Um filme por mês UTC, edição, fonte e escala, com métricas mensais e acumuladas. |
| Gold | `movielens_quality` | Uma auditoria da edição com contagens de cada camada. |

O ID MovieLens é a chave analítica. No mapa IMDb, `matched` representa correspondência um para um, `missing` representa ausência de candidato e `ambiguous` representa conflito de candidatos.

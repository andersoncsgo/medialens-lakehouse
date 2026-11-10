# Modelo de dados atual

| Tabela | Grão | Chaves e rastreabilidade |
| --- | --- | --- |
| `tmdb_api_responses` | Resposta de página por lote | `run_id, page` identificam a coleta. Guarda endpoint, idioma, estado HTTP, hora UTC, contagens e JSON. |
| `tmdb_movies` | Filme por fonte | `source, tmdb_id`. Usa a observação válida mais recente. Mantém `run_id, page` da origem. |
| `tmdb_rating_snapshots` | Avaliação de um filme por coleta | `source, tmdb_id, run_id`. Guarda `observed_at`, nota de 0 a 10, votos e escala. |
| `tmdb_rejects` | Registro rejeitado da Bronze | Mantém `run_id, page`, campos processados e `rejection_reason`. |
| `tmdb_vote_changes` | Filme por fonte com duas coletas | `source, tmdb_id`. Mantém IDs, horários e votos das duas coletas mais recentes. |

A Silver usa schema explícito. IDs inválidos, títulos vazios, horários de coleta inválidos, votos negativos, notas fora da faixa e datas de lançamento malformadas geram rejeições. Nota ou votos ausentes permanecem nulos. Filmes homônimos ficam separados pelo ID.

O [modelo MovieLens](movielens.md#camadas) preserva o `movie_id` original e usa um mapa de IDs externos com estados de correspondência. A Gold mantém métricas, escalas, contagens e datas de cada provedor em colunas separadas.

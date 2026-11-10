# MovieLens Latest Full

O pipeline em batch `movielens_lakehouse` processa a edição **2023-07-20** do MovieLens em um volume privado do Unity Catalog. A amostra local contém 86.537 filmes, 86.537 registros de vínculo e 33.832.162 avaliações. O arquivo de avaliações ocupa cerca de 934 MB. Tags e Tag Genome pertencem ao mesmo download, mas ficam fora deste fluxo.

Fonte: [GroupLens — MovieLens Latest Datasets](https://grouplens.org/datasets/movielens/latest/). Consulte a [licença da edição](https://files.grouplens.org/datasets/movielens/ml-latest-README.html) antes de redistribuir dados ou derivados. Cite Harper e Konstan (2015), [The MovieLens Datasets: History and Context](https://doi.org/10.1145/2827872). Os CSVs e IDs de usuários ficam no ambiente privado, fora do Git e do painel.

## Camadas

| Camada | Saída | Grão e regra |
| --- | --- | --- |
| Bronze | `movielens_movies_raw`, `movielens_links_raw`, `movielens_ratings_raw` | Uma linha CSV, com campos de origem como texto, edição, caminho e data de modificação do arquivo. O volume preserva os arquivos de entrada. |
| Silver | `movielens_movies`, `movielens_external_ids` | Uma linha por filme MovieLens e edição. O mapa preserva candidatos IMDb e TMDB. A ligação TMDB só é confirmada se for um para um nos dois sentidos. |
| Silver | `movielens_ratings`, `movielens_rating_rejects` | Uma avaliação válida por edição, usuário, filme e segundo UTC. Duplicatas exatas são consolidadas. Notas divergentes para a mesma chave, valores inválidos e filmes desconhecidos vão para rejeições. |
| Gold | `movielens_movie_ratings` | Média de eventos, contagem de avaliações e intervalo de datas por filme e edição. A escala MovieLens é de 0,5 a 5. |
| Gold | `movielens_tmdb_coverage` | Uma linha por filme do catálogo TMDB, inclusive sem vínculo. Notas, escalas, contagens e datas de cada fonte ficam em colunas separadas. |

`matched` indica vínculo confirmado com avaliações MovieLens. `matched_without_ratings` indica vínculo sem avaliações válidas. `ambiguous` indica que o ID aparece em candidatos conflitantes. `unmatched` indica ausência de vínculo no recorte. A cobertura mede o catálogo atual da TMDB diante de um arquivo histórico. As notas resumem populações e períodos diferentes.

## Executar

Use o perfil `medialens-dev`. O catálogo `workspace` deve conter `medialens_bronze`, `medialens_silver` e `medialens_gold`. O pipeline lê `workspace.medialens_silver.tmdb_movies` e `workspace.medialens_silver.tmdb_rating_snapshots`, geradas pelo job TMDB. A identidade do pipeline precisa de permissões sobre o volume, as entradas e os schemas de destino.

No PowerShell, na raiz do repositório, valide e revise o plano antes do deploy:

```powershell
databricks bundle validate -t dev --profile medialens-dev
databricks bundle plan -t dev --profile medialens-dev --select volumes.movielens_landing --select pipelines.movielens_lakehouse
databricks bundle deploy -t dev --profile medialens-dev --select volumes.movielens_landing --select pipelines.movielens_lakehouse
```

Após o deploy criar o volume `movielens_landing`, envie apenas os três CSVs usados pelo fluxo. Use o diretório da edição. Para uma edição diferente, revise o contrato e crie outro diretório em vez de substituir estes arquivos.

```powershell
$landing = "dbfs:/Volumes/workspace/medialens_bronze/movielens_landing/ml-latest-2023-07-20"
databricks fs mkdir $landing --profile medialens-dev
databricks fs cp .\ml-latest\movies.csv "$landing/movies.csv" --profile medialens-dev
databricks fs cp .\ml-latest\links.csv "$landing/links.csv" --profile medialens-dev
databricks fs cp .\ml-latest\ratings.csv "$landing/ratings.csv" --profile medialens-dev
databricks fs ls $landing --profile medialens-dev
databricks bundle run movielens_lakehouse -t dev --profile medialens-dev
```

A execução é manual. O mesmo conjunto de CSVs pode ser reprocessado sem acumular cópias. As materialized views podem exigir recomputação, especialmente na leitura de CSV. A edição completa pode consumir a cota serverless do Free Edition. Após atualizar a Silver TMDB, execute o pipeline MovieLens novamente para atualizar a cobertura.

## Conferir

Na execução de 9 de novembro de 2026, a Bronze registrou **33.832.162** avaliações. Todas apareceram na Silver como eventos válidos e somaram o mesmo total na Gold, distribuídas por **83.239** filmes. A reconciliação retornou zero diferença, zero cópias exatas e zero rejeições.

Entre os **86.537** filmes MovieLens, **86.337** tinham vínculo TMDB inequívoco, **126** estavam sem vínculo e **74** tinham candidatos ambíguos. No catálogo TMDB efetivamente coletado no projeto, **3 dos 33** filmes tinham correspondência com avaliações e **30** ficaram sem correspondência. São dois denominadores diferentes: a qualidade do mapa de IDs MovieLens e a cobertura da amostra TMDB.

Execute no editor SQL do Databricks. `diferenca` deve ser zero. A coluna `copias_exatas` registra linhas consolidadas em eventos válidos. As rejeições contam todas as linhas de cada evento conflitante.

```sql
WITH valid AS (
  SELECT COUNT(*) AS eventos_validos, COALESCE(SUM(source_row_count), 0) AS linhas_validas
  FROM workspace.medialens_silver.movielens_ratings
), rejected AS (
  SELECT COALESCE(SUM(source_row_count), 0) AS linhas_rejeitadas
  FROM workspace.medialens_silver.movielens_rating_rejects
), raw AS (
  SELECT COUNT(*) AS linhas_bronze FROM workspace.medialens_bronze.movielens_ratings_raw
)
SELECT linhas_bronze, eventos_validos, linhas_validas - eventos_validos AS copias_exatas,
       linhas_rejeitadas, linhas_bronze - linhas_validas - linhas_rejeitadas AS diferenca
FROM raw CROSS JOIN valid CROSS JOIN rejected;

SELECT link_status, COUNT(*) AS filmes
FROM workspace.medialens_gold.movielens_tmdb_coverage
GROUP BY link_status
ORDER BY filmes DESC;
```

Documentação: [Lakeflow e fontes batch](https://docs.databricks.com/aws/en/ldp/load) e [volumes com Databricks CLI](https://docs.databricks.com/aws/en/volumes/volume-files).

Para simular entradas inválidas sem gravar no catálogo, use a [suíte SQL de testes](../tests/README.md#movielens-no-databricks).

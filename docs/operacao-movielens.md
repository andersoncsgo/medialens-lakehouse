# Operação e painel MovieLens

O pipeline materializa `workspace.medialens_gold.movielens_quality` no fim do grafo. A auditoria tem uma linha para a edição em uso e confere quatro contratos:

1. A Bronze de avaliações contém linhas.
2. As linhas recebidas batem com a soma das linhas válidas de origem e das rejeitadas. Cópias exatas consolidadas continuam contabilizadas.
3. Os eventos válidos da Silver batem com a soma das avaliações agregadas na Gold.
4. A tabela de cobertura mantém uma linha por ID do catálogo TMDB.

Se um contrato falhar, o Lakeflow marca a atualização como falha e registra a expectativa que falhou. A auditoria depende das tabelas Gold e roda depois delas. Tabelas já atualizadas por outros fluxos podem continuar disponíveis, então confira o estado da atualização antes de usar os números no painel. A auditoria guarda o último resultado publicado. Para ver o histórico das execuções, consulte o log do Lakeflow. [Monitoramento do Lakeflow](https://docs.databricks.com/aws/en/ldp/observability)

Para verificar as tabelas já materializadas sem recarregar a edição inteira, execute somente a auditoria:

```powershell
databricks bundle run movielens_lakehouse -t dev --profile medialens-dev --refresh workspace.medialens_gold.movielens_quality
```

## Visualizações do painel

Use a consulta abaixo para cartões de volume, rejeições, cópias exatas e cobertura. `coverage_pct` usa como denominador o catálogo TMDB coletado pelo projeto.

```sql
SELECT bronze_rows, silver_events, rejected_rows, exact_duplicate_rows,
       gold_films, matched_films, tmdb_films, coverage_pct
FROM workspace.medialens_gold.movielens_quality;
```

Use esta consulta para um gráfico de barras por estado de correspondência. Inclua os filmes sem vínculo para deixar a cobertura visível.

```sql
SELECT link_status, COUNT(*) AS filmes
FROM workspace.medialens_gold.movielens_tmdb_coverage
GROUP BY link_status
ORDER BY filmes DESC;
```

## Investigar uma falha

1. Abra a atualização no Lakeflow e verifique a expectativa que falhou em `movielens_quality`.
2. Para `bronze_silver_balance`, compare o total Bronze com `SUM(source_row_count)` de `movielens_ratings` e `movielens_rating_rejects`. Agrupe as rejeições por `rejection_reason`.
3. Para `silver_gold_balance`, compare `COUNT(*)` da Silver com `SUM(rating_count)` da Gold. Compare por `dataset_version` e `movie_id` para localizar a diferença.
4. Para `coverage_grain`, compare os IDs da Silver TMDB com a tabela de cobertura e investigue chaves repetidas.
5. Corrija a causa, reexecute o pipeline e confira as métricas. Para simular erros com dados sintéticos, use a [suíte SQL](../tests/README.md#movielens-no-databricks).

## Referências de portfólio

- A rubrica do Data Engineering Zoomcamp enfatiza execução reproduzível, documentação e duas visualizações. O projeto NYC 311 mostra como ligar as etapas do pipeline ao painel e como documentar a execução por componente. [Rubrica do Zoomcamp](https://datatalksclub.github.io/docs/courses/data-engineering-zoomcamp/project/) · [Projeto NYC 311](https://github.com/mdkeys/DEZC26_Project)
- O Jaffle Shop usa dados sintéticos e descreve como testar mudanças em um ambiente separado. Aqui a suíte usa CTEs sintéticas para provar a regra sem alterar o catálogo. [Jaffle Shop](https://github.com/dbt-labs/jaffle-shop)

# Ingestão Bronze da TMDB

A tarefa `ingest_tmdb_popular_movies` consulta `GET /3/movie/popular`, em português do Brasil. O bundle configura uma página por execução. O coletor aceita de uma a cinco páginas. Consulte [fontes e condições de uso](data-sources.md) antes de ampliar a coleta.

A autenticação usa o Token de Leitura da API TMDB, obtido do segredo Databricks `medialens-api/tmdb-read-token`. O código acrescenta o prefixo `Bearer` ao cabeçalho. O token fica fora da tabela e da saída da tarefa.

## Contrato e reparo

A tabela `workspace.medialens_bronze.tmdb_api_responses` armazena uma resposta por lote e página. `response_json` preserva o JSON recebido. Os metadados incluem origem, endpoint, idioma, código HTTP, contagens, parâmetros sem segredos, ID e horário UTC.

O notebook recebe `job_<run_id>` do bundle. O coletor valida o envelope da resposta e reúne todas as páginas antes de gravar um lote com `MERGE` de inserção. Se o mesmo ID já tiver um lote confirmado, o reparo devolve o resumo desse lote com `reused_batch: true`. A saída inclui a contagem de páginas e de resultados no lote.

- **429 e falhas transitórias.** São até três tentativas por página. Se a espera pedida pelo servidor superar 60 segundos, a tarefa falha para que a execução possa ser retomada mais tarde.
- **401/403.** Confira se o Token de Leitura da API está válido no segredo do workspace.
- **JSON inválido ou fora do contrato.** A tarefa falha antes de gravar os dados da coleta.
- **Rede ou permissões.** Confira a saída de rede do workspace e as permissões do catálogo e do schema.

Execute pelo [bundle](../README.md#como-executar). As dependências seguem para Silver e Gold depois de a Bronze concluir.

## Reparar uma execução

No site do Databricks, abra **Jobs & Pipelines → medialens-tmdb-lakehouse → Runs**. Abra a execução com falha ou cancelada e clique na tarefa que falhou para ler a mensagem. Corrija a causa e publique a mudança se ela estiver no código ou na configuração. Na página da execução original, clique em **Repair run**, revise as tarefas listadas e confirme. O reparo usa a configuração atual das tarefas. [Reparar jobs no Lakeflow](https://docs.databricks.com/aws/en/jobs/repair-job-failures)

Se a Bronze já terminou com sucesso e a Silver falhou, o reparo retoma a Silver e as tarefas dependentes. Se a Bronze precisar ser reexecutada e o lote daquele job já estiver gravado, a saída registra `reused_batch: true`. Uma execução nova pelo botão **Run now** cria outro ID e coleta outro lote.

Para conferir o lote antes e depois do reparo, substitua `123456789` pelo ID da execução do job. A consulta deve devolver uma linha por página com `linhas = 1`. Em uma falha anterior à primeira gravação, o resultado inicial pode estar vazio.

```sql
SELECT run_id, page, COUNT(*) AS linhas
FROM workspace.medialens_bronze.tmdb_api_responses
WHERE run_id = 'job_123456789'
GROUP BY run_id, page
ORDER BY page;
```

Referências: [autenticação TMDB](https://developer.themoviedb.org/docs/authentication-application), [endpoint oficial](https://developer.themoviedb.org/reference/movie-popular-list), [referências de execução do Lakeflow Jobs](https://docs.databricks.com/aws/en/jobs/dynamic-value-references) e [MERGE em Delta](https://docs.databricks.com/aws/en/sql/language-manual/delta-merge-into).

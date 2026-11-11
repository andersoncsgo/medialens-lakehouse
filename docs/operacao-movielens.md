# Operar o pipeline MovieLens

Abra **Jobs & Pipelines → medialens-movielens-lakehouse** e selecione a última atualização. Confira o estado de cada fluxo e a primeira expectativa que falhou.

```sql
SELECT * FROM workspace.medialens_gold.movielens_quality;

SELECT rejection_reason, sum(source_row_count) AS linhas
FROM workspace.medialens_silver.movielens_rating_rejects
GROUP BY rejection_reason
ORDER BY linhas DESC;
```

Se a leitura falhar, confira os três arquivos no volume da edição. Se a Bronze divergir da Silver, confira a soma das linhas de origem válidas e rejeitadas, inclusive conflitos. Se a Silver divergir da Gold, compare os totais por filme com o histórico mensal e confirme que os relacionamentos preservam o grão esperado. Após corrigir a origem da falha, execute uma nova atualização pelo bundle. [Guia de carga](movielens.md)

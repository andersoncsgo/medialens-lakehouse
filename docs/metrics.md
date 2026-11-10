# Métricas do MediaLens

## Variação de votos TMDb

O job TMDb atualiza `workspace.medialens_gold.tmdb_vote_changes` após a Silver.
A tarefa valida a unicidade por fonte e ID, a cobertura de filmes elegíveis, a
ordem temporal e a diferença de votos antes de substituir a tabela Gold.
A tabela tem uma linha por fonte e ID TMDb com pelo menos duas coletas.
A métrica subtrai a contagem anterior da contagem atual nas duas últimas
observações disponíveis. A tabela mantém datas e IDs das duas coletas para
rastrear os resultados na Silver. Se uma contagem estiver ausente, a diferença
fica nula. Uma queda na contagem permanece com sinal negativo.

Como os intervalos entre coletas variam por filme, a diferença é absoluta e
deve ser lida junto das datas. Uma nova execução do job completo inclui outra
coleta e pode mudar os pares comparados.

```sql
SELECT title, previous_observed_at, current_observed_at,
       previous_vote_count, current_vote_count, vote_count_change
FROM workspace.medialens_gold.tmdb_vote_changes
ORDER BY vote_count_change DESC NULLS LAST, title;
```

Também é possível atualizar só a Gold pelo PowerShell na raiz do projeto.
Use um ambiente Python com [Databricks Connect para serverless](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/python/tutorial-serverless)
e um perfil autenticado com acesso às tabelas Silver e Gold. O script executa
no workspace selecionado pelo perfil e substitui a tabela Gold.

```powershell
$env:PROJECT_ROOT = (Get-Location).Path
$env:DATABRICKS_CONFIG_PROFILE = "medialens-dev"
python notebooks/04_gold_tmdb_vote_changes.py
```

## KPIs candidatos

- Títulos por formato, ano e categoria de origem, conforme cobertura.
- Cobertura de notas, votos e IDs externos resolvidos.
- Distribuição e evolução das notas por provedor.
- Diferença entre fontes para obras correspondidas, exibindo notas e votos de cada lado.
- Qualidade da ingestão: recebidos, aceitos, rejeitados, duplicados e atrasados.

Para visualização, escala linear 0–100: `100 * (score - min) / (max - min)`. Sempre exiba provedor e escala original. Defina eventual limite mínimo de votos após explorar os dados.

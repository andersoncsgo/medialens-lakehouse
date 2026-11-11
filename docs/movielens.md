# Carga do MovieLens

O pipeline `movielens_lakehouse` lê os três arquivos da edição de 20/07/2023. O download contém 86.537 filmes e 33.832.162 avaliações. [Download e licença](data-sources.md)

## Executar

Use o perfil `medialens-dev`. Se estiver configurando o projeto pela primeira vez, crie os schemas no editor SQL do Databricks com uma identidade autorizada no catálogo.

```sql
CREATE SCHEMA IF NOT EXISTS workspace.medialens_bronze;
CREATE SCHEMA IF NOT EXISTS workspace.medialens_silver;
CREATE SCHEMA IF NOT EXISTS workspace.medialens_gold;
```

O pipeline precisa de acesso aos CSVs do volume e permissão para materializar tabelas nos schemas de destino.

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

A edição fica em um diretório próprio para tornar o processamento reproduzível. A atualização roda sob demanda, e a leitura da edição completa usa a cota serverless do Free Edition.

## Conferir

```sql
SELECT * FROM workspace.medialens_gold.movielens_quality;

SELECT rating_month, rating_count, monthly_average_rating,
       cumulative_rating_count, cumulative_average_rating
FROM workspace.medialens_gold.movielens_movie_rating_history
WHERE dataset_version = 'ml-latest-2023-07-20' AND movie_id = 1
ORDER BY rating_month;
```

A soma das avaliações válidas deve ser a mesma na Silver e nas duas saídas Gold. O ID 1 corresponde a Toy Story nesta edição. [Modelo de dados](data-model.md) · [Testes com dados sintéticos](../tests/README.md) · [Instalar o painel](dashboard.md)

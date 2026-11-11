# Arquitetura

O bundle declara um volume privado do Unity Catalog, um pipeline Lakeflow serverless em batch e um painel AI/BI. A lógica fica em arquivos SQL em `src/medialens/pipelines/movielens/`.

A Bronze lê os CSVs como texto e registra a edição e o arquivo de origem. A Silver valida as avaliações, preserva rejeições e resolve o catálogo por ID. A Gold materializa métricas por filme e por mês e verifica que ambas as contagens reconciliam com a Silver. O painel consulta as agregações para a análise e a Silver para exibir os motivos de rejeição.

O fluxo roda sob demanda para a edição fixa. O reprocessamento lê o mesmo recorte de entrada e reconstrói os resultados. [Guia de operação](operacao-movielens.md) · [Materialized views no Lakeflow](https://docs.databricks.com/aws/en/ldp/concepts/materialized-views)

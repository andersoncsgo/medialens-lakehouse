# Recursos Databricks

O bundle gerencia um Lakeflow Job manual com a chave `tmdb_bronze_ingestion`. O job executa Bronze → Silver → Gold no serverless. A configuração mantém a chave usada pelo CLI e apresenta o nome `medialens-tmdb-lakehouse` na interface.

Consulte [como executar](../README.md#como-executar) e [como investigar uma falha](../docs/architecture.md#como-investigar).

O bundle também declara `movielens_landing`, um volume gerenciado, e `movielens_lakehouse`, um pipeline Lakeflow em batch que lê os três CSVs e integra o catálogo MovieLens à Silver da TMDB. Consulte o [guia MovieLens](../docs/movielens.md).

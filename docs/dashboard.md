# Painel AI/BI do MediaLens

A página **Catálogo e gêneros** mostra a nota e o volume lado a lado e lista os 20 filmes com as maiores médias entre os que têm pelo menos 100 avaliações. Um filme pode participar de vários gêneros. As contagens por gênero se sobrepõem.

Em **Histórico por filme**, escolha um título no filtro. O gráfico superior mostra a nota acumulada até o mês observado. O inferior mostra o número de avaliações daquele mês. A tabela permite conferir a média mensal, a acumulada e suas contagens. O título traz o ano de lançamento quando ele está no catálogo. A primeira observação é o primeiro mês com avaliação e o último mês possível é julho de 2023. Meses sem avaliações ficam sem registro.

**Qualidade das camadas** mostra a reconciliação das contagens e os motivos de rejeição. A tabela de rejeições fica vazia quando todas as linhas passam pelas regras.

O painel combina a comparação de notas por gênero com o recorte temporal por filme. As referências usam perguntas analíticas parecidas em dashboards separados por assunto. [MovieLens Pipeline Case](https://github.com/euamura/data_engineering_movielens_pipeline_case/blob/main/docs/README_EN.md) · [IMDb Analytics & Data Warehouse](https://github.com/Paramjeet-singh-neu/IMBD#dashboard-preview)

## Instalar pelo bundle

Depois de executar o pipeline MovieLens, copie o ID de um SQL warehouse com acesso às tabelas do projeto e execute na raiz do repositório:

```powershell
$warehouse = "COLE_O_ID_DO_WAREHOUSE"
databricks bundle deploy -t dev --profile medialens-dev --select dashboards.medialens_analytics --var "dashboard_warehouse_id=$warehouse"
```

O layout e as consultas estão em [medialens.lvdash.json](../dashboards/medialens.lvdash.json). Também é possível importar o arquivo pela interface e selecionar o warehouse. [Importação e exportação](https://docs.databricks.com/aws/en/dashboards/automate/import-export)

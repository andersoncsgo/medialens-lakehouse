# Testes MovieLens no Databricks

Na raiz do projeto, use Python e um perfil Databricks autenticado com acesso a um SQL warehouse.

```powershell
python tests/run_movielens_databricks.py --profile medialens-dev
```

A suíte usa o SQL da Silver e da Gold com dados sintéticos em CTEs. Verifica homônimos, IDs IMDb com zeros, vínculos ambíguos, duplicatas, rejeições, média acumulada ponderada e reconciliação das duas saídas Gold. Também simula um filme inválido e a perda de um evento entre Silver e Gold. Para verificar os arquivos e a materialização, execute o [pipeline MovieLens](../docs/movielens.md).

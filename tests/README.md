# Testes

Na raiz do projeto, use Python 3.12 no PowerShell.

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

Os testes de ingestão simulam HTTP e a interface Spark. Os testes da Gold usam as consultas SQL da aplicação com dados sintéticos em SQLite e simulam o bloqueio da gravação quando a qualidade falha. A suíte roda sem credenciais, acesso à API ou Spark local. Valide o deploy e a escrita Delta em uma execução Databricks.

## MovieLens no Databricks

Com o CLI autenticado e acesso a um SQL warehouse, execute na raiz do projeto:

```powershell
python tests/run_movielens_databricks.py --profile medialens-dev
```

A suíte executa as consultas de transformação da Silver e Gold com CTEs sintéticas. Ela verifica homônimos, vínculos ambíguos, zeros à esquerda do IMDb, duplicatas, notas inválidas, valores `NaN`, eventos conflitantes, reconciliação e separação de escalas e contagens. Uma segunda consulta aplica o predicado da expectativa `valid_movie` a um filme com ID nulo e precisa falhar com o marcador esperado. O script considera essa falha intencional um sucesso.

As consultas usam apenas dados sintéticos em memória. A suíte verifica a lógica SQL e a regra da expectativa. Para verificar a leitura dos CSVs e a materialização em Delta, execute o pipeline e as consultas do [guia MovieLens](../docs/movielens.md).

A suíte também confere a auditoria da Gold e simula a perda de uma avaliação entre Silver e Gold. O erro `MEDIALENS_TEST_GOLD_BALANCE` confirma que o predicado de reconciliação detectou a diferença.

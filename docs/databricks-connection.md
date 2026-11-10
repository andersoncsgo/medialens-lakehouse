# Conectar ao Databricks

Use o PowerShell para executar o CLI. O processamento ocorre no workspace Databricks Free Edition.

```powershell
winget install --id Databricks.DatabricksCLI --exact
databricks version
$workspaceUrl = "https://DOMINIO-DO-SEU-WORKSPACE"
databricks auth login --host $workspaceUrl --profile medialens-dev
databricks current-user me --profile medialens-dev
```

Copie a URL base do workspace a partir da barra de endereços. O login abre o navegador para concluir OAuth. Se aparecer `invalid_grant`, repita o login com o mesmo perfil.

## Segredo da TMDB

No workspace que vai executar o job, crie o escopo uma vez e guarde o **Token de Leitura da API** no segredo. O segundo comando solicita o valor no terminal de forma interativa.

```powershell
databricks secrets create-scope medialens-api --profile medialens-dev
databricks secrets put-secret medialens-api tmdb-read-token --profile medialens-dev
```

A identidade que executa o job precisa ler o segredo e escrever nos schemas do projeto. Se houver falha de rede no workspace, verifique as limitações de saída da Free Edition. Consulte o [README](../README.md#como-executar) para validar, publicar e executar o job.

Referências: [CLI](https://docs.databricks.com/aws/en/dev-tools/cli/install), [OAuth](https://docs.databricks.com/aws/en/dev-tools/cli/authentication), [segredos](https://docs.databricks.com/aws/en/security/secrets/) e [limitações do Free Edition](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations).

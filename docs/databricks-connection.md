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

[CLI](https://docs.databricks.com/aws/en/dev-tools/cli/install) · [OAuth](https://docs.databricks.com/aws/en/dev-tools/cli/authentication) · [Free Edition](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations)

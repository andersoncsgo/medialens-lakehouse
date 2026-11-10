# Databricks notebook source
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

    # O Databricks injeta estas variáveis durante a execução do notebook.
    dbutils = cast(Any, None)
    spark = cast(SparkSession, None)
else:
    try:
        dbutils
    except NameError:
        dbutils = None

if dbutils is not None:
    dbutils.widgets.text("project_root", "", "Caminho do projeto no workspace")
    dbutils.widgets.text("catalog", "workspace", "Catálogo")
    dbutils.widgets.text("silver_schema", "medialens_silver", "Schema Silver")
    dbutils.widgets.text("gold_schema", "medialens_gold", "Schema Gold")

    project_root = dbutils.widgets.get("project_root")
    catalog = dbutils.widgets.get("catalog")
    silver_schema = dbutils.widgets.get("silver_schema")
    gold_schema = dbutils.widgets.get("gold_schema")
else:
    project_root = os.environ.get("PROJECT_ROOT")
    catalog = os.environ.get("CATALOG", "workspace")
    silver_schema = os.environ.get("SILVER_SCHEMA", "medialens_silver")
    gold_schema = os.environ.get("GOLD_SCHEMA", "medialens_gold")

    if not project_root:
        raise ValueError("Informe o caminho absoluto do projeto via variável de ambiente PROJECT_ROOT.")

src = Path(project_root) / "src"
if not src.is_absolute() or not (src / "medialens").is_dir():
    raise ValueError("Informe o caminho absoluto do projeto no widget project_root.")
sys.path.insert(0, str(src))

from medialens.analytics.tmdb_gold import rebuild_tmdb_vote_changes

if dbutils is None:
    profile = os.environ.get("DATABRICKS_CONFIG_PROFILE", "").strip()
    if not profile:
        raise ValueError("Defina DATABRICKS_CONFIG_PROFILE com o perfil Databricks a usar.")

    try:
        from databricks.connect import DatabricksSession
    except ModuleNotFoundError as error:
        if error.name not in {"databricks", "databricks.connect"}:
            raise
        raise RuntimeError(
            "Instale o Databricks Connect no ambiente Python para executar pelo terminal."
        ) from error

    spark = DatabricksSession.builder.serverless().profile(profile).getOrCreate()

count = rebuild_tmdb_vote_changes(spark, catalog, silver_schema, gold_schema)
print(f"tmdb_vote_changes: {count} linhas")

# Databricks notebook source
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

    # O Databricks injeta estas variáveis durante a execução do notebook.
    dbutils = cast(Any, None)
    spark = cast(SparkSession, None)

dbutils.widgets.text("project_root", "", "Caminho do projeto no workspace")
dbutils.widgets.text("catalog", "workspace", "Catálogo")
dbutils.widgets.text("bronze_schema", "medialens_bronze", "Schema Bronze")
dbutils.widgets.text("silver_schema", "medialens_silver", "Schema Silver")

src = Path(dbutils.widgets.get("project_root")) / "src"
if not src.is_absolute() or not (src / "medialens").is_dir():
    raise ValueError("Informe o caminho absoluto do projeto no widget project_root.")
sys.path.insert(0, str(src))

from medialens.transformations.tmdb_silver import rebuild_tmdb_silver

counts = rebuild_tmdb_silver(
    spark, dbutils.widgets.get("catalog"), dbutils.widgets.get("bronze_schema"),
    dbutils.widgets.get("silver_schema"),
)
for table, count in counts.items():
    print(f"{table}: {count} linhas")

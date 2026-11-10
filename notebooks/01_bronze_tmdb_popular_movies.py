# Databricks notebook source
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast
from uuid import uuid4

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

    dbutils = cast(Any, None)
    spark = cast(SparkSession, None)

dbutils.widgets.text("project_root", "", "Caminho do projeto no workspace")
dbutils.widgets.text("catalog", "workspace", "Catálogo")
dbutils.widgets.text("schema", "medialens_bronze", "Schema Bronze")
dbutils.widgets.text("language", "pt-BR", "Idioma do catálogo")
dbutils.widgets.text("max_pages", "1", "Máximo de páginas (1 a 5)")
dbutils.widgets.text("run_id", "", "Identificador da execução")

src = Path(dbutils.widgets.get("project_root")) / "src"
if not src.is_absolute() or not (src / "medialens").is_dir():
    raise ValueError("Informe o caminho absoluto do projeto no widget project_root.")
sys.path.insert(0, str(src))

from medialens.ingestion.tmdb import ingest_popular_movies

summary = ingest_popular_movies(
    spark,
    catalog=dbutils.widgets.get("catalog").strip(),
    schema=dbutils.widgets.get("schema").strip(),
    token=dbutils.secrets.get(scope="medialens-api", key="tmdb-read-token"),
    language=dbutils.widgets.get("language").strip(),
    max_pages=int(dbutils.widgets.get("max_pages")),
    run_id=dbutils.widgets.get("run_id").strip() or str(uuid4()),
)
output = json.dumps(summary, ensure_ascii=False)
print(output)
dbutils.notebook.exit(output)

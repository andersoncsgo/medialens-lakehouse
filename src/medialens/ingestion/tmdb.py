"""Coleta paginada da TMDb e persistência de lotes Bronze."""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

ENDPOINT = "/3/movie/popular"
BASE_URL = "https://api.themoviedb.org"
RETRYABLE_STATUS = {429, 500, 502, 503, 504}

BRONZE_SCHEMA = """
    source STRING NOT NULL, endpoint STRING NOT NULL, entity_type STRING NOT NULL,
    page INT NOT NULL, language STRING NOT NULL, http_status INT NOT NULL,
    results_count INT NOT NULL, total_results INT NOT NULL, total_pages INT NOT NULL,
    run_id STRING NOT NULL, ingested_at STRING NOT NULL, request_params_json STRING NOT NULL,
    response_json STRING NOT NULL
"""


def _retry_delay(header, attempt):
    if header:
        try:
            seconds = int(header)
        except ValueError:
            try:
                retry_at = parsedate_to_datetime(header)
                seconds = (retry_at - datetime.now(timezone.utc)).total_seconds()
            except (TypeError, ValueError, OverflowError):
                seconds = 2 ** attempt
        return max(1, seconds)
    return 2 ** attempt


def _get_page(token, params):
    request = urllib.request.Request(
        f"{BASE_URL}{ENDPOINT}?{urllib.parse.urlencode(params)}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read().decode("utf-8")
                return response.status, raw
        except urllib.error.HTTPError as error:
            status = error.code
            retry_after = error.headers.get("Retry-After")
            error.close()
            if status not in RETRYABLE_STATUS or attempt == 2:
                raise RuntimeError(f"TMDb retornou HTTP {status} na página {params['page']}.") from None
            delay = _retry_delay(retry_after, attempt)
            if delay > 60:
                raise RuntimeError(f"TMDb retornou HTTP {status} e pede uma pausa de {delay:.0f}s.") from None
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise RuntimeError(f"Falha de conexão com a TMDb na página {params['page']}.") from None
            delay = _retry_delay(None, attempt)
        time.sleep(delay)


def fetch_popular_movies(token, language, max_pages, run_id):
    """Retorna o lote completo em memória antes de qualquer gravação de dados."""
    token = token.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    if not token:
        raise ValueError("O segredo tmdb-read-token está vazio.")
    if not language.strip() or not 1 <= max_pages <= 5:
        raise ValueError("Informe um idioma e max_pages entre 1 e 5.")

    ingested_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []
    for page in range(1, max_pages + 1):
        params = {"language": language, "page": page}
        status, raw = _get_page(token, params)
        try:
            body = json.loads(raw)
        except ValueError:
            raise RuntimeError(f"Resposta da TMDb não é JSON válido na página {page}.") from None
        if (
            not isinstance(body, dict) or body.get("page") != page
            or not isinstance(body.get("results"), list)
            or any(type(body.get(key)) is not int or body[key] < 0
                   for key in ("total_pages", "total_results"))
        ):
            raise RuntimeError(f"Resposta da TMDb fora do contrato na página {page}.")

        rows.append({
            "source": "tmdb", "endpoint": ENDPOINT, "entity_type": "movie",
            "page": page, "language": language, "http_status": status,
            "results_count": len(body["results"]), "total_results": body["total_results"],
            "total_pages": body["total_pages"], "run_id": run_id, "ingested_at": ingested_at,
            "request_params_json": json.dumps(params, ensure_ascii=False, sort_keys=True),
            "response_json": raw,
        })
        if page >= body["total_pages"]:
            break
    return rows


def ingest_popular_movies(spark, catalog, schema, token, language, max_pages, run_id):
    """Reutiliza um lote confirmado ao reparar a mesma execução do job."""
    for name in (catalog, schema):
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            raise ValueError(f"Identificador inválido: {name!r}")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", run_id):
        raise ValueError("Identificador de execução inválido.")

    namespace = f"`{catalog}`.`{schema}`"
    table = f"{namespace}.`tmdb_api_responses`"
    if spark.catalog.tableExists(table):
        existing = (
            spark.table(table).where(f"run_id = '{run_id}'")
            .select("page", "results_count", "ingested_at").orderBy("page").collect()
        )
    else:
        existing = []

    if existing:
        rows = existing
    else:
        rows = fetch_popular_movies(token, language, max_pages, run_id)
        spark.sql(f"CREATE SCHEMA IF NOT EXISTS {namespace}").collect()
        spark.sql(f"CREATE TABLE IF NOT EXISTS {table} ({BRONZE_SCHEMA}) USING DELTA").collect()
        stage = "_medialens_tmdb_bronze_batch"
        spark.createDataFrame(rows, schema=BRONZE_SCHEMA).createOrReplaceTempView(stage)
        try:
            spark.sql(f"""
                MERGE INTO {table} AS bronze
                USING {stage} AS batch
                  ON bronze.run_id = batch.run_id AND bronze.page = batch.page
                WHEN NOT MATCHED THEN INSERT *
            """).collect()
        finally:
            spark.catalog.dropTempView(stage)

    return {
        "table": f"{catalog}.{schema}.tmdb_api_responses", "run_id": run_id,
        "pages_saved": len(rows), "results_in_last_page": rows[-1]["results_count"],
        "total_results_in_batch": sum(row["results_count"] for row in rows),
        "ingested_at": rows[0]["ingested_at"], "reused_batch": bool(existing),
    }

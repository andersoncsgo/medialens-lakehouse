import io
import json
import unittest
from urllib.error import HTTPError
from unittest.mock import MagicMock, patch

from medialens.ingestion.tmdb import ENDPOINT, fetch_popular_movies, ingest_popular_movies


def page_body(page, total_pages=2):
    return json.dumps({"page": page, "results": [{"id": page}],
                       "total_pages": total_pages, "total_results": total_pages})


class TmdbIngestionTests(unittest.TestCase):
    def test_retains_raw_json_and_stops_on_last_page(self):
        with patch("medialens.ingestion.tmdb._get_page",
                   side_effect=[(200, page_body(1)), (200, page_body(2))]) as get:
            rows = fetch_popular_movies("Bearer ficticio", "pt-BR", 5, "job_42")
        self.assertEqual(get.call_count, 2)
        self.assertEqual([row["page"] for row in rows], [1, 2])
        self.assertEqual({row["run_id"] for row in rows}, {"job_42"})
        self.assertEqual(len({row["ingested_at"] for row in rows}), 1)
        self.assertEqual(rows[0]["endpoint"], ENDPOINT)
        self.assertEqual(rows[0]["response_json"], page_body(1))

    def test_retries_429_with_retry_after(self):
        error = HTTPError("https://example.invalid", 429, "Limitado",
                          {"Retry-After": "3"}, io.BytesIO())
        response = MagicMock(status=200)
        response.__enter__.return_value = response
        response.read.return_value = page_body(1, 1).encode()
        with patch("urllib.request.urlopen", side_effect=[error, response]) as request:
            with patch("time.sleep") as sleep:
                rows = fetch_popular_movies("ficticio", "pt-BR", 1, "job_42")
        sleep.assert_called_once_with(3)
        self.assertEqual(request.call_count, 2)
        self.assertEqual(rows[0]["http_status"], 200)

    def test_401_fails_without_retry_or_payload(self):
        error = HTTPError("https://example.invalid", 401, "Negado", {}, io.BytesIO(b"segredo"))
        with patch("urllib.request.urlopen", side_effect=error) as request:
            with self.assertRaisesRegex(RuntimeError, r"^TMDb retornou HTTP 401 na página 1\.$"):
                fetch_popular_movies("ficticio", "pt-BR", 1, "job_42")
        request.assert_called_once()

    def test_rejects_successful_http_with_invalid_contract(self):
        with patch("medialens.ingestion.tmdb._get_page", return_value=(200, '{"results":{}}')):
            with self.assertRaisesRegex(RuntimeError, "fora do contrato"):
                fetch_popular_movies("ficticio", "pt-BR", 1, "job_42")

    def test_repair_uses_committed_batch_without_http_or_write(self):
        spark = MagicMock()
        spark.catalog.tableExists.return_value = True
        spark.table.return_value.where.return_value.select.return_value.orderBy.return_value.collect.return_value = [
            {"page": 1, "results_count": 20, "ingested_at": "2026-11-09T01:00:00+00:00"},
        ]
        with patch("medialens.ingestion.tmdb.fetch_popular_movies") as fetch:
            summary = ingest_popular_movies(spark, "workspace", "bronze", "ficticio", "pt-BR", 1, "job_42")
        fetch.assert_not_called()
        spark.sql.assert_not_called()
        self.assertTrue(summary["reused_batch"])
        self.assertEqual(summary["total_results_in_batch"], 20)

    def test_failed_second_page_does_not_write_first_page(self):
        spark = MagicMock()
        spark.catalog.tableExists.return_value = False
        with patch("medialens.ingestion.tmdb._get_page",
                   side_effect=[(200, page_body(1)), RuntimeError("Falha na segunda página")]):
            with self.assertRaisesRegex(RuntimeError, "segunda página"):
                ingest_popular_movies(spark, "workspace", "bronze", "ficticio", "pt-BR", 2, "job_42")
        spark.sql.assert_not_called()
        spark.createDataFrame.assert_not_called()

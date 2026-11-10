import sqlite3
import unittest
from unittest.mock import MagicMock

from medialens.analytics.tmdb_gold import quality_query, rebuild_tmdb_vote_changes, vote_changes_query


class TmdbGoldQueryTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.addCleanup(self.db.close)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE snapshots (source, tmdb_id, run_id, observed_at, vote_count);
            CREATE TABLE movies (source, tmdb_id, title);
            INSERT INTO movies VALUES ('tmdb', 1, 'Mesmo título'), ('tmdb', 2, 'Mesmo título'),
                ('tmdb', 3, 'Outro título'), ('tmdb', 4, 'Filme com menos votos');
            INSERT INTO snapshots VALUES
                ('tmdb', 1, 'a', '2026-01-01', 1), ('tmdb', 1, 'b', '2026-01-02', 7),
                ('tmdb', 1, 'c', '2026-01-03', 10), ('tmdb', 2, 'a', '2026-01-01', 5),
                ('tmdb', 3, 'a', '2026-01-01', NULL), ('tmdb', 3, 'b', '2026-01-02', 4),
                ('tmdb', 4, 'a', '2026-01-01', 12), ('tmdb', 4, 'b', '2026-01-02', 9);
        """)
        self.db.execute("CREATE TABLE candidate AS " + vote_changes_query("snapshots", "movies"))

    def test_compares_latest_two_preserving_nulls_and_negative_changes(self):
        rows = list(self.db.execute("SELECT * FROM candidate ORDER BY tmdb_id"))
        self.assertEqual([row["tmdb_id"] for row in rows], [1, 3, 4])
        self.assertEqual([row["vote_count_change"] for row in rows], [3, None, -3])
        self.assertEqual((rows[0]["previous_run_id"], rows[0]["current_run_id"]), ("b", "c"))
        metrics = self.db.execute(quality_query("candidate", "snapshots")).fetchone()
        self.assertEqual(tuple(metrics), (3, 0, 0, 3))

    def test_flags_duplicate_keys_and_incorrect_calculation(self):
        self.db.execute("INSERT INTO candidate SELECT * FROM candidate WHERE tmdb_id = 1")
        self.db.execute("UPDATE candidate SET vote_count_change = 0 WHERE tmdb_id = 3")
        metrics = self.db.execute(quality_query("candidate", "snapshots")).fetchone()
        self.assertEqual(tuple(metrics), (4, 2, 1, 3))

    def test_reports_missing_eligible_movie(self):
        self.db.execute("DELETE FROM candidate WHERE tmdb_id = 1")
        metrics = self.db.execute(quality_query("candidate", "snapshots")).fetchone()
        self.assertEqual(tuple(metrics), (2, 0, 0, 3))

    def test_failing_quality_keeps_existing_gold(self):
        spark = MagicMock()
        spark.sql.return_value.first.return_value = MagicMock()
        spark.sql.return_value.first.return_value.__getitem__.return_value = 1
        spark.sql.return_value.first.return_value.asDict.return_value = {
            "row_count": 4, "duplicate_rows": 2, "invalid_rows": 0, "expected_rows": 3,
        }
        with self.assertRaisesRegex(RuntimeError, "Falha na qualidade da Gold"):
            rebuild_tmdb_vote_changes(spark, "workspace", "silver", "gold")
        self.assertFalse(any("CREATE OR REPLACE TABLE" in call.args[0] for call in spark.sql.call_args_list))
        spark.catalog.dropTempView.assert_called_once_with("_medialens_tmdb_gold_candidate")

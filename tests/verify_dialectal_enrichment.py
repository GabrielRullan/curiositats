#!/usr/bin/env python3
"""Automated verification script for dialectal enrichment in 'curiositats.db'.

Feature 10 & Follow-up Acceptance Criteria:
1. Complete ingestion of DIEC2 Balearic corpus (91 entries).
2. Complete ingestion of Viccionari Balearic corpus (944 entries).
3. NOT NULL and non-empty constraints on all mandatory fields in 'words'.
4. Absolute absence of duplicate terms (case-insensitive).
5. Minimum total count thresholds across all tables (words >= 1000, total >= 1050).
6. Unicode encoding integrity (zero mojibake / \\ufffd).
7. SQLite integrity check (PRAGMA integrity_check).

Usage:
    python tests/verify_dialectal_enrichment.py
    python -m unittest tests/verify_dialectal_enrichment.py
"""

import json
from pathlib import Path
import re
import sqlite3
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "curiositats.db"
DIEC_JSON_PATH = PROJECT_ROOT / "database" / "diec_balear_entries.json"
VICC_JSON_PATH = PROJECT_ROOT / "database" / "viccionari_balear_entries.json"
SEED_JSON_PATH = PROJECT_ROOT / "database" / "seed_data.json"


def clean_diec_term(raw_term: str) -> str:
    """Strip homograph trailing numbers and capitalize first letter."""
    cleaned = re.sub(r"\d+$", "", raw_term).strip()
    return cleaned[0].upper() + cleaned[1:] if cleaned else cleaned


class TestDialectalEnrichment(unittest.TestCase):
    """Test suite validating dialectal enrichment and database integrity."""

    @classmethod
    def setUpClass(cls):
        if not DB_PATH.exists():
            raise unittest.SkipTest(f"Database not found at {DB_PATH}")
        cls.conn = sqlite3.connect(DB_PATH)
        cls.conn.row_factory = sqlite3.Row

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "conn") and cls.conn:
            cls.conn.close()

    def test_pragma_integrity_check(self):
        """PRAGMA integrity_check must return 'ok'."""
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "ok")

    def test_r3_diec_corpus_completeness(self):
        """Verify that all 91 DIEC2 Balearic entries are present in curiositats.db."""
        self.assertTrue(DIEC_JSON_PATH.exists(), f"Missing {DIEC_JSON_PATH}")
        with open(DIEC_JSON_PATH, "r", encoding="utf-8") as f:
            diec_entries = json.load(f)

        self.assertEqual(len(diec_entries), 91, f"Expected 91 DIEC2 entries, got {len(diec_entries)}")

        cursor = self.conn.cursor()
        missing = []
        for item in diec_entries:
            raw = item.get("term", "")
            cleaned = clean_diec_term(raw)
            cursor.execute(
                "SELECT id, term, definition, grammatical_category, dialectal_notes, source_reference "
                "FROM words WHERE LOWER(TRIM(term)) = LOWER(TRIM(?))",
                (cleaned,)
            )
            row = cursor.fetchone()
            if not row:
                missing.append(cleaned)
            else:
                self.assertTrue(bool(row["definition"]), f"Empty definition for DIEC term '{cleaned}'")
                self.assertTrue(bool(row["grammatical_category"]), f"Empty category for DIEC term '{cleaned}'")

        self.assertEqual(len(missing), 0, f"DIEC2 terms missing in database: {missing}")

    def test_r2_viccionari_corpus_completeness(self):
        """Verify that Viccionari corpus entries are present in curiositats.db."""
        self.assertTrue(VICC_JSON_PATH.exists(), f"Missing {VICC_JSON_PATH}")
        with open(VICC_JSON_PATH, "r", encoding="utf-8") as f:
            vicc_entries = json.load(f)

        self.assertGreaterEqual(len(vicc_entries), 940, f"Expected >= 940 Viccionari entries, got {len(vicc_entries)}")

        cursor = self.conn.cursor()
        missing = []
        matched_count = 0
        for item in vicc_entries:
            term = (item.get("term") or "").strip()
            if not term:
                continue
            cursor.execute(
                "SELECT id, definition, grammatical_category "
                "FROM words WHERE LOWER(TRIM(term)) = LOWER(TRIM(?))",
                (term,)
            )
            row = cursor.fetchone()
            if not row:
                missing.append(term)
            else:
                matched_count += 1
                self.assertTrue(bool(row["definition"]), f"Empty definition for Viccionari term '{term}'")

        self.assertEqual(len(missing), 0, f"Viccionari terms missing in database: {missing[:10]}...")
        self.assertGreaterEqual(matched_count, 940, f"Expected >= 940 matched Viccionari terms, got {matched_count}")

    def test_mandatory_fields_not_null_or_empty(self):
        """Verify that mandatory fields in 'words' are strictly NOT NULL and non-empty."""
        cursor = self.conn.cursor()
        checks = [
            ("term", "term IS NULL OR TRIM(term) = ''"),
            ("definition", "definition IS NULL OR TRIM(definition) = ''"),
            ("grammatical_category", "grammatical_category IS NULL OR TRIM(grammatical_category) = ''"),
            ("source_reference", "source_reference IS NULL OR TRIM(source_reference) = ''"),
            ("id", "id IS NULL OR id <= 0"),
        ]
        for field, condition in checks:
            with self.subTest(field=field):
                cursor.execute(f"SELECT COUNT(*) FROM words WHERE {condition}")
                count = cursor.fetchone()[0]
                self.assertEqual(count, 0, f"Found {count} rows in 'words' with invalid {field} ({condition})")

    def test_no_duplicate_terms(self):
        """Verify that there are zero duplicate terms in 'words' (case-insensitive)."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT LOWER(TRIM(term)), COUNT(*) "
            "FROM words "
            "GROUP BY LOWER(TRIM(term)) "
            "HAVING COUNT(*) > 1"
        )
        dups = cursor.fetchall()
        self.assertEqual(len(dups), 0, f"Found duplicate terms in 'words': {dups}")

    def test_total_count_thresholds(self):
        """Verify total count thresholds reflecting full dialectal enrichment."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM words")
        words_count = cursor.fetchone()[0]
        self.assertGreaterEqual(words_count, 1000, f"Expected >= 1000 words, got {words_count}")

        cursor.execute("SELECT COUNT(*) FROM fauna")
        fauna_count = cursor.fetchone()[0]
        self.assertGreaterEqual(fauna_count, 7, f"Expected >= 7 fauna, got {fauna_count}")

        cursor.execute("SELECT COUNT(*) FROM flora")
        flora_count = cursor.fetchone()[0]
        self.assertGreaterEqual(flora_count, 5, f"Expected >= 5 flora, got {flora_count}")

        cursor.execute("SELECT COUNT(*) FROM emblematic_businesses")
        biz_count = cursor.fetchone()[0]
        self.assertGreaterEqual(biz_count, 5, f"Expected >= 5 businesses, got {biz_count}")

        cursor.execute("SELECT COUNT(*) FROM historical_events")
        events_count = cursor.fetchone()[0]
        self.assertGreaterEqual(events_count, 6, f"Expected >= 6 events, got {events_count}")

        total_items = words_count + fauna_count + flora_count + biz_count + events_count
        self.assertGreaterEqual(total_items, 1050, f"Expected >= 1050 total curiositats, got {total_items}")

    def test_unicode_and_mojibake_absence(self):
        """Verify that no text column contains Unicode replacement character \\ufffd."""
        cursor = self.conn.cursor()
        tables = ["words", "fauna", "flora", "emblematic_businesses", "historical_events"]
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [row["name"] for row in cursor.fetchall() if "TEXT" in row["type"].upper() or "CHAR" in row["type"].upper()]
            for col in columns:
                with self.subTest(table=table, col=col):
                    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} LIKE '%\ufffd%'")
                    corrupted = cursor.fetchone()[0]
                    self.assertEqual(corrupted, 0, f"Corrupted character \\ufffd found in {table}.{col}")

    def test_dialectal_notes_present(self):
        """Verify that enriched words have appropriate dialectal notes or sources."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM words "
            "WHERE (dialectal_notes IS NOT NULL AND TRIM(dialectal_notes) != '') "
            "   OR source_reference LIKE '%DIEC2%' "
            "   OR source_reference LIKE '%Viccionari%'"
        )
        dialectal_count = cursor.fetchone()[0]
        self.assertGreaterEqual(dialectal_count, 1000, f"Expected >= 1000 dialectal records, got {dialectal_count}")


if __name__ == "__main__":
    unittest.main()

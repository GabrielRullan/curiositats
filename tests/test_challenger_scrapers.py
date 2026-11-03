#!/usr/bin/env python3
"""
Empirical verification and adversarial stress-test script by Challenger 2.
Tests DCVB crawler, Viccionari extraction, schemas, rate-limiting, caching,
and database resilience.
"""

import json
import os
from pathlib import Path
import random
import re
import sqlite3
import subprocess
import sys
import unittest
import urllib.parse
import xml.etree.ElementTree as ET

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DCVB_CRAWLER_SCRIPT = PROJECT_ROOT / "scripts" / "scrapers" / "dcvb_crawler.py"
VICCIONARI_SCRAPER_SCRIPT = PROJECT_ROOT / "scripts" / "scrapers" / "viccionari_balear_scraper.py"
VICCIONARI_JSON = PROJECT_ROOT / "database" / "viccionari_balear_entries.json"
DCVB_JSON = PROJECT_ROOT / "database" / "dcvb_extracted_entries.json"
DCVB_CACHE_DIR = PROJECT_ROOT / "database" / "dcvb_cache"
DB_PATH = PROJECT_ROOT / "curiositats.db"


class TestChallengerScrapers(unittest.TestCase):
    """Adversarial and empirical test suite for scrapers, crawlers, and datasets."""

    def test_01_crawler_cli_help(self):
        """Verify that dcvb_crawler.py --help exits with 0 and documents all arguments."""
        res = subprocess.run(
            [sys.executable, str(DCVB_CRAWLER_SCRIPT), "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(res.returncode, 0, f"--help failed: {res.stderr}")
        self.assertIn("--limit", res.stdout)
        self.assertIn("--term", res.stdout)
        self.assertIn("--delay", res.stdout)
        self.assertIn("--cache-dir", res.stdout)
        self.assertIn("--output", res.stdout)
        self.assertIn("--import-to-db", res.stdout)

    def test_02_crawler_cli_term_burballa(self):
        """Verify running with --term burballa extracts valid record and schema."""
        res = subprocess.run(
            [sys.executable, str(DCVB_CRAWLER_SCRIPT), "--term", "burballa"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(res.returncode, 0, f"--term burballa failed: {res.stderr}")
        stdout = res.stdout
        self.assertIn("Burballa", stdout)

        # Parse JSON block from output
        json_match = re.search(r"(\{\s*\"id\":\s*\"DCVBE[^\}]+\})", stdout, re.DOTALL)
        self.assertIsNotNone(json_match, f"Could not find JSON in output:\n{stdout}")
        data = json.loads(json_match.group(1))

        # Check required schema elements
        self.assertIn("id", data)
        self.assertEqual(data["id"], "DCVBE027511")
        self.assertIn("term", data)
        self.assertEqual(data["term"], "Burballa")
        # Check POS
        self.assertTrue("grammatical_category" in data or "pos" in data or "raw_pos" in data)
        self.assertEqual(data.get("grammatical_category"), "nom femení")
        # Check definitions
        self.assertTrue("definition" in data or "definitions" in data)
        self.assertIn("ribot", data.get("definition", ""))
        # Check sayings
        self.assertIn("sayings", data)
        self.assertIsInstance(data["sayings"], list)
        self.assertGreater(len(data["sayings"]), 0)
        # Check dialect/geo marks
        self.assertTrue("dialectal_notes" in data or "geo_marks" in data)
        self.assertIn("Mallorca", data.get("dialectal_notes", ""))

    def test_03_crawler_cli_limit_5(self):
        """Verify running with --limit 5 generates exactly 5 valid items."""
        temp_out = PROJECT_ROOT / "database" / "dcvb_test_limit_5.json"
        try:
            res = subprocess.run(
                [
                    sys.executable,
                    str(DCVB_CRAWLER_SCRIPT),
                    "--limit",
                    "5",
                    "--output",
                    str(temp_out),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            self.assertEqual(res.returncode, 0, f"--limit 5 failed: {res.stderr}")
            self.assertTrue(temp_out.exists(), "Output file was not created")

            with open(temp_out, "r", encoding="utf-8") as f:
                items = json.load(f)

            self.assertEqual(len(items), 5, f"Expected 5 items, got {len(items)}")
            for item in items:
                self.assertIn("id", item)
                self.assertIn("term", item)
                self.assertTrue(bool(item["term"].strip()))
                self.assertTrue("grammatical_category" in item or "raw_pos" in item)
                self.assertTrue(bool(item.get("definition")))
                self.assertIn("sayings", item)
                self.assertIn("dialectal_notes", item)
        finally:
            if temp_out.exists():
                temp_out.unlink()

    def test_04_viccionari_balear_entries_schema_and_count(self):
        """Verify database/viccionari_balear_entries.json valid JSON, 944 entries."""
        self.assertTrue(VICCIONARI_JSON.exists(), f"Missing {VICCIONARI_JSON}")
        with open(VICCIONARI_JSON, "r", encoding="utf-8") as f:
            entries = json.load(f)

        self.assertIsInstance(entries, list)
        self.assertEqual(len(entries), 944, f"Expected exactly 944 entries, got {len(entries)}")

        # Check that all entries have pageid, term, categories, definition
        missing_terms = [e for e in entries if not e.get("term") or not str(e["term"]).strip()]
        self.assertEqual(len(missing_terms), 0, "Some entries have empty terms")

        missing_defs = [e for e in entries if not e.get("definition") or not str(e["definition"]).strip()]
        self.assertEqual(len(missing_defs), 0, "Some entries have empty definitions")

        missing_cats = [e for e in entries if not e.get("categories") or len(e["categories"]) == 0]
        self.assertEqual(len(missing_cats), 0, "Some entries have empty categories")

    def test_05_viccionari_sample_10_random_entries(self):
        """Sample 10 random entries checking IPA, definitions, categories, and DCVB URLs."""
        with open(VICCIONARI_JSON, "r", encoding="utf-8") as f:
            entries = json.load(f)

        random.seed(12345)
        samples = random.sample(entries, 10)

        for s in samples:
            # Term check
            self.assertTrue(isinstance(s.get("term"), str) and len(s["term"].strip()) > 0)
            # Pageid check
            self.assertTrue(isinstance(s.get("pageid"), int) and s["pageid"] > 0)
            # Categories check: must contain 'Mallorquí' or 'Balear'
            cats = s.get("categories", [])
            self.assertTrue(any(c in ["Mallorquí", "Balear"] for c in cats), f"Invalid categories: {cats}")
            # Definition check
            defn = s.get("definition", "")
            self.assertTrue(isinstance(defn, str) and len(defn.strip()) > 0)
            # DCVB URL well-formed check
            dcvb_url = s.get("dcvb_url")
            if dcvb_url:
                self.assertTrue(
                    dcvb_url.startswith("https://dcvb.iec.cat/results.asp?word=")
                    or dcvb_url.startswith("https://dcvb.iec.cat/"),
                    f"Malformed DCVB URL: {dcvb_url}",
                )
            # IPA check
            ipa = s.get("ipa_pronunciation")
            if ipa:
                self.assertTrue(
                    ipa.startswith("/") or ipa.startswith("["),
                    f"IPA does not start with / or [: {ipa}",
                )

    def test_06_dcvb_extracted_entries_count_and_dialect_marks(self):
        """Verify database/dcvb_extracted_entries.json has 100 entries and verified Mall./Bal. marks."""
        self.assertTrue(DCVB_JSON.exists(), f"Missing {DCVB_JSON}")
        with open(DCVB_JSON, "r", encoding="utf-8") as f:
            entries = json.load(f)

        self.assertIsInstance(entries, list)
        self.assertEqual(len(entries), 100, f"Expected 100 DCVB entries, got {len(entries)}")

        dialect_pattern = re.compile(r"\b(mall|bal|men|eiv|forment)\w*", re.IGNORECASE)

        for e in entries:
            term = e.get("term")
            self.assertTrue(bool(term), "Missing term")
            notes = e.get("dialectal_notes", "")
            self.assertTrue(
                bool(notes),
                f"Entry {e.get('id')} ({term}) is missing dialectal_notes",
            )
            self.assertTrue(
                dialect_pattern.search(notes) is not None,
                f"Entry {term} dialectal_notes '{notes}' does not match Balearic pattern",
            )
            # Check source reference
            self.assertEqual(e.get("source_reference"), "Diccionari Català-Valencià-Balear (Alcover-Moll)")

    def test_07_rate_limiting_polite_handling_and_caching(self):
        """Confirm User-Agent header, delays, and caching behavior in crawler and scraper."""
        # 1. Inspect dcvb_crawler.py
        with open(DCVB_CRAWLER_SCRIPT, "r", encoding="utf-8") as f:
            crawler_code = f.read()

        self.assertIn("USER_AGENT =", crawler_code)
        self.assertIn("CuriositatsBot", crawler_code)
        self.assertIn("delay: float = 1.2", crawler_code)
        self.assertIn("time.sleep(self.delay)", crawler_code)
        self.assertIn("self.cache_dir", crawler_code)

        # 2. Inspect viccionari_balear_scraper.py
        with open(VICCIONARI_SCRAPER_SCRIPT, "r", encoding="utf-8") as f:
            scraper_code = f.read()

        self.assertIn("USER_AGENT =", scraper_code)
        self.assertIn("CuriositatsBot", scraper_code)
        self.assertIn("REQUEST_DELAY = 0.35", scraper_code)
        self.assertIn("time.sleep", scraper_code)

        # 3. Cache directory verification
        self.assertTrue(DCVB_CACHE_DIR.exists(), f"Cache dir {DCVB_CACHE_DIR} does not exist")
        cache_files = list(DCVB_CACHE_DIR.glob("*.xml"))
        self.assertGreaterEqual(len(cache_files), 100, f"Expected >= 100 XML cache files, found {len(cache_files)}")
        self.assertTrue((DCVB_CACHE_DIR / "dcvb_dialect_ids.json").exists(), "Missing dcvb_dialect_ids.json cache")

    def test_08_adversarial_cli_inputs(self):
        """Stress-test dcvb_crawler.py with malicious, edge case, and boundary CLI inputs."""
        temp_zero = PROJECT_ROOT / "database" / "temp_zero.json"
        adversarial_cases = [
            ("Nonexistent term", ["--term", "nonexistenttermxyz999888"]),
            ("SQL Injection payload", ["--term", "'; DROP TABLE words; --"]),
            ("XSS payload", ["--term", "<script>alert('XSS')</script>"]),
            ("Special unicode punctuation", ["--term", "¡¿·...---"]),
            ("Zero limit boundary", ["--limit", "0", "--output", str(temp_zero)]),
        ]

        try:
            for name, args in adversarial_cases:
                res = subprocess.run(
                    [sys.executable, str(DCVB_CRAWLER_SCRIPT)] + args,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                # The crawler should not crash with unhandled exception
                self.assertEqual(res.returncode, 0, f"Adversarial case '{name}' failed with code {res.returncode}: {res.stderr}")
                self.assertNotIn("Traceback (most recent call last):", res.stderr)

            # Document boundary observation: crawler checks limit AFTER first append,
            # so limit=0 extracts 1 item instead of 0.
            if temp_zero.exists():
                with open(temp_zero, "r", encoding="utf-8") as f:
                    zero_data = json.load(f)
                self.assertEqual(len(zero_data), 1, "Boundary finding confirmed: limit=0 yields 1 entry due to post-append check")
        finally:
            if temp_zero.exists():
                temp_zero.unlink()

    def test_09_database_deduplication_and_integrity(self):
        """Stress-test curiositats.db words table after all corpus imports."""
        self.assertTrue(DB_PATH.exists(), f"Database missing at {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check total words count: should include seed + diec (91) + viccionari (944) + dcvb (100) minus overlaps
        cursor.execute("SELECT COUNT(*) FROM words")
        total_words = cursor.fetchone()[0]
        self.assertGreaterEqual(total_words, 1000, f"Expected >= 1000 words, got {total_words}")

        # Check for case-insensitive duplicates
        cursor.execute(
            """
            SELECT LOWER(TRIM(term)), COUNT(*)
            FROM words
            GROUP BY LOWER(TRIM(term))
            HAVING COUNT(*) > 1
            """
        )
        duplicates = cursor.fetchall()
        self.assertEqual(len(duplicates), 0, f"Found duplicate terms in curiositats.db: {duplicates}")

        # Check for empty mandatory fields
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM words
            WHERE term IS NULL OR TRIM(term) = '' OR definition IS NULL OR TRIM(definition) = ''
            """
        )
        empty_records = cursor.fetchone()[0]
        self.assertEqual(empty_records, 0, f"Found {empty_records} records with empty term or definition")

        conn.close()

    def test_10_cache_data_structure_integrity(self):
        """Verify the integrity of cached dialect IDs and XML documents."""
        ids_file = DCVB_CACHE_DIR / "dcvb_dialect_ids.json"
        self.assertTrue(ids_file.exists(), "Missing dcvb_dialect_ids.json")
        with open(ids_file, "r", encoding="utf-8") as f:
            cached_ids = json.load(f)

        self.assertIsInstance(cached_ids, list)
        self.assertGreaterEqual(len(cached_ids), 20000, f"Expected >= 20000 cached IDs, got {len(cached_ids)}")

        # Verify ID format (e.g., DCVBE000002)
        id_pattern = re.compile(r"^DCVBE\d+$")
        for eid in cached_ids[:500]:
            self.assertTrue(id_pattern.match(eid), f"Malformed ID: {eid}")


if __name__ == "__main__":
    unittest.main()

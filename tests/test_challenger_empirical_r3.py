#!/usr/bin/env python3
"""Empirical Challenger Test Suite — Round 3.

Adversarial stress-testing of 'Una teringa de curiositats':
1. Catalan diacritic search (NFD decomposed vs NFC precomposed equivalence)
2. Database CHECK constraints enforcement and runtime rejection:
   - Latitude boundary [39.0, 40.2]
   - Longitude boundary [2.2, 3.6]
   - Foundation year (> 1200)
   - Historical event timeline (year_start <= year_end)
3. Dates and Chronological integrity
4. SQL Injection and XSS attack resilience across endpoints
"""

import json
from pathlib import Path
import sqlite3
import sys
import unicodedata
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.base import DB_PATH, fetch_api, start_test_server
import server


class TestEmpiricalChallengerR3(unittest.TestCase):
    """Adversarial challenger test cases."""

    @classmethod
    def setUpClass(cls):
        start_test_server()
        cls.conn = sqlite3.connect(DB_PATH)
        cls.conn.row_factory = sqlite3.Row

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "conn") and cls.conn:
            cls.conn.close()

    # =========================================================================
    # 1. CATALAN DIACRITIC SEARCH (NFD vs NFC EQUIVALENCE)
    # =========================================================================

    def test_catalan_nfd_vs_nfc_diacritic_search_equivalence(self):
        """Verify NFD decomposed and NFC precomposed forms yield identical results."""
        catalan_test_cases = [
            # Precomposed, Decomposed description
            ("talaiòtic", "o + combining grave accent (\\u0300)"),
            ("raça", "c + combining cedilla (\\u0327)"),
            ("pericó", "o + combining acute accent (\\u0301)"),
            ("ensaïmada", "i + combining diaeresis (\\u0308)"),
            ("còco", "first o + combining grave accent (\\u0300)"),
            ("fàcil", "a + combining grave accent (\\u0300)"),
            ("més", "e + combining acute accent (\\u0301)"),
            ("al·lot", "Catalan ela geminada with middle dot"),
            ("lluïssor", "i + combining diaeresis"),
            ("balear", "unaccented baseline"),
        ]

        for word, desc in catalan_test_cases:
            nfc_form = unicodedata.normalize("NFC", word)
            nfd_form = unicodedata.normalize("NFD", word)

            with self.subTest(word=word, description=desc):
                # 1. Test direct server logic
                res_nfc = server.fetch_all_curiositats(search=nfc_form)
                res_nfd = server.fetch_all_curiositats(search=nfd_form)
                self.assertEqual(
                    res_nfc, res_nfd,
                    f"Direct server search mismatch for '{word}' between NFC and NFD"
                )

                # 2. Test HTTP API endpoint
                status_nfc, data_nfc, _ = fetch_api("/api/curiositats", {"search": nfc_form})
                status_nfd, data_nfd, _ = fetch_api("/api/curiositats", {"search": nfd_form})

                self.assertEqual(status_nfc, 200, f"HTTP error for NFC query '{nfc_form}'")
                self.assertEqual(status_nfd, 200, f"HTTP error for NFD query '{nfd_form}'")
                self.assertEqual(
                    len(data_nfc), len(data_nfd),
                    f"Result count mismatch for '{word}': NFC={len(data_nfc)}, NFD={len(data_nfd)}"
                )
                self.assertEqual(
                    data_nfc, data_nfd,
                    f"Data mismatch for '{word}' between NFC and NFD via HTTP"
                )

    def test_catalan_specific_nfd_talaio_u0300_tic(self):
        """Explicitly test dispatch requirement: talaio\\u0300tic vs talaiòtic."""
        explicit_nfd = "talaio\u0300tic"
        explicit_nfc = "talaiòtic"

        status_nfc, data_nfc, _ = fetch_api("/api/curiositats", {"search": explicit_nfc})
        status_nfd, data_nfd, _ = fetch_api("/api/curiositats", {"search": explicit_nfd})

        self.assertEqual(status_nfc, 200)
        self.assertEqual(status_nfd, 200)
        self.assertGreater(len(data_nfc), 0, "Expected at least 1 match for talaiòtic")
        self.assertEqual(data_nfc, data_nfd, "NFD and NFC for talaiòtic must be 100% identical")

    # =========================================================================
    # 2. DATABASE CHECK CONSTRAINTS AUDIT & ENFORCEMENT
    # =========================================================================

    def test_existing_data_satisfies_all_domain_constraints(self):
        """Verify all existing rows in database strictly satisfy coordinate and date constraints."""
        c = self.conn.cursor()

        # Businesses constraints
        c.execute("SELECT id, name, latitude, longitude, foundation_year FROM emblematic_businesses")
        businesses = c.fetchall()
        self.assertGreaterEqual(len(businesses), 5)
        for b in businesses:
            bid, name, lat, lon, year = b["id"], b["name"], b["latitude"], b["longitude"], b["foundation_year"]
            self.assertIsNotNone(lat, f"Business {name} (id {bid}) has NULL latitude")
            self.assertIsNotNone(lon, f"Business {name} (id {bid}) has NULL longitude")
            self.assertTrue(
                39.0 <= lat <= 40.2,
                f"Business {name} lat {lat} outside [39.0, 40.2]"
            )
            self.assertTrue(
                2.2 <= lon <= 3.6,
                f"Business {name} lon {lon} outside [2.2, 3.6]"
            )
            if year is not None:
                self.assertGreater(
                    year, 1200,
                    f"Business {name} foundation_year {year} not > 1200"
                )

        # Historical events constraints
        c.execute("SELECT id, title, year_start, year_end FROM historical_events")
        events = c.fetchall()
        self.assertGreaterEqual(len(events), 6)
        for e in events:
            eid, title, ys, ye = e["id"], e["title"], e["year_start"], e["year_end"]
            self.assertIsNotNone(ys, f"Event {title} (id {eid}) has NULL year_start")
            if ye is not None:
                self.assertLessEqual(
                    ys, ye,
                    f"Event {title} year_start ({ys}) > year_end ({ye})"
                )

    def test_sqlite_enforces_coordinate_check_constraints(self):
        """Adversarial stress test: SQLite rejects coordinates outside Balearic bounds."""
        test_conn = sqlite3.connect(DB_PATH)
        test_cur = test_conn.cursor()

        try:
            # 1. Latitude below minimum (38.999)
            with self.assertRaises(sqlite3.IntegrityError, msg="Failed to reject lat < 39.0"):
                test_cur.execute(
                    "INSERT INTO emblematic_businesses "
                    "(name, category_type, sector, municipality, history_summary, latitude, longitude) "
                    "VALUES ('Test Lat Low', 'Comerç arrelat', 'Forn', 'Palma', 'Desc', 38.999, 2.5)"
                )

            # 2. Latitude above maximum (40.201)
            with self.assertRaises(sqlite3.IntegrityError, msg="Failed to reject lat > 40.2"):
                test_cur.execute(
                    "INSERT INTO emblematic_businesses "
                    "(name, category_type, sector, municipality, history_summary, latitude, longitude) "
                    "VALUES ('Test Lat High', 'Comerç arrelat', 'Forn', 'Palma', 'Desc', 40.201, 2.5)"
                )

            # 3. Longitude below minimum (2.199)
            with self.assertRaises(sqlite3.IntegrityError, msg="Failed to reject lon < 2.2"):
                test_cur.execute(
                    "INSERT INTO emblematic_businesses "
                    "(name, category_type, sector, municipality, history_summary, latitude, longitude) "
                    "VALUES ('Test Lon Low', 'Comerç arrelat', 'Forn', 'Palma', 'Desc', 39.5, 2.199)"
                )

            # 4. Longitude above maximum (3.601)
            with self.assertRaises(sqlite3.IntegrityError, msg="Failed to reject lon > 3.6"):
                test_cur.execute(
                    "INSERT INTO emblematic_businesses "
                    "(name, category_type, sector, municipality, history_summary, latitude, longitude) "
                    "VALUES ('Test Lon High', 'Comerç arrelat', 'Forn', 'Palma', 'Desc', 39.5, 3.601)"
                )

            # 5. Boundary valid inserts: exactly 39.0 and 40.2, 2.2 and 3.6
            test_cur.execute(
                "INSERT INTO emblematic_businesses "
                "(name, category_type, sector, municipality, history_summary, latitude, longitude) "
                "VALUES ('Test Bound Min', 'Comerç arrelat', 'Forn', 'Palma', 'Desc', 39.0, 2.2)"
            )
            test_cur.execute(
                "INSERT INTO emblematic_businesses "
                "(name, category_type, sector, municipality, history_summary, latitude, longitude) "
                "VALUES ('Test Bound Max', 'Comerç arrelat', 'Forn', 'Palma', 'Desc', 40.2, 3.6)"
            )
        finally:
            test_conn.rollback()
            test_conn.close()

    def test_sqlite_enforces_foundation_year_check_constraint(self):
        """Adversarial stress test: SQLite rejects foundation_year <= 1200."""
        test_conn = sqlite3.connect(DB_PATH)
        test_cur = test_conn.cursor()

        try:
            # 1. Exactly 1200 (boundary condition: CHECK specifies > 1200, so 1200 is illegal)
            with self.assertRaises(sqlite3.IntegrityError, msg="Failed to reject foundation_year == 1200"):
                test_cur.execute(
                    "INSERT INTO emblematic_businesses "
                    "(name, category_type, sector, municipality, history_summary, latitude, longitude, foundation_year) "
                    "VALUES ('Test Year 1200', 'Comerç arrelat', 'Forn', 'Palma', 'Desc', 39.5, 2.5, 1200)"
                )

            # 2. Pre-1200 (e.g. 800)
            with self.assertRaises(sqlite3.IntegrityError, msg="Failed to reject foundation_year == 800"):
                test_cur.execute(
                    "INSERT INTO emblematic_businesses "
                    "(name, category_type, sector, municipality, history_summary, latitude, longitude, foundation_year) "
                    "VALUES ('Test Year 800', 'Comerç arrelat', 'Forn', 'Palma', 'Desc', 39.5, 2.5, 800)"
                )

            # 3. Boundary valid insert: 1201
            test_cur.execute(
                "INSERT INTO emblematic_businesses "
                "(name, category_type, sector, municipality, history_summary, latitude, longitude, foundation_year) "
                "VALUES ('Test Year 1201', 'Comerç arrelat', 'Forn', 'Palma', 'Desc', 39.5, 2.5, 1201)"
            )

            # 4. Valid NULL foundation_year
            test_cur.execute(
                "INSERT INTO emblematic_businesses "
                "(name, category_type, sector, municipality, history_summary, latitude, longitude, foundation_year) "
                "VALUES ('Test Year NULL', 'Comerç arrelat', 'Forn', 'Palma', 'Desc', 39.5, 2.5, NULL)"
            )
        finally:
            test_conn.rollback()
            test_conn.close()

    def test_sqlite_enforces_historical_event_year_ordering(self):
        """Adversarial stress test: SQLite rejects year_start > year_end."""
        test_conn = sqlite3.connect(DB_PATH)
        test_cur = test_conn.cursor()

        try:
            # 1. year_start > year_end (1500 > 1499)
            with self.assertRaises(sqlite3.IntegrityError, msg="Failed to reject year_start > year_end"):
                test_cur.execute(
                    "INSERT INTO historical_events "
                    "(title, historical_period, year_start, year_end, date_display, summary) "
                    "VALUES ('Inverted Timeline', 'Edat Moderna', 1500, 1499, '1500-1499', 'Desc')"
                )

            # 2. Boundary condition: year_start == year_end (single year event)
            test_cur.execute(
                "INSERT INTO historical_events "
                "(title, historical_period, year_start, year_end, date_display, summary) "
                "VALUES ('Single Year Boundary', 'Edat Mitjana', 1229, 1229, '1229', 'Desc')"
            )

            # 3. Valid NULL year_end (ongoing or punctual event)
            test_cur.execute(
                "INSERT INTO historical_events "
                "(title, historical_period, year_start, year_end, date_display, summary) "
                "VALUES ('Punctual Event', 'Prehistòria', -1000, NULL, 'c. 1000 a. C.', 'Desc')"
            )
        finally:
            test_conn.rollback()
            test_conn.close()

    # =========================================================================
    # 3. DATES & CHRONOLOGY
    # =========================================================================

    def test_historical_events_dates_structure(self):
        """Verify date displays and year numbers have coherent historical ranges."""
        c = self.conn.cursor()
        c.execute("SELECT title, year_start, year_end, date_display FROM historical_events")
        rows = c.fetchall()

        for r in rows:
            title = r["title"]
            ys = r["year_start"]
            ye = r["year_end"]
            dd = r["date_display"]

            self.assertTrue(len(dd.strip()) > 0, f"Empty date_display for '{title}'")
            self.assertGreaterEqual(ys, -3000, f"Unreasonably ancient year_start {ys} for '{title}'")
            self.assertLessEqual(ys, 2026, f"Future year_start {ys} for '{title}'")
            if ye is not None:
                self.assertLessEqual(ye, 2026, f"Future year_end {ye} for '{title}'")

    # =========================================================================
    # 4. ADVERSARIAL SQL INJECTION & XSS ATTACKS
    # =========================================================================

    def test_sql_injection_payloads_in_search(self):
        """Adversarial attacks: SQL injection in /api/curiositats?search=..."""
        sqli_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE words; --",
            "' UNION SELECT 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 --",
            "admin' --",
            "1' AND 1=1 --",
            "' OR EXISTS(SELECT * FROM words) --",
            "1; SELECT pg_sleep(1); --",
            "' OR (SELECT count(*) FROM words) > 0 --",
        ]

        for payload in sqli_payloads:
            with self.subTest(payload=payload):
                status, items, headers = fetch_api("/api/curiositats", {"search": payload})
                self.assertEqual(status, 200)
                self.assertIsInstance(items, list)
                # Since literal string doesn't exist in data, it should return 0 items
                self.assertEqual(len(items), 0, f"SQLi payload leaked data: {payload}")
                self.assertIn("application/json", headers.get("Content-Type", ""))

    def test_sql_injection_payloads_in_category(self):
        """Adversarial attacks: SQL injection in /api/curiositats?category=..."""
        sqli_payloads = [
            "words' OR '1'='1",
            "words'; DROP TABLE words; --",
            "' UNION SELECT * FROM words --",
        ]

        for payload in sqli_payloads:
            with self.subTest(payload=payload):
                status, items, _ = fetch_api("/api/curiositats", {"category": payload})
                self.assertEqual(status, 200)
                self.assertIsInstance(items, list)
                self.assertEqual(len(items), 0)

    def test_sql_injection_payloads_in_random_category(self):
        """Adversarial attacks: SQL injection in /api/random?category=..."""
        sqli_payloads = [
            "words'; DROP TABLE words; --",
            "' OR 1=1 --",
        ]

        for payload in sqli_payloads:
            with self.subTest(payload=payload):
                status, data, _ = fetch_api("/api/random", {"category": payload})
                self.assertEqual(status, 404, f"Expected 404 for malicious category {payload}")
                self.assertIn("error", data)
                self.assertEqual(data["error"], "Not Found")

    def test_xss_injection_payloads(self):
        """Adversarial attacks: XSS injection payloads in query parameters."""
        xss_payloads = [
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "<svg/onload=alert(1)>",
            "javascript:alert('XSS')",
            "\"><script>alert(document.cookie)</script>",
        ]

        for payload in xss_payloads:
            with self.subTest(payload=payload):
                status, items, headers = fetch_api("/api/curiositats", {"search": payload})
                self.assertEqual(status, 200)
                self.assertEqual(len(items), 0)
                # Confirm response content-type strictly application/json (stops browser HTML execution)
                self.assertTrue(
                    headers.get("Content-Type", "").startswith("application/json"),
                    f"Insecure Content-Type: {headers.get('Content-Type')}"
                )


if __name__ == "__main__":
    unittest.main()

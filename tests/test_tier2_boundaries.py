"""Tier 2: Boundary & Corner Cases Tests for 'Una teringa de curiositats'.

Covers boundary conditions, edge cases, and adversarial input testing:
- Accented search (Catalan diacritics: ç, l·l, à, è, é, í, ò, ó, ú, ï, ü)
- Empty, whitespace-only, and extremely long search strings
- Malicious search inputs (SQL injection characters, XSS meta-characters)
- Invalid and malformed category query parameters
- Coordinate and year boundary constraints
- Database character encoding integrity (zero mojibake / U+FFFD)
"""

import json
import sqlite3
import urllib.parse

from tests.base import (
    DB_PATH,
    SEED_PATH,
    TeringaTestCase,
    detect_mojibake,
    fetch_api,
    get_db_connection,
)


class TestTier2BoundariesAndCornerCases(TeringaTestCase):
    """Tier 2: Boundary conditions, corner cases, and adversarial resilience."""

    # =========================================================================
    # ACCENTED & CATALAN DIACRITICS SEARCH
    # =========================================================================

    def test_search_catalan_accented_lowercase(self):
        """Verify search matches words with acute/grave accents correctly (e.g. 'talaiòtic')."""
        status, items, _ = fetch_api("/api/curiositats", {"search": "talaiòtic"})
        self.assertEqual(status, 200)
        self.assertIsInstance(items, list)
        self.assertGreaterEqual(len(items), 1, "Expected match for accented query 'talaiòtic'")
        titles = [it.get("title", "") for it in items]
        self.assertTrue(
            any("Talaiòtica" in t or "talaiòtic" in t.lower() for t in titles),
            f"Expected Talaiòtica event in results: {titles}"
        )

    def test_search_catalan_accented_uppercase(self):
        """Verify search is case-insensitive for accented Catalan characters (e.g. 'TALAIÒTICA')."""
        status, items, _ = fetch_api("/api/curiositats", {"search": "TALAIÒTICA"})
        self.assertEqual(status, 200)
        self.assertIsInstance(items, list)
        self.assertGreaterEqual(len(items), 1, "Expected case-insensitive match for 'TALAIÒTICA'")

    def test_search_catalan_cedilla(self):
        """Verify search handles Catalan 'ç' (e.g. 'raça' or 'força')."""
        status, items, _ = fetch_api("/api/curiositats", {"search": "raça"})
        self.assertEqual(status, 200)
        self.assertIsInstance(items, list)
        # Should match fauna entries with tag or definition containing 'raça'
        self.assertGreaterEqual(len(items), 1, "Expected results for search 'raça'")

    def test_search_catalan_ela_geminada(self):
        """Verify search handles Catalan 'l·l' (ela geminada)."""
        status, items, _ = fetch_api("/api/curiositats", {"search": "l·l"})
        self.assertEqual(status, 200)
        self.assertIsInstance(items, list)
        # Should match words or descriptions containing ela geminada (e.g. 'col·loquial')
        self.assertGreaterEqual(len(items), 1, "Expected results for ela geminada 'l·l'")

    # =========================================================================
    # SEARCH INPUT BOUNDARIES & RESILIENCE
    # =========================================================================

    def test_search_empty_query(self):
        """Verify empty search query (?search=) returns all items without error."""
        status, items, _ = fetch_api("/api/curiositats", {"search": ""})
        self.assertEqual(status, 200)
        self.assertIsInstance(items, list)
        self.assertGreaterEqual(len(items), 31, "Empty search should return full catalog")

    def test_search_whitespace_query(self):
        """Verify whitespace-only query (?search=%20%20) returns full catalog or empty safely."""
        status, items, _ = fetch_api("/api/curiositats", {"search": "   "})
        self.assertEqual(status, 200)
        self.assertIsInstance(items, list)
        # server.py strips whitespace: s = search.lower().strip() -> if empty, returns all items
        self.assertGreaterEqual(len(items), 31, "Whitespace query should resolve cleanly to all items")

    def test_search_sql_injection_attempt(self):
        """Verify search input containing SQL injection patterns is treated as literal text."""
        malicious_queries = [
            "' OR 1=1 --",
            "'; DROP TABLE words; --",
            "\" UNION SELECT NULL, NULL, NULL --",
            "admin' --",
        ]
        for q in malicious_queries:
            status, items, _ = fetch_api("/api/curiositats", {"search": q})
            self.assertEqual(status, 200, f"Query '{q}' caused server failure")
            self.assertIsInstance(items, list)
            # Must return empty list rather than leaking all rows or breaking
            self.assertEqual(len(items), 0, f"Query '{q}' unexpectedly returned items")

    def test_search_html_xss_characters(self):
        """Verify search input containing HTML tags and script payloads is handled safely."""
        xss_queries = [
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "&quot;hello&quot;",
        ]
        for q in xss_queries:
            status, items, _ = fetch_api("/api/curiositats", {"search": q})
            self.assertEqual(status, 200, f"XSS query '{q}' caused server failure")
            self.assertIsInstance(items, list)
            self.assertEqual(len(items), 0)

    def test_search_extreme_length_query(self):
        """Verify extremely long query string (500 chars) does not crash server."""
        long_query = "x" * 500
        status, items, _ = fetch_api("/api/curiositats", {"search": long_query})
        self.assertEqual(status, 200)
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 0)

    # =========================================================================
    # CATEGORY PARAMETER BOUNDARIES
    # =========================================================================

    def test_category_invalid_slug(self):
        """Verify non-existent category (?category=nonexistent) returns empty list with status 200."""
        status, items, _ = fetch_api("/api/curiositats", {"category": "nonexistent_slug"})
        self.assertEqual(status, 200, "Invalid category must return 200 OK")
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 0, "Invalid category must return empty list")

    def test_category_injection_characters(self):
        """Verify category containing special/injection characters returns empty list safely."""
        status, items, _ = fetch_api("/api/curiositats", {"category": "words'; DROP TABLE words;--"})
        self.assertEqual(status, 200)
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 0)

    # =========================================================================
    # DATA DOMAIN BOUNDARIES & CONSTRAINTS
    # =========================================================================

    def test_coordinates_geographic_bounds(self):
        """Verify emblematic business coordinates lie strictly within Balearic boundaries."""
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT name, latitude, longitude FROM emblematic_businesses")
        rows = c.fetchall()
        conn.close()

        self.assertGreaterEqual(len(rows), 1, "No businesses found in database")
        for r in rows:
            name, lat, lon = r["name"], r["latitude"], r["longitude"]
            self.assertIsNotNone(lat, f"Latitude is NULL for business '{name}'")
            self.assertIsNotNone(lon, f"Longitude is NULL for business '{name}'")
            self.assertTrue(
                39.0 <= lat <= 40.2,
                f"Business '{name}' latitude {lat} is outside Balearic range [39.0, 40.2]"
            )
            self.assertTrue(
                2.2 <= lon <= 3.6,
                f"Business '{name}' longitude {lon} is outside Balearic range [2.2, 3.6]"
            )

    def test_foundation_year_bounds(self):
        """Verify foundation_year in emblematic businesses is either NULL or > 1200."""
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT name, foundation_year FROM emblematic_businesses")
        rows = c.fetchall()
        conn.close()

        for r in rows:
            name, year = r["name"], r["foundation_year"]
            if year is not None:
                self.assertGreater(
                    year,
                    1200,
                    f"Foundation year {year} for '{name}' is suspiciously ancient (must be > 1200)"
                )
                self.assertLessEqual(
                    year,
                    2026,
                    f"Foundation year {year} for '{name}' cannot be in the future"
                )

    def test_historical_events_year_ordering(self):
        """Verify year_start <= year_end for all historical events where year_end is specified."""
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT title, year_start, year_end FROM historical_events")
        rows = c.fetchall()
        conn.close()

        for r in rows:
            title, y_start, y_end = r["title"], r["year_start"], r["year_end"]
            self.assertIsNotNone(y_start, f"year_start cannot be NULL for event '{title}'")
            if y_end is not None:
                self.assertLessEqual(
                    y_start,
                    y_end,
                    f"Event '{title}' has inverted timeline: year_start ({y_start}) > year_end ({y_end})"
                )

    # =========================================================================
    # CHARACTER ENCODING & MOJIBAKE AUDIT
    # =========================================================================

    def test_database_encoding_integrity(self):
        """Audit all textual fields across all database tables for mojibake or U+FFFD."""
        conn = get_db_connection()
        c = conn.cursor()

        tables_and_columns = {
            "words": ["term", "definition", "example_sentence", "etymology", "dialectal_notes"],
            "fauna": ["common_name_ca", "scientific_name", "habitat", "description", "curiosities"],
            "flora": ["common_name_ca", "scientific_name", "habitat", "description", "curiosities"],
            "emblematic_businesses": ["name", "municipality", "address", "history_summary", "heritage_elements"],
            "historical_events": ["title", "historical_period", "date_display", "summary", "detailed_description"],
        }

        for table, columns in tables_and_columns.items():
            col_list = ", ".join(columns)
            c.execute(f"SELECT {col_list} FROM {table}")
            rows = c.fetchall()
            for r in rows:
                for col in columns:
                    val = r[col]
                    if isinstance(val, str):
                        self.assertCatalanTextClean(val, f"{table}.{col}")

        conn.close()

    def test_seed_data_encoding_integrity(self):
        """Audit seed_data.json content for mojibake or corrupt characters."""
        with open(SEED_PATH, "r", encoding="utf-8") as f:
            raw_text = f.read()

        findings = detect_mojibake(raw_text)
        self.assertEqual(
            findings,
            [],
            f"Detected encoding corruption in seed_data.json: {findings}"
        )

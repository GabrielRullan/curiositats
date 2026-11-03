"""Tier 3: Cross-Feature Interactions Tests for 'Una teringa de curiositats'.

Covers module and contract interactions across the full system stack:
- Stats API aggregation vs Curiositats items length and category partitioning
- Combined category and search query filters
- Database records vs Canonical seed_data.json consistency
- Database catalog vs Frontend FALLBACK_DATA parity in web/app.js
- OpenAPI 3.x specification contracts vs live server responses
"""

import json
import sqlite3

from tests.base import (
    DB_PATH,
    SEED_PATH,
    TeringaTestCase,
    WEB_DIR,
    extract_fallback_data,
    fetch_api,
    get_db_connection,
    is_m1_ready,
    is_m4_ready,
    milestone_requirement,
)


def is_fallback_data_synced() -> bool:
    """Check if web/app.js FALLBACK_DATA contains 31 items."""
    items = extract_fallback_data()
    return len(items) == 31


class TestTier3CrossFeatureInteractions(TeringaTestCase):
    """Tier 3: Cross-feature contracts and data synchronization tests."""

    # =========================================================================
    # STATS AGGREGATION VS CURIOSITATS ENDPOINT CONTRACTS
    # =========================================================================

    def test_stats_total_matches_curiositats_count(self):
        """Verify /api/stats 'total' equals the exact length of unfiltered /api/curiositats."""
        status_stats, stats, _ = fetch_api("/api/stats")
        self.assertEqual(status_stats, 200)

        status_items, items, _ = fetch_api("/api/curiositats")
        self.assertEqual(status_items, 200)

        self.assertEqual(
            stats["total"],
            len(items),
            f"/api/stats total ({stats['total']}) does not match /api/curiositats count ({len(items)})"
        )

    def test_stats_category_breakdown_matches_filtered_endpoints(self):
        """Verify each category count in /api/stats exactly equals /api/curiositats?category=<cat>."""
        _, stats, _ = fetch_api("/api/stats")

        categories_map = {
            "words": "words",
            "fauna": "fauna",
            "flora": "flora",
            "businesses": "businesses",
            "history": "history",
        }

        partition_sum = 0
        for stat_key, query_cat in categories_map.items():
            status, items, _ = fetch_api("/api/curiositats", {"category": query_cat})
            self.assertEqual(status, 200)
            self.assertEqual(
                stats[stat_key],
                len(items),
                f"Count mismatch for '{stat_key}': stats has {stats[stat_key]}, query returned {len(items)}"
            )
            partition_sum += len(items)

        self.assertEqual(
            partition_sum,
            stats["total"],
            "Sum of individual category queries must equal stats total"
        )

    def test_combined_category_and_search_query(self):
        """Verify combining category and search parameters produces intersection of both filters."""
        # Query 1: search 'moix' in words -> should return 'Qui no té feina el moix pentina'
        status, items_words, _ = fetch_api("/api/curiositats", {"category": "words", "search": "moix"})
        self.assertEqual(status, 200)
        self.assertGreaterEqual(len(items_words), 1, "Expected search 'moix' to find proverb in words")
        for it in items_words:
            self.assertEqual(it["type"], "words")
            corpus = f"{it['title']} {it['subtitle']} {it['tag']} {it['definition']}".lower()
            self.assertIn("moix", corpus)

        # Query 2: search 'moix' in fauna -> should return 0 items
        status, items_fauna, _ = fetch_api("/api/curiositats", {"category": "fauna", "search": "moix"})
        self.assertEqual(status, 200)
        self.assertEqual(len(items_fauna), 0, "Query 'moix' in fauna must yield 0 results")

    # =========================================================================
    # DATABASE VS SEED DATA CANONICAL ALIGNMENT
    # =========================================================================

    def test_database_matches_seed_data_records(self):
        """Verify every item in database/seed_data.json exists 1:1 in curiositats.db."""
        with open(SEED_PATH, "r", encoding="utf-8") as f:
            seed = json.load(f)

        conn = get_db_connection()
        c = conn.cursor()

        # 1. Words
        for w in seed.get("words", []):
            term = w["term"]
            c.execute("SELECT definition FROM words WHERE term = ?", (term,))
            row = c.fetchone()
            self.assertIsNotNone(row, f"Seed word '{term}' not found in curiositats.db")

        # 2. Fauna
        for fa in seed.get("fauna", []):
            name = fa["common_name_ca"]
            c.execute("SELECT scientific_name FROM fauna WHERE common_name_ca = ?", (name,))
            row = c.fetchone()
            self.assertIsNotNone(row, f"Seed fauna '{name}' not found in curiositats.db")

        # 3. Flora
        for fl in seed.get("flora", []):
            name = fl["common_name_ca"]
            c.execute("SELECT scientific_name FROM flora WHERE common_name_ca = ?", (name,))
            row = c.fetchone()
            self.assertIsNotNone(row, f"Seed flora '{name}' not found in curiositats.db")

        # 4. Businesses
        for b in seed.get("emblematic_businesses", []):
            name = b["name"]
            c.execute("SELECT municipality FROM emblematic_businesses WHERE name = ?", (name,))
            row = c.fetchone()
            self.assertIsNotNone(row, f"Seed business '{name}' not found in curiositats.db")

        # 5. Historical events
        for ev in seed.get("historical_events", []):
            title = ev["title"]
            c.execute("SELECT year_start FROM historical_events WHERE title = ?", (title,))
            row = c.fetchone()
            self.assertIsNotNone(row, f"Seed event '{title}' not found in curiositats.db")

        conn.close()

    # =========================================================================
    # DATABASE VS FRONTEND FALLBACK_DATA PARITY
    # =========================================================================

    @milestone_requirement("M1", is_fallback_data_synced, "Synchronization of web/app.js FALLBACK_DATA to 31 items")
    def test_frontend_fallback_data_parity_with_database(self):
        """Verify web/app.js FALLBACK_DATA has all 31 items matching database titles."""
        fallback_items = extract_fallback_data()
        self.assertEqual(
            len(fallback_items),
            31,
            f"FALLBACK_DATA in web/app.js has {len(fallback_items)} items; expected 31"
        )

        # Verify every fallback title exists in curiositats.db
        conn = get_db_connection()
        c = conn.cursor()

        db_titles = set()
        c.execute("SELECT term AS title FROM words")
        db_titles.update(r[0] for r in c.fetchall())
        c.execute("SELECT common_name_ca AS title FROM fauna")
        db_titles.update(r[0] for r in c.fetchall())
        c.execute("SELECT common_name_ca AS title FROM flora")
        db_titles.update(r[0] for r in c.fetchall())
        c.execute("SELECT name AS title FROM emblematic_businesses")
        db_titles.update(r[0] for r in c.fetchall())
        c.execute("SELECT title FROM historical_events")
        db_titles.update(r[0] for r in c.fetchall())
        conn.close()

        fallback_titles = {item["title"] for item in fallback_items if "title" in item}
        for fb_title in fallback_titles:
            self.assertIn(
                fb_title,
                db_titles,
                f"Fallback item title '{fb_title}' has no corresponding record in curiositats.db"
            )

    # =========================================================================
    # OPENAPI SPECIFICATION VS LIVE SERVER ROUTE CONSISTENCY
    # =========================================================================

    @milestone_requirement("M4", is_m4_ready, "OpenAPI spec contract validation against live server")
    def test_openapi_spec_contracts_match_server_responses(self):
        """Verify paths declared in web/openapi.json respond according to spec status codes."""
        openapi_file = WEB_DIR / "openapi.json"
        with open(openapi_file, "r", encoding="utf-8") as f:
            spec = json.load(f)

        paths = spec.get("paths", {})
        for path, operations in paths.items():
            for method, op_def in operations.items():
                if method.lower() == "get":
                    status, body, headers = fetch_api(path)
                    expected_responses = op_def.get("responses", {})
                    self.assertIn(
                        str(status),
                        expected_responses,
                        f"Live server returned HTTP {status} for {path}, but spec only declares: {list(expected_responses.keys())}"
                    )
                    content_spec = expected_responses[str(status)].get("content", {})
                    if "application/json" in content_spec:
                        self.assertIn("application/json", headers.get("Content-Type", ""))

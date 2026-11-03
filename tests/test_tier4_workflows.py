"""Tier 4: Real-World Application Workflows Tests for 'Una teringa de curiositats'.

Covers end-to-end user workflows, lifecycle operations, and integration flows:
- End-to-end data loading and system health verification
- Interactive catalog navigation, faceted filtering, and detail modal inspection
- Spotlight random curiosity discovery workflow ("Una a la sort")
- Static CDN offline fallback parity simulation
- Database initialization and zero-state recovery workflow (scripts/importers/init_db.py)
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from tests.base import (
    DB_PATH,
    INIT_DB_SCRIPT,
    PROJECT_ROOT,
    SCHEMA_PATH,
    SEED_PATH,
    TeringaTestCase,
    extract_fallback_data,
    fetch_api,
    get_db_connection,
)


class TestTier4RealWorldWorkflows(TeringaTestCase):
    """Tier 4: User journeys and operational system workflows."""

    # =========================================================================
    # WORKFLOW 1: INITIAL DATA LOADING & HEALTH FLOW
    # =========================================================================

    def test_workflow_initial_data_loading(self):
        """Simulate client initial load: check stats, fetch catalog, verify categories."""
        # Step 1: Health check via stats endpoint
        status_stats, stats, _ = fetch_api("/api/stats")
        self.assertEqual(status_stats, 200, "Initial stats health check failed")
        self.assertGreaterEqual(stats.get("total", 0), 31, "Catalog count indicates incomplete data")

        # Step 2: Fetch primary catalog items
        status_catalog, catalog, _ = fetch_api("/api/curiositats")
        self.assertEqual(status_catalog, 200, "Primary catalog fetch failed")
        self.assertEqual(len(catalog), stats["total"], "Catalog length differs from stats total")

        # Step 3: Validate representation of all five catalog categories
        observed_categories = {it.get("type") for it in catalog}
        expected_categories = {"words", "fauna", "flora", "businesses", "history"}
        self.assertEqual(
            observed_categories,
            expected_categories,
            f"Catalog is missing representation for categories: {expected_categories - observed_categories}"
        )

    # =========================================================================
    # WORKFLOW 2: CATALOG BROWSING & DISCOVERY FLOW
    # =========================================================================

    def test_workflow_catalog_browsing_simulation(self):
        """Simulate realistic user browsing journey across categories, searches, and detail items."""
        # 1. User arrives on full catalog
        _, catalog, _ = fetch_api("/api/curiositats")
        self.assertGreaterEqual(len(catalog), 31)

        # 2. User switches to Flora filter pill
        _, flora_items, _ = fetch_api("/api/curiositats", {"category": "flora"})
        self.assertEqual(len(flora_items), 5, "Flora category must yield exactly 5 items")
        for it in flora_items:
            self.assertEqual(it["type"], "flora")

        # 3. User searches for endemic species
        _, search_results, _ = fetch_api("/api/curiositats", {"category": "flora", "search": "balear"})
        self.assertGreaterEqual(len(search_results), 1, "Flora search for 'balear' must return matching species")
        item = search_results[0]

        # 4. User opens detail card for item
        self.assertIn("title", item)
        self.assertIn("definition", item)
        self.assertIn("source_reference", item)
        self.assertIsNotNone(item["source_reference"])

        # 5. User pivots to History category and filters by period
        _, history_items, _ = fetch_api("/api/curiositats", {"category": "history"})
        self.assertEqual(len(history_items), 6, "History category must yield exactly 6 items")
        titles = [h["title"] for h in history_items]
        self.assertTrue(any("Revolta" in t or "Conquesta" in t or "Talaiòtica" in t for t in titles))

    # =========================================================================
    # WORKFLOW 3: SPOTLIGHT RANDOM CURIOSITY RETRIEVAL ("UNA A LA SORT")
    # =========================================================================

    def test_workflow_random_curiosity_exploration(self):
        """Simulate user clicking 'Treu-ne una altra a la sort' repeatedly."""
        seen_ids = set()
        seen_types = set()
        iterations = 15

        for i in range(iterations):
            status, item, _ = fetch_api("/api/random")
            self.assertEqual(status, 200, f"Random query iteration {i+1} failed")
            self.assertIsInstance(item, dict)
            self.assertIn("id", item)
            self.assertIn("title", item)
            self.assertIn("type", item)
            self.assertIn("definition", item)

            seen_ids.add(item["id"])
            seen_types.add(item["type"])

        # Verifies random distribution (must observe diversity, not a static mock)
        self.assertGreater(
            len(seen_ids),
            1,
            f"Random endpoint returned identical item {seen_ids} across {iterations} queries"
        )
        self.assertGreaterEqual(
            len(seen_types),
            2,
            f"Expected at least 2 distinct categories across {iterations} random requests, got: {seen_types}"
        )

    # =========================================================================
    # WORKFLOW 4: STATIC CDN OFFLINE FALLBACK PARITY SIMULATION
    # =========================================================================

    def test_workflow_offline_fallback_simulation(self):
        """Simulate client-side filtering on FALLBACK_DATA, mimicking Firebase static hosting."""
        fallback_data = extract_fallback_data()
        self.assertGreater(len(fallback_data), 0, "No FALLBACK_DATA found in web/app.js")

        # Simulate client-side search for 'sobrassada' in fallback data
        keyword = "sobrassada"
        matching_fallback = []
        for it in fallback_data:
            corpus = f"{it.get('title', '')} {it.get('subtitle', '')} {it.get('tag', '')} {it.get('definition', '')}".lower()
            if keyword in corpus:
                matching_fallback.append(it)

        # Execute equivalent search via API server
        status, api_matches, _ = fetch_api("/api/curiositats", {"search": keyword})
        self.assertEqual(status, 200)

        # Both must find the Porc Negre entry
        self.assertGreaterEqual(len(matching_fallback), 1, "Fallback search must locate Porc Negre entry")
        self.assertGreaterEqual(len(api_matches), 1, "API search must locate Porc Negre entry")

        fb_titles = {x["title"] for x in matching_fallback}
        api_titles = {x["title"] for x in api_matches}
        self.assertTrue(
            "Porc Negre Mallorquí" in fb_titles or any("Porc" in t for t in fb_titles),
            f"Expected Porc Negre in fallback results: {fb_titles}"
        )
        self.assertTrue(
            "Porc Negre Mallorquí" in api_titles or any("Porc" in t for t in api_titles),
            f"Expected Porc Negre in API results: {api_titles}"
        )

    # =========================================================================
    # WORKFLOW 5: DATABASE INITIALIZATION & ZERO-STATE RECOVERY FLOW
    # =========================================================================

    def test_workflow_database_initialization_dry_run(self):
        """Execute scripts/importers/init_db.py --check to verify clean validation."""
        self.assertTrue(INIT_DB_SCRIPT.exists(), "scripts/importers/init_db.py not found")

        cmd = [sys.executable, str(INIT_DB_SCRIPT), "--check"]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(PROJECT_ROOT))
        self.assertEqual(
            res.returncode,
            0,
            f"init_db.py --check failed with code {res.returncode}.\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}"
        )
        self.assertIn("31 registres catalogats", res.stdout.lower())

    def test_workflow_database_regeneration_to_temp_file(self):
        """Verify init_db.py can build a fresh database from scratch into an empty path."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_db_path = Path(tmp.name)

        try:
            cmd = [
                sys.executable,
                str(INIT_DB_SCRIPT),
                "--db", str(tmp_db_path),
                "--schema", str(SCHEMA_PATH),
                "--seed", str(SEED_PATH),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(PROJECT_ROOT))
            self.assertEqual(
                res.returncode,
                0,
                f"Fresh DB regeneration failed with exit code {res.returncode}.\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}"
            )

            # Connect and verify newly generated database
            conn = get_db_connection()
            # Verify temp db
            import sqlite3
            tmp_conn = sqlite3.connect(tmp_db_path)
            c = tmp_conn.cursor()
            c.execute("SELECT COUNT(*) FROM words")
            w_count = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM fauna")
            fa_count = c.fetchone()[0]
            tmp_conn.close()
            conn.close()

            self.assertEqual(w_count, 8, "Fresh DB words count must be 8")
            self.assertEqual(fa_count, 7, "Fresh DB fauna count must be 7")

        finally:
            if tmp_db_path.exists():
                try:
                    tmp_db_path.unlink()
                except Exception:
                    pass

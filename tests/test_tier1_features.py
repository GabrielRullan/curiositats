"""Tier 1: Feature Coverage Tests for 'Una teringa de curiositats'.

Covers all core requirements (R1 - R5):
- R1: Database integrity and API endpoints (/api/curiositats, /api/random, /api/stats)
- R2: Project creation documentation (README.md, docs/ARCHITECTURE.md, docs/SOURCES.md)
- R3: AI reference addition skill (skills/afegir-referencies/SKILL.md)
- R4: OpenAPI specification & Swagger UI
- R5: Contact section, Cookie-free privacy notice, and Git configuration
"""

import json
from pathlib import Path
import re
import sqlite3

from tests.base import (
    DB_PATH,
    DOCS_DIR,
    PROJECT_ROOT,
    SCHEMA_PATH,
    SEED_PATH,
    SKILLS_DIR,
    SOURCES_PATH,
    TeringaTestCase,
    WEB_DIR,
    fetch_api,
    get_db_connection,
    is_m1_ready,
    is_m2_ready,
    is_m3_ready,
    is_m4_ready,
    is_m5_ready,
    milestone_requirement,
)


class TestTier1FeatureCoverage(TeringaTestCase):
    """Tier 1: Explicit feature coverage across R1 - R5 specifications."""

    # =========================================================================
    # R1: DATA INTEGRITY & DATABASE SCHEMA
    # =========================================================================

    def test_r1_database_file_exists_and_valid(self):
        """Verify curiositats.db exists and is an operable SQLite 3 database."""
        self.assertTrue(DB_PATH.exists(), f"Database file not found at {DB_PATH}")
        self.assertGreater(DB_PATH.stat().st_size, 0, "Database file is empty")

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("PRAGMA integrity_check")
        row = c.fetchone()
        conn.close()
        self.assertEqual(row[0], "ok", f"SQLite integrity check failed: {row[0]}")

    def test_r1_database_tables_exist(self):
        """Verify all 5 domain tables exist in curiositats.db."""
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {r[0] for r in c.fetchall()}
        conn.close()

        expected_tables = {"words", "fauna", "flora", "emblematic_businesses", "historical_events"}
        self.assertTrue(
            expected_tables.issubset(tables),
            f"Missing required tables in DB: {expected_tables - tables}"
        )

    def test_r1_database_record_counts(self):
        """Verify database contains clean catalog counts (minimum 31 items)."""
        conn = get_db_connection()
        c = conn.cursor()
        counts = {}
        for table in ["words", "fauna", "flora", "emblematic_businesses", "historical_events"]:
            c.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = c.fetchone()[0]
        conn.close()

        self.assertGreaterEqual(counts["words"], 8, "Expected at least 8 words in database")
        self.assertEqual(counts["fauna"], 7, "Expected exactly 7 fauna entries")
        self.assertEqual(counts["flora"], 5, "Expected exactly 5 flora entries")
        self.assertEqual(counts["emblematic_businesses"], 5, "Expected exactly 5 emblematic businesses")
        self.assertEqual(counts["historical_events"], 6, "Expected exactly 6 historical events")

        total = sum(counts.values())
        self.assertGreaterEqual(total, 31, f"Total catalog records ({total}) must be >= 31")

    def test_r1_seed_data_counts(self):
        """Verify seed_data.json matches canonical 31 records specification."""
        self.assertTrue(SEED_PATH.exists(), "database/seed_data.json not found")
        with open(SEED_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(len(data.get("words", [])), 8, "seed_data.json words count must be 8")
        self.assertEqual(len(data.get("fauna", [])), 7, "seed_data.json fauna count must be 7")
        self.assertEqual(len(data.get("flora", [])), 5, "seed_data.json flora count must be 5")
        self.assertEqual(len(data.get("emblematic_businesses", [])), 5, "seed_data.json businesses count must be 5")
        self.assertEqual(len(data.get("historical_events", [])), 6, "seed_data.json historical events count must be 6")

        total_seed = sum(len(data[k]) for k in ["words", "fauna", "flora", "emblematic_businesses", "historical_events"])
        self.assertEqual(total_seed, 31, "Total seed records must be exactly 31")

    def test_r1_no_null_or_empty_critical_fields(self):
        """Verify no critical columns contain NULL or empty strings in curiositats.db."""
        conn = get_db_connection()
        c = conn.cursor()
        checks = [
            ("words", "term IS NULL OR TRIM(term) = '' OR definition IS NULL OR TRIM(definition) = ''"),
            ("fauna", "common_name_ca IS NULL OR TRIM(common_name_ca) = '' OR description IS NULL OR TRIM(description) = ''"),
            ("flora", "common_name_ca IS NULL OR TRIM(common_name_ca) = '' OR scientific_name IS NULL OR TRIM(scientific_name) = ''"),
            ("emblematic_businesses", "name IS NULL OR TRIM(name) = '' OR municipality IS NULL OR history_summary IS NULL"),
            ("historical_events", "title IS NULL OR TRIM(title) = '' OR year_start IS NULL OR summary IS NULL"),
        ]

        for table, condition in checks:
            c.execute(f"SELECT COUNT(*) FROM {table} WHERE {condition}")
            bad_count = c.fetchone()[0]
            self.assertEqual(bad_count, 0, f"Table '{table}' has {bad_count} rows with invalid/null critical fields")
        conn.close()

    @milestone_requirement("M1", is_m1_ready, "Data homogenization for Ca de Bou")
    def test_r1_ca_de_bou_homogenization(self):
        """Verify Ca de Bou entry is cleaned of English gloss '(Mallorquin Mastiff)'."""
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT common_name_ca FROM fauna WHERE common_name_ca LIKE '%Ca de Bou%'")
        rows = c.fetchall()
        conn.close()

        self.assertGreaterEqual(len(rows), 1, "Ca de Bou not found in fauna table")
        for row in rows:
            name = row[0]
            self.assertEqual(name, "Ca de Bou", f"Fauna common_name_ca contains uncleaned text: '{name}'")
            self.assertNotIn("Mallorquin Mastiff", name, "English translation must be removed")

    @milestone_requirement("M1", is_m1_ready, "Normalization of group_type")
    def test_r1_group_type_normalization(self):
        """Verify domestic breeds have normalized Catalan group_type instead of raw 'raca_domestica'."""
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT common_name_ca, group_type FROM fauna WHERE group_type = 'raca_domestica'")
        unnormalized = c.fetchall()
        conn.close()

        self.assertEqual(
            len(unnormalized),
            0,
            f"Found raw unnormalized 'raca_domestica' in fauna: {unnormalized}"
        )

    # =========================================================================
    # R1: REST API ENDPOINTS (/api/curiositats, /api/random, /api/stats)
    # =========================================================================

    def test_r1_api_curiositats_unfiltered(self):
        """Verify GET /api/curiositats returns 200 OK, JSON list, and unified schema."""
        status, data, headers = fetch_api("/api/curiositats")
        self.assertEqual(status, 200, f"Expected HTTP 200 from /api/curiositats, got {status}")
        self.assertIn("application/json", headers.get("Content-Type", ""))
        self.assertIsInstance(data, list, "API response must be a JSON array")
        self.assertGreaterEqual(len(data), 31, "Unfiltered /api/curiositats must return >= 31 items")

        for item in data[:10]:
            self.assertUnifiedCuriositatItem(item)

    def test_r1_api_curiositats_category_filtering(self):
        """Verify GET /api/curiositats?category=<cat> filters accurately for each category."""
        categories = {
            "words": 8,
            "fauna": 7,
            "flora": 5,
            "businesses": 5,
            "history": 6,
        }

        for cat, expected_min_count in categories.items():
            status, items, _ = fetch_api("/api/curiositats", {"category": cat})
            self.assertEqual(status, 200, f"Failed GET /api/curiositats?category={cat}")
            self.assertIsInstance(items, list)
            self.assertGreaterEqual(
                len(items),
                expected_min_count,
                f"Expected >= {expected_min_count} items for category '{cat}', got {len(items)}"
            )
            for it in items:
                self.assertEqual(it["type"], cat, f"Item type '{it['type']}' does not match requested category '{cat}'")

    def test_r1_api_random(self):
        """Verify GET /api/random returns 200 OK and a single curiosity item."""
        status, item, headers = fetch_api("/api/random")
        self.assertEqual(status, 200, f"Expected HTTP 200 from /api/random, got {status}")
        self.assertIn("application/json", headers.get("Content-Type", ""))
        self.assertIsInstance(item, dict, "API /api/random must return a JSON object")
        self.assertUnifiedCuriositatItem(item)

    def test_r1_api_stats(self):
        """Verify GET /api/stats returns 200 OK, category breakdown, and total count."""
        status, stats, headers = fetch_api("/api/stats")
        self.assertEqual(status, 200, f"Expected HTTP 200 from /api/stats, got {status}")
        self.assertIn("application/json", headers.get("Content-Type", ""))
        self.assertIsInstance(stats, dict, "API /api/stats must return a JSON object")

        for key in ["words", "fauna", "flora", "businesses", "history", "total"]:
            self.assertIn(key, stats, f"Missing key '{key}' in /api/stats response")
            self.assertIsInstance(stats[key], int, f"Stats value for '{key}' must be integer")

        sum_categories = (
            stats["words"] + stats["fauna"] + stats["flora"] + stats["businesses"] + stats["history"]
        )
        self.assertEqual(
            stats["total"],
            sum_categories,
            f"Stats total ({stats['total']}) must equal sum of categories ({sum_categories})"
        )
        self.assertGreaterEqual(stats["total"], 31, "Total count must be >= 31")

    # =========================================================================
    # R2: CREATION DOCUMENTATION
    # =========================================================================

    def test_r2_readme_documentation_exists(self):
        """Verify README.md exists and describes the project architecture and philosophy."""
        readme = PROJECT_ROOT / "README.md"
        self.assertTrue(readme.exists(), "README.md not found at project root")
        content = readme.read_text(encoding="utf-8")
        self.assertGreater(len(content), 200, "README.md content is too brief")
        self.assertIn("Una teringa de curiositats", content)

    @milestone_requirement("M2", is_m2_ready, "docs/ARCHITECTURE.md update reflecting Python http.server")
    def test_r2_architecture_documentation_accurate(self):
        """Verify docs/ARCHITECTURE.md reflects Python http.server instead of FastAPI."""
        arch = DOCS_DIR / "ARCHITECTURE.md"
        self.assertTrue(arch.exists(), "docs/ARCHITECTURE.md not found")
        content = arch.read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", content, "ARCHITECTURE.md must not reference FastAPI as current backend")
        self.assertTrue(
            "http.server" in content or "Python 3" in content,
            "ARCHITECTURE.md must document standard library Python backend"
        )

    def test_r2_sources_documentation_exists(self):
        """Verify docs/SOURCES.md exists and documents catalog references."""
        sources = DOCS_DIR / "SOURCES.md"
        self.assertTrue(sources.exists(), "docs/SOURCES.md not found")
        content = sources.read_text(encoding="utf-8")
        self.assertGreater(len(content), 500, "docs/SOURCES.md content is too brief")

    # =========================================================================
    # R3: AI REFERENCE SKILL
    # =========================================================================

    @milestone_requirement("M3", is_m3_ready, "skills/afegir-referencies/SKILL.md existence and format")
    def test_r3_skill_file_structure_and_frontmatter(self):
        """Verify skills/afegir-referencies/SKILL.md exists with valid YAML frontmatter."""
        skill_file = SKILLS_DIR / "afegir-referencies" / "SKILL.md"
        self.assertTrue(skill_file.exists(), f"Skill file not found at {skill_file}")

        content = skill_file.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("---"), "SKILL.md must start with YAML frontmatter delimiter (---)")
        parts = content.split("---", 2)
        self.assertGreaterEqual(len(parts), 3, "SKILL.md must contain YAML frontmatter section")

        frontmatter = parts[1]
        self.assertIn("name:", frontmatter, "Frontmatter must contain 'name' field")
        self.assertIn("afegir-referencies", frontmatter, "Frontmatter name must be 'afegir-referencies'")
        self.assertIn("description:", frontmatter, "Frontmatter must contain 'description' field")

        body = parts[2]
        self.assertIn("Criteris", body, "SKILL.md must define quality/acceptance criteria")
        self.assertIn("Procediment", body, "SKILL.md must define the addition procedure")

    # =========================================================================
    # R4: OPENAPI SPECIFICATION & SWAGGER UI
    # =========================================================================

    @milestone_requirement("M4", is_m4_ready, "OpenAPI specification in web/openapi.json")
    def test_r4_openapi_json_specification(self):
        """Verify web/openapi.json exists, is valid JSON, and defines core endpoints."""
        openapi_file = WEB_DIR / "openapi.json"
        self.assertTrue(openapi_file.exists(), "web/openapi.json not found")

        with open(openapi_file, "r", encoding="utf-8") as f:
            spec = json.load(f)

        self.assertIn("openapi", spec, "Spec must have 'openapi' version field")
        self.assertIn("paths", spec, "Spec must define 'paths'")
        paths = spec["paths"]
        self.assertIn("/api/curiositats", paths, "Spec missing /api/curiositats path")
        self.assertIn("/api/random", paths, "Spec missing /api/random path")
        self.assertIn("/api/stats", paths, "Spec missing /api/stats path")

    @milestone_requirement("M4", is_m4_ready, "Swagger UI interactive interface")
    def test_r4_swagger_ui_html_exists(self):
        """Verify web/swagger/index.html exists and embeds Swagger UI bundle."""
        swagger_file = WEB_DIR / "swagger" / "index.html"
        self.assertTrue(swagger_file.exists(), "web/swagger/index.html not found")
        content = swagger_file.read_text(encoding="utf-8")
        self.assertIn("swagger-ui", content.lower(), "Swagger UI HTML must reference swagger-ui bundle or CDN")

    @milestone_requirement("M4", is_m4_ready, "Server routing for Swagger UI and OpenAPI")
    def test_r4_server_serves_swagger_ui(self):
        """Verify server serves Swagger UI and openapi spec without 404."""
        status_swagger, _, _ = fetch_api("/swagger/")
        status_openapi, _, _ = fetch_api("/openapi.json")
        self.assertIn(status_swagger, (200, 301, 302), "GET /swagger/ must succeed or redirect")
        self.assertEqual(status_openapi, 200, "GET /openapi.json must return 200 OK")

    # =========================================================================
    # R5: CONTACT, PRIVACY & GIT CONFIGURATION
    # =========================================================================

    @milestone_requirement("M5", is_m5_ready, "Contact and cookie-free privacy notice in web/index.html")
    def test_r5_web_contact_and_privacy_notice(self):
        """Verify web/index.html includes contact information and cookie-free privacy notice."""
        index_html = WEB_DIR / "index.html"
        self.assertTrue(index_html.exists(), "web/index.html not found")
        content = index_html.read_text(encoding="utf-8").lower()

        # Contact check
        has_contact = "contact" in content or "contacte" in content or "mailto:" in content
        self.assertTrue(has_contact, "web/index.html must contain a contact section or link")

        # Cookie-free privacy notice check
        has_privacy = "privadesa" in content or "sense cookies" in content or "no utilitza cookies" in content
        self.assertTrue(has_privacy, "web/index.html must contain cookie-free privacy notice")

    @milestone_requirement("M5", is_m5_ready, "Git configuration files (.gitignore, LICENSE)")
    def test_r5_git_configuration_files(self):
        """Verify .gitignore and LICENSE files exist at project root."""
        gitignore = PROJECT_ROOT / ".gitignore"
        license_file = PROJECT_ROOT / "LICENSE"
        self.assertTrue(gitignore.exists(), ".gitignore file must exist at project root")
        self.assertTrue(license_file.exists(), "LICENSE file must exist at project root")

        gitignore_content = gitignore.read_text(encoding="utf-8")
        self.assertIn(".agents", gitignore_content, ".gitignore should ignore .agents directory")

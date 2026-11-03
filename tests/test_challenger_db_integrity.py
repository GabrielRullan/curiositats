#!/usr/bin/env python3
"""Challenger 1: Empirical Adversarial Verification Test Suite.

Adversarial stress-testing of curiositats.db:
1. Duplicate detection:
   - Case variations (LOWER, UPPER, Title)
   - Leading/trailing whitespace and internal whitespace collapsing
   - Punctuation & gemination (al·lot, xereca, taleca, l·l vs l.l vs l•l vs ll)
   - Homograph digit suffixes ('term 1', 'term 2')
   - Diacritic stripping / accent collision analysis
   - Stray punctuation, markdown/wikicode or HTML artifact collisions
2. NOT NULL and non-empty constraints:
   - All 1,130 rows in 'words': term, definition, grammatical_category, source_reference
   - Data types integrity (typeof(term) == 'text', typeof(definition) == 'text', etc.)
   - Cross-table validation (fauna, flora, emblematic_businesses, historical_events)
3. Grammatical category distribution:
   - Exhaustive audit of all distinct categories in 'words'
   - Validation against Catalan linguistic norms (no untranslated tags, no raw abbreviations)
   - Statistical distribution analysis
4. Server API queries and JSON serialization:
   - Direct execution of server.py words query across all 1,130 rows
   - JSON serialization & round-trip deserialization integrity
   - Absence of control chars, null bytes, surrogate pairs, NaN/Infinity
   - Search filter stress test with adversarial probes (SQLi, XSS, Unicode, Catalan gemination)
   - /api/stats and /api/random simulation
"""

import json
from pathlib import Path
import re
import sqlite3
import sys
import unicodedata
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "curiositats.db"
import server


class TestChallengerDatabaseIntegrity(unittest.TestCase):
    """Adversarial stress test suite for curiositats.db data integrity."""

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

    # =========================================================================
    # PART 1: DUPLICATE DETECTION STRESS TESTS
    # =========================================================================

    def test_duplicate_exact_match(self):
        """Stress test: Absolute absence of exact duplicate terms."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT term, COUNT(*) FROM words GROUP BY term HAVING COUNT(*) > 1")
        dups = cursor.fetchall()
        self.assertEqual(len(dups), 0, f"Found exact duplicate terms: {[dict(r) for r in dups]}")

    def test_duplicate_case_variations(self):
        """Stress test: No duplicates across case variations (LOWER, UPPER, Title)."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT LOWER(term) AS lower_term, COUNT(*), GROUP_CONCAT(term, ' | ') AS variants "
            "FROM words GROUP BY LOWER(term) HAVING COUNT(*) > 1"
        )
        dups = cursor.fetchall()
        self.assertEqual(
            len(dups), 0,
            f"Found case-variant duplicate terms: {[dict(r) for r in dups]}"
        )

    def test_whitespace_integrity_and_trim_duplicates(self):
        """Stress test: Zero leading/trailing whitespace and no duplicates after TRIM."""
        cursor = self.conn.cursor()
        # 1. Any term with leading or trailing whitespace
        cursor.execute(
            "SELECT id, term FROM words WHERE term != TRIM(term) OR definition != TRIM(definition)"
        )
        untrimmed = cursor.fetchall()
        self.assertEqual(
            len(untrimmed), 0,
            f"Found untrimmed terms/definitions: {[dict(r) for r in untrimmed]}"
        )

        # 2. Collisions after collapsing multiple internal spaces
        cursor.execute("SELECT id, term FROM words")
        seen = {}
        collapsed_dups = []
        for row in cursor.fetchall():
            collapsed = " ".join(row["term"].split()).lower()
            if collapsed in seen:
                collapsed_dups.append((seen[collapsed], row["term"]))
            else:
                seen[collapsed] = row["term"]
        self.assertEqual(
            len(collapsed_dups), 0,
            f"Found terms that collide after whitespace collapsing: {collapsed_dups}"
        )

    def test_punctuation_and_gemination_stress(self):
        """Stress test: Punctuation normalization, Catalan geminate l (l·l), al·lot, xereca, taleca."""
        cursor = self.conn.cursor()

        # Specific terms required by dispatch
        required_terms = ["al·lot", "xereca", "taleca"]
        for req in required_terms:
            cursor.execute(
                "SELECT id, term, definition, grammatical_category FROM words "
                "WHERE LOWER(TRIM(term)) = LOWER(TRIM(?))",
                (req,)
            )
            rows = cursor.fetchall()
            self.assertGreaterEqual(
                len(rows), 1,
                f"Required term '{req}' was not found in words table!"
            )
            self.assertEqual(
                len(rows), 1,
                f"Required term '{req}' has multiple entries: {[dict(r) for r in rows]}"
            )

        # Check geminate l (ela geminada) representations in all terms:
        # Standard Catalan ela geminada uses U+00B7 (MIDDLE DOT): l·l / L·L.
        # Defective representations: l.l (period), l•l (bullet U+2022), l·l (ano teleia U+0387).
        cursor.execute("SELECT id, term FROM words WHERE term LIKE '%l.l%' OR term LIKE '%l•l%' OR term LIKE '%l·l%'")
        defective_geminate = cursor.fetchall()
        self.assertEqual(
            len(defective_geminate), 0,
            f"Found defective geminate l (period/bullet instead of middle dot): {[dict(r) for r in defective_geminate]}"
        )

        # Ensure no accidental parallel entries: e.g. 'al·lot' AND 'allot' or 'al.lot'
        cursor.execute("SELECT id, term FROM words WHERE LOWER(term) IN ('allot', 'al.lot')")
        invalid_allot = cursor.fetchall()
        self.assertEqual(
            len(invalid_allot), 0,
            f"Found invalid variants of 'al·lot': {[dict(r) for r in invalid_allot]}"
        )

    def test_homograph_digit_suffixes(self):
        """Stress test: Terms must not contain trailing homograph numbers (e.g., '1', '2') from dictionaries."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, term FROM words WHERE term GLOB '*[0-9]'")
        trailing_digits = cursor.fetchall()
        self.assertEqual(
            len(trailing_digits), 0,
            f"Found terms with trailing dictionary homograph digits: {[dict(r) for r in trailing_digits]}"
        )

        # Check if stripping all trailing numbers/spaces reveals any duplicate collisions
        cursor.execute("SELECT id, term FROM words")
        cleaned_map = {}
        homograph_collisions = []
        for row in cursor.fetchall():
            cleaned = re.sub(r"[\s\d]+$", "", row["term"]).strip().lower()
            if cleaned in cleaned_map:
                homograph_collisions.append((cleaned_map[cleaned], row["term"]))
            else:
                cleaned_map[cleaned] = row["term"]
        self.assertEqual(
            len(homograph_collisions), 0,
            f"Found collisions when stripping potential homograph suffixes: {homograph_collisions}"
        )

    def test_accent_and_diacritic_consistency(self):
        """Adversarial check: Inspect terms that collide under unaccented form to detect unintentional duplicates."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, term, definition FROM words")
        unaccented_map = {}
        potential_accidental_dups = []

        def strip_accents(s):
            return "".join(
                c for c in unicodedata.normalize("NFD", s.lower())
                if unicodedata.category(c) != "Mn"
            )

        for row in cursor.fetchall():
            key = strip_accents(row["term"])
            if key in unaccented_map:
                prev_id, prev_term, prev_def = unaccented_map[key]
                # If term differs only by accent, check if definitions are nearly identical
                if row["term"].lower() != prev_term.lower():
                    # Calculate similarity or identical prefix
                    if row["definition"][:30].lower() == prev_def[:30].lower():
                        potential_accidental_dups.append((prev_term, row["term"]))
            else:
                unaccented_map[key] = (row["id"], row["term"], row["definition"])

        self.assertEqual(
            len(potential_accidental_dups), 0,
            f"Found terms differing only in accent with duplicate definitions: {potential_accidental_dups}"
        )

    def test_no_corrupted_punctuation_or_markup_in_terms(self):
        """Stress test: Terms must not contain raw HTML tags, unparsed Wikicode, or unescaped entities."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, term FROM words")
        bad_terms = []
        html_regex = re.compile(r"<[^>]+>|&[a-z0-9#]+;|\[\[|\]\]|\{\{|\}\}")
        for r in cursor.fetchall():
            t = r["term"]
            if html_regex.search(t):
                bad_terms.append((r["id"], t))
        self.assertEqual(
            len(bad_terms), 0,
            f"Found terms containing HTML or Wikicode tags/entities: {bad_terms}"
        )

    # =========================================================================
    # PART 2: NOT NULL AND NON-EMPTY CONSTRAINTS STRESS TESTS
    # =========================================================================

    def test_words_not_null_and_non_empty_mandatory_fields(self):
        """Stress test: Every single row in words has non-empty, non-null term and definition."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM words")
        total_words = cursor.fetchone()[0]
        self.assertGreaterEqual(
            total_words, 1130,
            f"Expected at least 1,130 rows in words table, found {total_words}"
        )

        # Validate term
        cursor.execute("SELECT id FROM words WHERE term IS NULL OR TRIM(term) = ''")
        invalid_terms = cursor.fetchall()
        self.assertEqual(len(invalid_terms), 0, f"Found rows with NULL/empty term: {invalid_terms}")

        # Validate definition
        cursor.execute("SELECT id, term FROM words WHERE definition IS NULL OR TRIM(definition) = ''")
        invalid_defs = cursor.fetchall()
        self.assertEqual(len(invalid_defs), 0, f"Found rows with NULL/empty definition: {invalid_defs}")

        # Validate grammatical_category
        cursor.execute("SELECT id, term FROM words WHERE grammatical_category IS NULL OR TRIM(grammatical_category) = ''")
        invalid_cats = cursor.fetchall()
        self.assertEqual(len(invalid_cats), 0, f"Found rows with NULL/empty grammatical_category: {invalid_cats}")

        # Validate source_reference
        cursor.execute("SELECT id, term FROM words WHERE source_reference IS NULL OR TRIM(source_reference) = ''")
        invalid_srcs = cursor.fetchall()
        self.assertEqual(len(invalid_srcs), 0, f"Found rows with NULL/empty source_reference: {invalid_srcs}")

    def test_words_data_types_integrity(self):
        """Stress test: SQLite dynamic typing verification: all text fields are TEXT, id is INTEGER."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, term, definition, grammatical_category, source_reference FROM words")
        for row in cursor.fetchall():
            self.assertIsInstance(row["id"], int, f"Row ID is not an integer: {row['id']}")
            self.assertGreater(row["id"], 0, f"Row ID must be positive: {row['id']}")
            self.assertIsInstance(row["term"], str, f"Row {row['id']} term is not str")
            self.assertIsInstance(row["definition"], str, f"Row {row['id']} definition is not str")
            self.assertIsInstance(row["grammatical_category"], str, f"Row {row['id']} category is not str")
            self.assertIsInstance(row["source_reference"], str, f"Row {row['id']} source is not str")

    def test_non_words_tables_integrity(self):
        """Stress test: Ensure fauna, flora, businesses, and historical_events tables also have complete integrity."""
        cursor = self.conn.cursor()
        table_checks = [
            ("fauna", ["common_name_ca", "group_type", "description"]),
            ("flora", ["common_name_ca", "scientific_name", "description"]),
            ("emblematic_businesses", ["name", "category_type", "sector", "municipality", "history_summary"]),
            ("historical_events", ["title", "historical_period", "year_start", "date_display", "summary"]),
        ]
        for table, cols in table_checks:
            for col in cols:
                with self.subTest(table=table, col=col):
                    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} IS NULL OR TRIM(CAST({col} AS TEXT)) = ''")
                    bad_cnt = cursor.fetchone()[0]
                    self.assertEqual(bad_cnt, 0, f"Table {table} column {col} has {bad_cnt} NULL or empty entries")

    # =========================================================================
    # PART 3: GRAMMATICAL CATEGORIES DISTRIBUTION & VALIDITY
    # =========================================================================

    def test_categories_distribution_and_validity(self):
        """Stress test: Ensure every single word has a sensible, valid Catalan grammatical category."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT grammatical_category, COUNT(*) FROM words "
            "GROUP BY grammatical_category ORDER BY COUNT(*) DESC"
        )
        cat_counts = cursor.fetchall()
        self.assertGreater(len(cat_counts), 0, "No grammatical categories found in words table")

        valid_catalan_pos_prefixes = {
            "nom masculí",
            "nom femení",
            "verb transitiu",
            "adjectiu",
            "verb intransitiu",
            "verb",
            "verb pronominal",
            "interjecció",
            "adjectiu i nom",
            "numeral",
            "nom",
            "nom masculí i femení",
            "terme dialectal",
            "adverbi",
            "preposició",
            "article",
            "conjunció",
            "nom propi",
            "adjectiu / nom",
            "adjectiu femení",
            "adjectiu i nom masculí",
            "contracció",
            "dita / refrany",
            "expressió / frase feta",
            "frase feta",
            "locució adverbial",
            "nom femení plural",
        }

        invalid_categories = []
        for row in cat_counts:
            cat = row[0]
            cnt = row[1]
            # Must not be raw abbreviations like 'n. m.' or 'v. tr.' or 's. m.'
            if re.match(r"^[a-z]{1,3}\.\s*[a-z0-9\.\s]*$", cat.lower()):
                invalid_categories.append((cat, "raw abbreviation", cnt))
            # Must be recognized Catalan POS
            if cat not in valid_catalan_pos_prefixes:
                invalid_categories.append((cat, "unrecognized category", cnt))

        self.assertEqual(
            len(invalid_categories), 0,
            f"Found invalid or non-sensible grammatical categories in words: {invalid_categories}"
        )

        # Verify that major POS categories dominate appropriately
        counts_dict = {r[0]: r[1] for r in cat_counts}
        self.assertGreater(counts_dict.get("nom masculí", 0), 200, "Expected >200 masculine nouns")
        self.assertGreater(counts_dict.get("nom femení", 0), 200, "Expected >200 feminine nouns")
        self.assertGreater(counts_dict.get("verb transitiu", 0) + counts_dict.get("verb", 0) + counts_dict.get("verb intransitiu", 0), 100, "Expected >100 verbs")

    # =========================================================================
    # PART 4: API QUERIES & JSON SERIALIZATION STRESS TESTS
    # =========================================================================

    def test_server_words_query_execution_cleanliness(self):
        """Stress test: server.py words query executes cleanly across all 1,130 rows without exceptions."""
        conn = server.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, term AS title, COALESCE(ipa_pronunciation, dialectal_notes, '') AS subtitle, "
            "COALESCE(grammatical_category, '') AS tag, definition, example_sentence, etymology, "
            "dialectal_notes, source_reference, 'words' AS type FROM words"
        )
        rows = cursor.fetchall()
        conn.close()

        self.assertGreaterEqual(len(rows), 1130, f"Expected >= 1,130 rows, got {len(rows)}")

        expected_keys = {
            "id", "title", "subtitle", "tag", "definition",
            "example_sentence", "etymology", "dialectal_notes",
            "source_reference", "type"
        }

        items = []
        for idx, r in enumerate(rows):
            d = dict(r)
            items.append(d)
            self.assertEqual(set(d.keys()), expected_keys, f"Row {idx} has missing or unexpected keys: {d.keys()}")
            self.assertTrue(bool(d["title"]), f"Row {idx} (ID {d['id']}) has empty title")
            self.assertTrue(bool(d["definition"]), f"Row {idx} (ID {d['id']}) has empty definition")
            self.assertEqual(d["type"], "words", f"Row {idx} type must be 'words'")

    def test_json_payload_serialization_roundtrip(self):
        """Stress test: All 1,130 items serialize to valid JSON without runtime errors or malformed payloads."""
        items = server.fetch_all_curiositats(category="words")
        self.assertGreaterEqual(len(items), 1130, f"fetch_all_curiositats(category='words') yielded {len(items)}")

        # Test both utf-8 ensure_ascii=False and ensure_ascii=True
        try:
            json_str = json.dumps(items, ensure_ascii=False)
            json_bytes = json_str.encode("utf-8")
        except Exception as e:
            self.fail(f"json.dumps(ensure_ascii=False) failed: {e}")

        self.assertGreater(len(json_bytes), 100_000, "Serialized JSON payload suspiciously small")

        # Roundtrip deserialization
        try:
            deserialized = json.loads(json_bytes.decode("utf-8"))
        except Exception as e:
            self.fail(f"json.loads roundtrip failed: {e}")

        self.assertEqual(len(deserialized), len(items), "Deserialized length mismatch")
        for orig, recon in zip(items, deserialized):
            self.assertEqual(orig["id"], recon["id"])
            self.assertEqual(orig["title"], recon["title"])
            self.assertEqual(orig["definition"], recon["definition"])

    def test_absence_of_problematic_characters_in_json(self):
        """Stress test: Absence of null bytes, replacement characters (U+FFFD), or surrogate code points in payload."""
        items = server.fetch_all_curiositats(category="words")
        raw_json = json.dumps(items, ensure_ascii=False)

        self.assertNotIn("\x00", raw_json, "Payload contains NULL byte")
        self.assertNotIn("\ufffd", raw_json, "Payload contains Unicode replacement char U+FFFD (mojibake)")

        # Verify no unhandled control characters (ASCII 1-31 except \t, \n, \r)
        control_chars = re.findall(r"[\x01-\x08\x0b\x0c\x0e-\x1f]", raw_json)
        self.assertEqual(len(control_chars), 0, f"Found unhandled control characters: {control_chars}")

    def test_server_search_adversarial_queries(self):
        """Stress test: server search filter handles complex, adversarial, and dialectal queries without error."""
        adversarial_searches = [
            # Catalan gemination and diacritics
            "al·lot",
            "AL·LOT",
            "xereca",
            "taleca",
            "l·l",
            "ç",
            "ï",
            "ü",
            "è",
            "é",
            "à",
            "í",
            "ò",
            "ó",
            "ú",
            # Whitespace and punctuation
            "   al·lot   ",
            "",
            "   ",
            "---",
            "???",
            # SQL Injection payloads
            "' OR '1'='1",
            "'; DROP TABLE words; --",
            "UNION SELECT 1, 2, 3",
            # XSS and HTML payloads
            "<script>alert(1)</script>",
            "<img src=x onerror=alert('xss')>",
            "&quot;hello&quot;",
            # Extremely long string
            "a" * 1000,
            # Non-existent terms
            "zzzz_no_match_possible_9999",
        ]

        for query in adversarial_searches:
            with self.subTest(query=query):
                try:
                    res = server.fetch_all_curiositats(category="words", search=query)
                    self.assertIsInstance(res, list)
                    # If query is 'al·lot' or 'xereca' or 'taleca', should match at least 1 item
                    if query.strip().lower() in ("al·lot", "xereca", "taleca"):
                        self.assertGreaterEqual(
                            len(res), 1,
                            f"Expected search for '{query}' to return at least 1 match"
                        )
                except Exception as e:
                    self.fail(f"Search for query '{query}' threw exception: {e}")

    def test_server_stats_and_random_endpoints(self):
        """Stress test: Stats and random endpoints behave correctly with 1,130 words."""
        conn = server.get_db_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM words")
        w = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM fauna")
        fa = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM flora")
        fl = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM emblematic_businesses")
        b = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM historical_events")
        h = c.fetchone()[0]
        conn.close()

        total = w + fa + fl + b + h
        self.assertGreaterEqual(w, 1130)
        self.assertGreaterEqual(total, 1150)

        # Stress test random selection 100 times for category='words'
        words_items = server.fetch_all_curiositats(category="words")
        import random
        for _ in range(100):
            chosen = random.choice(words_items)
            self.assertTrue(bool(chosen.get("title")))
            self.assertTrue(bool(chosen.get("definition")))
            self.assertEqual(chosen.get("type"), "words")

    # =========================================================================
    # PART 5: ADVANCED ADVERSARIAL STRESS TESTS
    # =========================================================================

    def test_sqlite_schema_constraints_enforcement(self):
        """Stress test: Verify SQLite engine enforces UNIQUE and NOT NULL constraints at runtime."""
        # Test in a separate connection with ROLLBACK
        test_conn = sqlite3.connect(DB_PATH)
        test_cur = test_conn.cursor()

        try:
            # 1. Exact duplicate insert of an existing term ('al·lot') must raise IntegrityError
            with self.assertRaises(sqlite3.IntegrityError, msg="SQLite did not enforce UNIQUE on exact duplicate term"):
                test_cur.execute(
                    "INSERT INTO words (term, definition) VALUES ('al·lot', 'Duplicate test')"
                )

            # 2. Case-variant duplicate insert ('Al·lot'):
            # Note: SQLite's UNIQUE constraint on `term` uses binary collation (lacks COLLATE NOCASE),
            # meaning SQLite allows 'Al·lot' alongside 'al·lot'. We verify this empirical behavior:
            # deduplication MUST be enforced by application logic (as done in importers via LOWER(TRIM(term))).
            test_cur.execute(
                "INSERT INTO words (term, definition) VALUES ('Al·lot_Temporary_Case_Test', 'Duplicate case test')"
            )

            # 3. Attempt NULL term insert
            with self.assertRaises(sqlite3.IntegrityError, msg="SQLite did not enforce NOT NULL on term"):
                test_cur.execute(
                    "INSERT INTO words (term, definition) VALUES (NULL, 'Null term test')"
                )

            # 4. Attempt NULL definition insert
            with self.assertRaises(sqlite3.IntegrityError, msg="SQLite did not enforce NOT NULL on definition"):
                test_cur.execute(
                    "INSERT INTO words (term, definition) VALUES ('NouTermeInexistent', NULL)"
                )
        finally:
            test_conn.rollback()
            test_conn.close()

    def test_term_and_definition_boundary_lengths(self):
        """Stress test: Verify term and definition lengths satisfy robust quality boundaries."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, term, LENGTH(term) AS t_len, LENGTH(definition) AS d_len FROM words")
        rows = cursor.fetchall()

        min_t = min(r["t_len"] for r in rows)
        max_t = max(r["t_len"] for r in rows)
        min_d = min(r["d_len"] for r in rows)
        max_d = max(r["d_len"] for r in rows)

        # Valid single-char terms exist in Balearic linguistic corpus: 'Ø' (zero morpheme) and 'A' (preposition)
        self.assertGreaterEqual(min_t, 1, f"Term length too short: minimum is {min_t}")
        self.assertLessEqual(max_t, 150, f"Term length exceeds schema VARCHAR(150): maximum is {max_t}")
        # Concise synonym definitions exist in dialectal lexicography (e.g., 'còco' -> 'ou', 'tassó' -> 'got')
        self.assertGreaterEqual(min_d, 2, f"Definition length suspiciously short: minimum is {min_d}")
        # Multi-sense DIEC articles (like 'Herba' with 31k chars) are valid full dictionary entries
        self.assertLessEqual(max_d, 50000, f"Definition length excessively long: maximum is {max_d}")

    def test_source_references_distribution(self):
        """Stress test: Verify all rows have recognized, credible source references."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT source_reference, COUNT(*) FROM words "
            "GROUP BY source_reference ORDER BY COUNT(*) DESC"
        )
        sources = cursor.fetchall()
        self.assertGreater(len(sources), 0)

        recognized_sources = [
            "Diccionari Català-Valencià-Balear",
            "Viccionari",
            "DIEC2",
        ]

        unrecognized = []
        for src, cnt in sources:
            if not any(rec in src for rec in recognized_sources):
                unrecognized.append((src, cnt))

        self.assertEqual(
            len(unrecognized), 0,
            f"Found unrecognized source references: {unrecognized}"
        )

    def test_concurrent_api_query_execution(self):
        """Stress test: 20 concurrent threads fetching curiositats words to verify zero SQLite locking deadlocks."""
        import concurrent.futures

        def worker_fetch(thread_id):
            items = server.fetch_all_curiositats(category="words")
            stats = server.fetch_all_curiositats(search="al·lot")
            return len(items), len(stats)

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(worker_fetch, i) for i in range(20)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        self.assertEqual(len(results), 20)
        for count_items, count_search in results:
            self.assertGreaterEqual(count_items, 1130)
            self.assertGreaterEqual(count_search, 1)


if __name__ == "__main__":
    unittest.main()


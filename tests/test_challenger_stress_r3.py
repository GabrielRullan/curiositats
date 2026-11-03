#!/usr/bin/env python3
"""Challenger 1 (Iteration 3 Gate): Empirical Stress Testing Harness.

Adversarial stress testing of:
1. /api/random stratification (uniform distribution across 5 categories, Chi-Square test).
2. Subtitle non-nullity (0 null subtitles across SQLite DB, full catalog API, and random samples).
3. HTTP 404 on invalid category parameters (adversarial inputs, SQLi, casing, special chars).
4. ThreadingHTTPServer concurrency stress testing (50, 75, 100 concurrent workers, 200+ requests).
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import math
from pathlib import Path
import random
import sqlite3
import sys
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.base import (
    DB_PATH,
    fetch_api,
    get_db_connection,
    start_test_server,
)

VALID_CATEGORIES = ("words", "fauna", "flora", "businesses", "history")


class TestApiRandomStratification(unittest.TestCase):
    """Empirical verification of /api/random stratification and uniform distribution."""

    def test_random_unconditional_stratification_distribution(self):
        """Stress-test /api/random across 1,000 requests for uniform category distribution."""
        sample_size = 1000
        category_counts = {cat: 0 for cat in VALID_CATEGORIES}
        null_subtitles = 0
        latencies = []

        print(f"\n[Stratification] Executing {sample_size} requests to /api/random...")
        for i in range(sample_size):
            t0 = time.perf_counter()
            status, item, headers = fetch_api("/api/random")
            dt = time.perf_counter() - t0
            latencies.append(dt)

            self.assertEqual(status, 200, f"Request {i+1} failed with status {status}")
            self.assertIsInstance(item, dict)
            cat = item.get("type")
            self.assertIn(cat, VALID_CATEGORIES, f"Unexpected category '{cat}'")
            category_counts[cat] += 1

            sub = item.get("subtitle")
            if sub is None:
                null_subtitles += 1

        print(f"[Stratification] Observed category counts across {sample_size} requests:")
        for cat, count in category_counts.items():
            pct = (count / sample_size) * 100
            print(f"  - {cat:12s}: {count:4d} ({pct:5.1f}%)")

        # Chi-Square Goodness-of-Fit Test
        # Null Hypothesis H0: Category distribution is uniform (20% for each of the 5 categories)
        expected_per_cat = sample_size / len(VALID_CATEGORIES)  # 200 for N=1000
        chi_square = sum((count - expected_per_cat) ** 2 / expected_per_cat for count in category_counts.values())

        # For df = 4:
        # Critical value at alpha = 0.05 is 9.488
        # Critical value at alpha = 0.01 is 13.277
        # Critical value at alpha = 0.001 is 18.467
        print(f"[Stratification] Chi-Square statistic: {chi_square:.3f} (df=4, crit_0.01=13.28, crit_0.05=9.49)")

        # Verify no category is starving (every category must be represented significantly)
        for cat, count in category_counts.items():
            self.assertGreater(
                count,
                expected_per_cat * 0.65,
                f"Category '{cat}' is severely under-represented: {count} (expected {expected_per_cat})"
            )
            self.assertLess(
                count,
                expected_per_cat * 1.35,
                f"Category '{cat}' is severely over-represented: {count} (expected {expected_per_cat})"
            )

        # Confirm Chi-Square does not reject uniformity at alpha = 0.01
        self.assertLess(
            chi_square,
            13.28,
            f"Chi-square statistic {chi_square:.3f} exceeds critical value 13.28 (rejects uniform distribution hypothesis)"
        )

        # Zero null subtitles
        self.assertEqual(null_subtitles, 0, f"Found {null_subtitles} null subtitles in /api/random sample")

    def test_random_category_specific_filtering(self):
        """Verify /api/random?category={cat} returns 100% matching category items."""
        for cat in VALID_CATEGORIES:
            with self.subTest(category=cat):
                for _ in range(25):
                    status, item, _ = fetch_api("/api/random", {"category": cat})
                    self.assertEqual(status, 200)
                    self.assertEqual(
                        item.get("type"),
                        cat,
                        f"Requested category '{cat}' but got item of type '{item.get('type')}'"
                    )

    def test_random_empty_and_whitespace_category_parameter(self):
        """Verify /api/random with empty or whitespace category defaults to stratified selection."""
        for param in ["", "   ", "\t"]:
            with self.subTest(param=repr(param)):
                status, item, _ = fetch_api("/api/random", {"category": param})
                self.assertEqual(status, 200)
                self.assertIn(item.get("type"), VALID_CATEGORIES)


class TestSubtitleNonNullity(unittest.TestCase):
    """Empirical verification that subtitle is strictly non-null across all layers."""

    def test_database_direct_subtitles_non_null(self):
        """Verify all rows in SQLite database yield non-null subtitle strings under server query logic."""
        conn = get_db_connection()
        c = conn.cursor()

        queries = [
            ("words", "SELECT id, term, COALESCE(ipa_pronunciation, dialectal_notes, '') AS subtitle FROM words"),
            ("fauna", "SELECT id, common_name_ca, COALESCE(scientific_name, '') AS subtitle FROM fauna"),
            ("flora", "SELECT id, common_name_ca, scientific_name AS subtitle FROM flora"),
            ("emblematic_businesses", "SELECT id, name, municipality AS subtitle FROM emblematic_businesses"),
            ("historical_events", "SELECT id, title, date_display AS subtitle FROM historical_events"),
        ]

        total_checked = 0
        for table, sql in queries:
            c.execute(sql)
            rows = c.fetchall()
            for r in rows:
                sub = r["subtitle"]
                self.assertIsNotNone(sub, f"Null subtitle in table '{table}', row id={r['id']}")
                self.assertIsInstance(sub, str, f"Non-string subtitle in table '{table}', row id={r['id']}")
                total_checked += 1

        conn.close()
        print(f"\n[Subtitle Audit] Verified {total_checked} database records: 0 null subtitles.")

    def test_api_catalog_all_items_subtitle_non_null(self):
        """Verify 100% of items returned by /api/curiositats have a non-null string subtitle."""
        status, items, _ = fetch_api("/api/curiositats")
        self.assertEqual(status, 200)
        self.assertGreater(len(items), 1000)

        null_count = 0
        empty_str_count = 0
        non_empty_str_count = 0

        for it in items:
            self.assertIn("subtitle", it, f"Item missing 'subtitle' key: {it.get('title')}")
            sub = it["subtitle"]
            if sub is None:
                null_count += 1
            elif isinstance(sub, str):
                if sub == "":
                    empty_str_count += 1
                else:
                    non_empty_str_count += 1
            else:
                self.fail(f"Item 'subtitle' is of unexpected type {type(sub)}: {sub}")

        print(
            f"[Subtitle Audit] API Catalog ({len(items)} items): "
            f"Null: {null_count}, Non-empty string: {non_empty_str_count}, Empty string: {empty_str_count}"
        )
        self.assertEqual(null_count, 0, f"Found {null_count} null subtitles in /api/curiositats")


class TestInvalidCategory404(unittest.TestCase):
    """Empirical verification that /api/random returns HTTP 404 for invalid category parameters."""

    def test_invalid_category_adversarial_matrix(self):
        """Stress-test /api/random?category=... with a matrix of invalid and adversarial inputs."""
        adversarial_categories = [
            "nonexistent",
            "invalid_slug",
            "foo",
            "bar",
            "12345",
            "true",
            "false",
            "null",
            "undefined",
            "none",
            "Words",        # Uppercase initial
            "WORDS",        # Full uppercase
            "FAUNA",
            "FLORA",
            "BUSINESSES",
            "HISTORY",
            "words; DROP TABLE words; --",
            "' OR '1'='1",
            "<script>alert(1)</script>",
            "words,fauna",
            "words/fauna",
            "paraules",     # Catalan word for 'words'
            "negocis",     # Catalan word for 'businesses'
            "historia",     # Catalan word for 'history'
            "x" * 200,      # Long string
        ]

        print(f"\n[404 Verification] Testing {len(adversarial_categories)} adversarial category payloads...")
        for cat in adversarial_categories:
            with self.subTest(category=cat):
                status, data, headers = fetch_api("/api/random", {"category": cat})

                # Assert HTTP 404
                self.assertEqual(
                    status,
                    404,
                    f"Category '{cat}' expected 404, got status {status}"
                )

                # Assert response is valid JSON dictionary
                self.assertIsInstance(data, dict, f"Expected JSON object for 404 response on '{cat}'")

                # Assert structured error response schema
                self.assertEqual(data.get("error"), "Not Found")
                self.assertIn("message", data)
                self.assertIn("valid_categories", data)
                self.assertEqual(
                    list(data["valid_categories"]),
                    list(VALID_CATEGORIES),
                    f"Invalid valid_categories in 404 response: {data.get('valid_categories')}"
                )

                # Assert headers
                content_type = headers.get("Content-Type", "")
                self.assertIn("application/json", content_type)
                self.assertEqual(headers.get("Access-Control-Allow-Origin"), "*")

        print(f"[404 Verification] All {len(adversarial_categories)} adversarial categories correctly returned structured 404.")


class TestThreadingHTTPServerConcurrency(unittest.TestCase):
    """Empirical concurrency stress testing of server.py's ThreadingHTTPServer."""

    def _execute_concurrent_batch(self, num_workers: int, total_requests: int):
        """Execute a batch of mixed requests concurrently using ThreadPoolExecutor."""
        base_url = start_test_server()
        endpoints = [
            ("/api/random", 200),
            ("/api/curiositats?category=fauna", 200),
            ("/api/curiositats?category=flora", 200),
            ("/api/stats", 200),
            ("/swagger/", 200),
            ("/openapi.json", 200),
            ("/api/random?category=nonexistent_category_x", 404),
        ]

        def worker_task(req_id: int):
            path, expected_status = random.choice(endpoints)
            url = f"{base_url}{path}"
            t0 = time.perf_counter()
            req = urllib.request.Request(url, headers={"User-Agent": f"ConcurrentStressWorker/{req_id}"})
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    status = resp.status
                    body = resp.read()
                    dt = time.perf_counter() - t0
                    return (req_id, status, expected_status, dt, len(body), None)
            except urllib.error.HTTPError as e:
                dt = time.perf_counter() - t0
                body = e.read()
                return (req_id, e.code, expected_status, dt, len(body), None)
            except Exception as e:
                dt = time.perf_counter() - t0
                return (req_id, -1, expected_status, dt, 0, str(e))

        t_start = time.perf_counter()
        results = []
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(worker_task, i) for i in range(total_requests)]
            for fut in as_completed(futures):
                results.append(fut.result())
        t_total = time.perf_counter() - t_start

        errors = [r for r in results if r[5] is not None or r[1] != r[2]]
        latencies = sorted([r[3] for r in results])
        median_lat = latencies[len(latencies) // 2]
        p95_lat = latencies[int(len(latencies) * 0.95)]
        p99_lat = latencies[int(len(latencies) * 0.99)]
        max_lat = latencies[-1]
        rps = total_requests / t_total

        print(
            f"[Concurrency] Workers={num_workers:3d} | Total Req={total_requests:3d} | "
            f"Time={t_total:.3f}s | Throughput={rps:6.1f} req/s | "
            f"Median={median_lat*1000:5.1f}ms | p95={p95_lat*1000:5.1f}ms | "
            f"p99={p99_lat*1000:5.1f}ms | Max={max_lat*1000:5.1f}ms | Errors={len(errors)}"
        )

        self.assertEqual(len(errors), 0, f"Concurrency test failed with {len(errors)} errors: {errors[:5]}")
        return {
            "num_workers": num_workers,
            "total_requests": total_requests,
            "time_total": t_total,
            "rps": rps,
            "median_ms": median_lat * 1000,
            "p95_ms": p95_lat * 1000,
            "p99_ms": p99_lat * 1000,
            "max_ms": max_lat * 1000,
            "errors": len(errors),
        }

    def test_concurrency_50_workers(self):
        """Stress-test ThreadingHTTPServer with 50 concurrent threads (100 requests)."""
        metrics = self._execute_concurrent_batch(num_workers=50, total_requests=100)
        self.assertEqual(metrics["errors"], 0)

    def test_concurrency_75_workers(self):
        """Stress-test ThreadingHTTPServer with 75 concurrent threads (150 requests)."""
        metrics = self._execute_concurrent_batch(num_workers=75, total_requests=150)
        self.assertEqual(metrics["errors"], 0)

    def test_concurrency_100_workers(self):
        """Stress-test ThreadingHTTPServer with 100 concurrent threads (200 requests)."""
        metrics = self._execute_concurrent_batch(num_workers=100, total_requests=200)
        self.assertEqual(metrics["errors"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)


class TestHostileAnglesAndSecurity(unittest.TestCase):
    """Adversarial security, method resilience, path traversal, and Unicode NFD tests."""

    def test_catalan_unicode_decomposed_nfd_search(self):
        """Verify search matches NFD (decomposed Unicode) queries against NFC corpus."""
        import unicodedata

        nfc_query = "talaiòtic"
        nfd_query = unicodedata.normalize("NFD", nfc_query)
        self.assertNotEqual(nfc_query, nfd_query, "NFD must be byte-different from NFC")

        status_nfc, items_nfc, _ = fetch_api("/api/curiositats", {"search": nfc_query})
        status_nfd, items_nfd, _ = fetch_api("/api/curiositats", {"search": nfd_query})

        self.assertEqual(status_nfc, 200)
        self.assertEqual(status_nfd, 200)
        self.assertGreater(len(items_nfc), 0)
        self.assertEqual(
            len(items_nfc),
            len(items_nfd),
            f"NFC search returned {len(items_nfc)} items, but NFD returned {len(items_nfd)}"
        )

    def test_http_options_cors_preflight(self):
        """Verify OPTIONS method returns 204 with CORS preflight headers."""
        base_url = start_test_server()
        url = f"{base_url}/api/random"
        req = urllib.request.Request(url, method="OPTIONS")
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 204)
            self.assertEqual(resp.headers.get("Access-Control-Allow-Origin"), "*")
            self.assertIn("GET", resp.headers.get("Access-Control-Allow-Methods", ""))

    def test_static_path_traversal_rejection(self):
        """Verify directory traversal attempts cannot escape the web directory."""
        traversal_payloads = [
            "/../curiositats.db",
            "/../../server.py",
            "/%2e%2e/curiositats.db",
            "/%2e%2e/%2e%2e/server.py",
            "/..\\..\\server.py",
        ]
        base_url = start_test_server()
        for payload in traversal_payloads:
            with self.subTest(payload=payload):
                url = f"{base_url}{payload}"
                req = urllib.request.Request(url)
                try:
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        # If 200, ensure it did not serve server.py or curiositats.db
                        body = resp.read()
                        self.assertNotIn(b"ThreadingHTTPServer", body)
                        self.assertNotIn(b"SQLite format 3", body)
                except urllib.error.HTTPError as e:
                    self.assertIn(e.code, (400, 403, 404), f"Unexpected status code {e.code} for traversal")

    def test_sustained_burst_stability(self):
        """Execute a sustained burst of 500 requests to verify zero connection starvation."""
        base_url = start_test_server()
        endpoints = [
            "/api/random",
            "/api/curiositats",
            "/api/stats",
            "/swagger/",
            "/api/random?category=words",
            "/api/random?category=businesses",
        ]

        def ping(idx: int):
            ep = endpoints[idx % len(endpoints)]
            req = urllib.request.Request(f"{base_url}{ep}")
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status

        t0 = time.perf_counter()
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(ping, i) for i in range(500)]
            statuses = [fut.result() for fut in as_completed(futures)]
        elapsed = time.perf_counter() - t0

        self.assertEqual(len(statuses), 500)
        self.assertTrue(all(s == 200 for s in statuses))
        rps = 500 / elapsed
        print(f"\n[Sustained Burst] 500 requests completed in {elapsed:.3f}s ({rps:.1f} req/s). 100% 200 OK.")

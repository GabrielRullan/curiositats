"""Base utilities, fixtures, and assertions for 'Una teringa de curiositats' test suite.

Zero external dependencies: uses Python standard library only (unittest, sqlite3, urllib, json, threading).
"""

import functools
from http.server import HTTPServer
import json
import os
from pathlib import Path
import re
import sqlite3
import threading
import unittest
import urllib.parse
import urllib.request

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "curiositats.db"
SEED_PATH = PROJECT_ROOT / "database" / "seed_data.json"
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"
SOURCES_PATH = PROJECT_ROOT / "database" / "reference_sources.json"
WEB_DIR = PROJECT_ROOT / "web"
DOCS_DIR = PROJECT_ROOT / "docs"
SKILLS_DIR = PROJECT_ROOT / "skills"
INIT_DB_SCRIPT = PROJECT_ROOT / "scripts" / "importers" / "init_db.py"

# Global test server singleton
_server_instance = None
_server_thread = None
_server_lock = threading.Lock()
_server_url = None


def is_strict() -> bool:
    """Return True if strict testing is enabled (no skipping allowed)."""
    val = os.environ.get("CURIOSTATS_E2E_STRICT", "").lower().strip()
    return val in ("1", "true", "yes", "on")


def is_m1_ready() -> bool:
    """Check if Milestone 1 (Data cleaning & alignment) is ready."""
    if not SEED_PATH.exists() or not DB_PATH.exists():
        return False
    try:
        with open(SEED_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for fa in data.get("fauna", []):
            if "Mallorquin Mastiff" in fa.get("common_name_ca", ""):
                return False
        return True
    except Exception:
        return False


def is_m2_ready() -> bool:
    """Check if Milestone 2 (Documentation) is ready."""
    readme = PROJECT_ROOT / "README.md"
    arch = DOCS_DIR / "ARCHITECTURE.md"
    sources = DOCS_DIR / "SOURCES.md"
    if not (readme.exists() and arch.exists() and sources.exists()):
        return False
    try:
        arch_text = arch.read_text(encoding="utf-8")
        # Should accurately document Python http.server and NOT mention FastAPI as current backend
        return "FastAPI" not in arch_text and "http.server" in arch_text
    except Exception:
        return False


def is_m3_ready() -> bool:
    """Check if Milestone 3 (AI skill for references) is ready."""
    skill_file = SKILLS_DIR / "afegir-referencies" / "SKILL.md"
    return skill_file.exists() and skill_file.stat().st_size > 100


def is_m4_ready() -> bool:
    """Check if Milestone 4 (OpenAPI and Swagger UI) is ready."""
    openapi_file = WEB_DIR / "openapi.json"
    swagger_file = WEB_DIR / "swagger" / "index.html"
    return openapi_file.exists() and swagger_file.exists()


def is_m5_ready() -> bool:
    """Check if Milestone 5 (Contact, Privacy, and Git) is ready."""
    gitignore = PROJECT_ROOT / ".gitignore"
    license_file = PROJECT_ROOT / "LICENSE"
    index_html = WEB_DIR / "index.html"
    if not (gitignore.exists() and license_file.exists() and index_html.exists()):
        return False
    try:
        content = index_html.read_text(encoding="utf-8").lower()
        return ("privadesa" in content or "cookie" in content) and ("contact" in content or "contacte" in content)
    except Exception:
        return False


def milestone_requirement(milestone_id: str, condition_fn, description: str = ""):
    """Decorator to mark a test as milestone-specific with progressive skip support."""
    def decorator(test_func):
        @functools.wraps(test_func)
        def wrapper(self, *args, **kwargs):
            if not is_strict() and not condition_fn():
                self.skipTest(f"[{milestone_id} Pending] {description or 'Milestone not yet implemented'}")
            return test_func(self, *args, **kwargs)
        return wrapper
    return decorator


def start_test_server():
    """Start local server on dynamic port 0 once per test process."""
    global _server_instance, _server_thread, _server_url
    with _server_lock:
        if _server_url is not None:
            return _server_url

        import server
        _server_instance = HTTPServer(("127.0.0.1", 0), server.TeringaRequestHandler)
        port = _server_instance.server_address[1]
        _server_thread = threading.Thread(target=_server_instance.serve_forever, daemon=True)
        _server_thread.start()
        _server_url = f"http://127.0.0.1:{port}"
        return _server_url


def stop_test_server():
    """Stop test server if running."""
    global _server_instance, _server_thread, _server_url
    with _server_lock:
        if _server_instance is not None:
            _server_instance.shutdown()
            _server_instance.server_close()
            _server_instance = None
            _server_thread = None
            _server_url = None


def fetch_api(path: str, params: dict = None) -> tuple:
    """Make HTTP GET request to test server and return (status_code, data, headers)."""
    base_url = start_test_server()
    url = f"{base_url}{path}"
    if params:
        url += f"?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(url, headers={"User-Agent": "TeringaE2ETester/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
            headers = dict(resp.getheaders())
            raw_body = resp.read()
            content_type = headers.get("Content-Type", "")
            if "application/json" in content_type:
                data = json.loads(raw_body.decode("utf-8"))
            else:
                data = raw_body.decode("utf-8", errors="replace")
            return status, data, headers
    except urllib.error.HTTPError as e:
        raw_body = e.read()
        try:
            data = json.loads(raw_body.decode("utf-8"))
        except Exception:
            data = raw_body.decode("utf-8", errors="replace")
        return e.code, data, dict(e.headers)


def get_db_connection():
    """Return sqlite3 connection with Row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def extract_fallback_data() -> list:
    """Parse FALLBACK_DATA array from web/app.js safely."""
    app_js_path = WEB_DIR / "app.js"
    if not app_js_path.exists():
        return []
    content = app_js_path.read_text(encoding="utf-8")
    m = re.search(r"const FALLBACK_DATA = (\[[\s\S]*?\]);", content)
    if not m:
        return []
    raw_array = m.group(1)

    # Standardize unquoted JS keys to JSON valid strings: e.g. type: -> "type":
    # Replace key names (word characters followed by colon)
    cleaned = re.sub(r'([,{]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', raw_array)
    # Remove trailing commas before closing brackets/braces
    cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
    try:
        return json.loads(cleaned)
    except Exception:
        # Fallback to regex item extraction if JSON parse fails due to complex JS
        items = []
        for obj_match in re.finditer(r'\{([^{}]+)\}', raw_array):
            block = obj_match.group(1)
            item = {}
            for field in ("type", "title", "subtitle", "tag", "definition", "curiosities", "source_reference"):
                field_match = re.search(rf'{field}\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', block)
                if field_match:
                    item[field] = field_match.group(1)
            if item.get("title"):
                items.append(item)
        return items


def detect_mojibake(text: str) -> list:
    """Scan text for common mojibake patterns or unicode replacement characters."""
    if not isinstance(text, str):
        return []
    suspicious_patterns = [
        ("\ufffd", "Unicode Replacement Character (U+FFFD)"),
        ("Ã¨", "Mojibake for è"),
        ("Ã©", "Mojibake for é"),
        ("Ã ", "Mojibake for à"),
        ("Ã²", "Mojibake for ò"),
        ("Ã³", "Mojibake for ó"),
        ("Ã­", "Mojibake for í"),
        ("Ã§", "Mojibake for ç"),
        ("Ã¯", "Mojibake for ï"),
        ("Ã¼", "Mojibake for ü"),
        ("â€™", "Mojibake for right single quote"),
        ("â€œ", "Mojibake for left double quote"),
        ("â€", "Mojibake for right double quote"),
    ]
    findings = []
    for pattern, desc in suspicious_patterns:
        if pattern in text:
            findings.append((pattern, desc))
    return findings


class TeringaTestCase(unittest.TestCase):
    """Base test case providing shared setup and assertions for all test tiers."""

    @classmethod
    def setUpClass(cls):
        cls.server_url = start_test_server()

    def assertCatalanTextClean(self, text: str, field_desc: str = "text"):
        """Assert text does not contain mojibake or corrupt encoding."""
        findings = detect_mojibake(text)
        self.assertEqual(
            findings,
            [],
            f"Encoding corruption detected in {field_desc}: {findings} inside: '{text[:80]}...'"
        )

    def assertUnifiedCuriositatItem(self, item: dict):
        """Assert dictionary has normalized curiosity fields returned by server and frontend."""
        required_keys = ["title", "subtitle", "tag", "definition", "source_reference", "type"]
        for key in required_keys:
            self.assertIn(key, item, f"Missing required unified schema key '{key}' in item: {item}")
            self.assertIsNotNone(item[key], f"Field '{key}' must not be None in item: {item}")
        self.assertIn(
            item["type"],
            ["words", "fauna", "flora", "businesses", "history"],
            f"Invalid item type '{item['type']}'"
        )

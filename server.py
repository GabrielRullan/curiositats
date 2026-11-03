"""Servidor web i API local per a 'Una teringa de curiositats'.

No requereix dependències externes (només la biblioteca estàndard de Python).
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import random
import sqlite3
import unicodedata
import urllib.parse

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "curiositats.db"
WEB_DIR = BASE_DIR / "web"

VALID_CATEGORIES = ("words", "fauna", "flora", "businesses", "history")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_all_curiositats(category=None, search=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    items = []

    # 1. Words
    if not category or category == "words":
        cursor.execute(
            "SELECT id, term AS title, COALESCE(ipa_pronunciation, dialectal_notes, '') AS subtitle, COALESCE(grammatical_category, '') AS tag, definition, example_sentence, etymology, dialectal_notes, source_reference, source_url, 'words' AS type FROM words"
        )
        for r in cursor.fetchall():
            items.append(dict(r))

    # 2. Fauna
    if not category or category == "fauna":
        cursor.execute(
            "SELECT id, common_name_ca AS title, COALESCE(scientific_name, '') AS subtitle, group_type AS tag, is_endemic, is_native_breed, conservation_status, habitat, description AS definition, curiosities, source_reference, source_url, 'fauna' AS type FROM fauna"
        )
        for r in cursor.fetchall():
            items.append(dict(r))

    # 3. Flora
    if not category or category == "flora":
        cursor.execute(
            "SELECT id, common_name_ca AS title, scientific_name AS subtitle, COALESCE(family, '') AS tag, is_endemic, flowering_period, habitat, traditional_uses, description AS definition, curiosities, source_reference, source_url, 'flora' AS type FROM flora"
        )
        for r in cursor.fetchall():
            items.append(dict(r))

    # 4. Negocis
    if not category or category == "businesses":
        cursor.execute(
            "SELECT id, name AS title, municipality AS subtitle, sector AS tag, category_type, foundation_year, address, latitude, longitude, history_summary AS definition, heritage_elements, source_reference, source_url, 'businesses' AS type FROM emblematic_businesses"
        )
        for r in cursor.fetchall():
            items.append(dict(r))

    # 5. Història
    if not category or category == "history":
        cursor.execute(
            "SELECT id, title, date_display AS subtitle, historical_period AS tag, location_scope, summary AS definition, detailed_description, key_figures, source_reference, source_url, 'history' AS type FROM historical_events"
        )
        for r in cursor.fetchall():
            items.append(dict(r))

    conn.close()

    # Filtre de cerca si s'ha especificat (normalització Unicode NFC per a caràcters catalans)
    if search:
        s = unicodedata.normalize("NFC", search).lower().strip()
        if s:
            filtered = []
            for it in items:
                raw_corpus = f"{it.get('title') or ''} {it.get('subtitle') or ''} {it.get('tag') or ''} {it.get('definition') or ''}"
                text_corpus = unicodedata.normalize("NFC", raw_corpus).lower()
                if s in text_corpus:
                    filtered.append(it)
            items = filtered

    return items


class TeringaRequestHandler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # Rutas d'API
        if parsed.path == "/api/curiositats":
            params = urllib.parse.parse_qs(parsed.query)
            category = params.get("category", [None])[0]
            search = params.get("search", [None])[0]
            items = fetch_all_curiositats(category=category, search=search)

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(items, ensure_ascii=False).encode("utf-8"))
            return

        elif parsed.path == "/api/random":
            params = urllib.parse.parse_qs(parsed.query)
            category = params.get("category", [None])[0]

            if category is not None and category.strip() != "":
                cat_clean = category.strip()
                if cat_clean not in VALID_CATEGORIES:
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    error_resp = {
                        "error": "Not Found",
                        "message": f"Categoria '{cat_clean}' no trobada o no vàlida. Categories permeses: {', '.join(VALID_CATEGORIES)}.",
                        "valid_categories": list(VALID_CATEGORIES),
                    }
                    self.wfile.write(json.dumps(error_resp, ensure_ascii=False).encode("utf-8"))
                    return

                items = fetch_all_curiositats(category=cat_clean)
                if not items:
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    error_resp = {
                        "error": "Not Found",
                        "message": f"No s'han trobat curiositats per a la categoria '{cat_clean}'.",
                        "valid_categories": list(VALID_CATEGORIES),
                    }
                    self.wfile.write(json.dumps(error_resp, ensure_ascii=False).encode("utf-8"))
                    return

                chosen = random.choice(items)
            else:
                # Mostreig estratificat equilibrat per categoria per evitar biaix lèxic
                categories = list(VALID_CATEGORIES)
                random.shuffle(categories)
                chosen = None
                for cat in categories:
                    items = fetch_all_curiositats(category=cat)
                    if items:
                        chosen = random.choice(items)
                        break

                if not chosen:
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    error_resp = {
                        "error": "Not Found",
                        "message": "No s'han trobat curiositats al catàleg.",
                        "valid_categories": list(VALID_CATEGORIES),
                    }
                    self.wfile.write(json.dumps(error_resp, ensure_ascii=False).encode("utf-8"))
                    return

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(chosen, ensure_ascii=False).encode("utf-8"))
            return

        elif parsed.path == "/api/stats":
            conn = get_db_connection()
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

            stats = {
                "words": w,
                "fauna": fa,
                "flora": fl,
                "businesses": b,
                "history": h,
                "total": w + fa + fl + b + h,
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(stats, ensure_ascii=False).encode("utf-8"))
            return

        elif parsed.path in ("/api/openapi.json", "/openapi.json"):
            openapi_file = WEB_DIR / "openapi.json"
            if openapi_file.is_file():
                content = openapi_file.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "openapi.json not found")
            return

        elif parsed.path == "/swagger":
            self.send_response(301)
            self.send_header("Location", "/swagger/")
            self.end_headers()
            return

        elif parsed.path == "/swagger/":
            swagger_file = WEB_DIR / "swagger" / "index.html"
            if swagger_file.is_file():
                content = swagger_file.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "Swagger UI not found")
            return

        # Fitxers estàtics (inclou /swagger/*, etc.)
        return super().do_GET()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()


def run_server(port=8080):
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, TeringaRequestHandler)
    print(
        f"🌐 Servidor d'Una teringa de curiositats en marxa a: http://localhost:{port}"
    )
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()

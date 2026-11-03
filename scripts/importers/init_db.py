"""Script per inicialitzar la base de dades SQLite 'curiositats.db' amb l'esquema i les dades inicials."""

import argparse
import json
from pathlib import Path
import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "curiositats.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"
SEED_PATH = BASE_DIR / "database" / "seed_data.json"

TABLES = ["words", "fauna", "flora", "emblematic_businesses", "historical_events"]


def validate_seed_data(data: dict) -> None:
    """Valida les dades inicials abans de qualsevol inserció (pre-insertion check)."""
    for table in TABLES:
        if table not in data:
            raise ValueError(f"Falta la taula '{table}' al fitxer de dades inicials.")
        if not isinstance(data[table], list) or len(data[table]) == 0:
            raise ValueError(f"La taula '{table}' no conté una llista vàlida de registres.")

    # 1. Words
    terms_seen = set()
    for i, w in enumerate(data["words"]):
        term = w.get("term", "").strip() if isinstance(w.get("term"), str) else ""
        definition = w.get("definition", "").strip() if isinstance(w.get("definition"), str) else ""
        if not term:
            raise ValueError(f"words[{i}]: 'term' no pot ser buit.")
        if not definition:
            raise ValueError(f"words[{i}] ({term}): 'definition' no pot ser buida.")
        if term in terms_seen:
            raise ValueError(f"words[{i}]: Terme duplicat '{term}'.")
        terms_seen.add(term)

    # 2. Fauna
    fauna_seen = set()
    for i, fa in enumerate(data["fauna"]):
        name = fa.get("common_name_ca", "").strip() if isinstance(fa.get("common_name_ca"), str) else ""
        group = fa.get("group_type", "").strip() if isinstance(fa.get("group_type"), str) else ""
        desc = fa.get("description", "").strip() if isinstance(fa.get("description"), str) else ""
        if not name:
            raise ValueError(f"fauna[{i}]: 'common_name_ca' no pot ser buit.")
        if not group:
            raise ValueError(f"fauna[{i}] ({name}): 'group_type' no pot ser buit.")
        if not desc:
            raise ValueError(f"fauna[{i}] ({name}): 'description' no pot ser buida.")
        if name in fauna_seen:
            raise ValueError(f"fauna[{i}]: Nom comú duplicat '{name}'.")
        fauna_seen.add(name)

    # 3. Flora
    flora_common_seen = set()
    flora_sci_seen = set()
    for i, fl in enumerate(data["flora"]):
        name = fl.get("common_name_ca", "").strip() if isinstance(fl.get("common_name_ca"), str) else ""
        sci = fl.get("scientific_name", "").strip() if isinstance(fl.get("scientific_name"), str) else ""
        desc = fl.get("description", "").strip() if isinstance(fl.get("description"), str) else ""
        if not name:
            raise ValueError(f"flora[{i}]: 'common_name_ca' no pot ser buit.")
        if not sci:
            raise ValueError(f"flora[{i}] ({name}): 'scientific_name' no pot ser buit.")
        if not desc:
            raise ValueError(f"flora[{i}] ({name}): 'description' no pot ser buida.")
        if name in flora_common_seen:
            raise ValueError(f"flora[{i}]: Nom comú duplicat '{name}'.")
        if sci in flora_sci_seen:
            raise ValueError(f"flora[{i}]: Nom científic duplicat '{sci}'.")
        flora_common_seen.add(name)
        flora_sci_seen.add(sci)

    # 4. Emblematic Businesses
    biz_seen = set()
    for i, b in enumerate(data["emblematic_businesses"]):
        name = b.get("name", "").strip() if isinstance(b.get("name"), str) else ""
        mun = b.get("municipality", "").strip() if isinstance(b.get("municipality"), str) else ""
        hist = b.get("history_summary", "").strip() if isinstance(b.get("history_summary"), str) else ""
        lat = b.get("latitude")
        lon = b.get("longitude")
        year = b.get("foundation_year")

        if not name:
            raise ValueError(f"emblematic_businesses[{i}]: 'name' no pot ser buit.")
        if not mun:
            raise ValueError(f"emblematic_businesses[{i}] ({name}): 'municipality' no pot ser buit.")
        if not hist:
            raise ValueError(f"emblematic_businesses[{i}] ({name}): 'history_summary' no pot ser buit.")
        if lat is not None and not (39.0 <= lat <= 40.2):
            raise ValueError(f"emblematic_businesses[{i}] ({name}): latitud {lat} fora de rang (39.0 - 40.2).")
        if lon is not None and not (2.2 <= lon <= 3.6):
            raise ValueError(f"emblematic_businesses[{i}] ({name}): longitud {lon} fora de rang (2.2 - 3.6).")
        if year is not None and year <= 1200:
            raise ValueError(f"emblematic_businesses[{i}] ({name}): any de fundació {year} invàlid (ha de ser > 1200 o NULL).")
        if name in biz_seen:
            raise ValueError(f"emblematic_businesses[{i}]: Negoci duplicat '{name}'.")
        biz_seen.add(name)

    # 5. Historical Events
    events_seen = set()
    for i, ev in enumerate(data["historical_events"]):
        title = ev.get("title", "").strip() if isinstance(ev.get("title"), str) else ""
        period = ev.get("historical_period", "").strip() if isinstance(ev.get("historical_period"), str) else ""
        summary = ev.get("summary", "").strip() if isinstance(ev.get("summary"), str) else ""
        y_start = ev.get("year_start")
        y_end = ev.get("year_end")

        if not title:
            raise ValueError(f"historical_events[{i}]: 'title' no pot ser buit.")
        if not period:
            raise ValueError(f"historical_events[{i}] ({title}): 'historical_period' no pot ser buit.")
        if not summary:
            raise ValueError(f"historical_events[{i}] ({title}): 'summary' no pot ser buit.")
        if y_start is None:
            raise ValueError(f"historical_events[{i}] ({title}): 'year_start' no pot ser NULL.")
        if y_end is not None and y_start > y_end:
            raise ValueError(f"historical_events[{i}] ({title}): year_start ({y_start}) > year_end ({y_end}).")
        if title in events_seen:
            raise ValueError(f"historical_events[{i}]: Esdeveniment duplicat '{title}'.")
        events_seen.add(title)


def insert_data(conn: sqlite3.Connection, data: dict) -> None:
    """Insereix totes les files a la connexió SQLite indicada."""
    cursor = conn.cursor()

    # Inserir Paraules
    for w in data.get("words", []):
        cursor.execute(
            """
            INSERT INTO words (term, ipa_pronunciation, grammatical_category, definition, example_sentence, etymology, dialectal_notes, source_reference)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                w.get("term"),
                w.get("ipa_pronunciation"),
                w.get("grammatical_category"),
                w.get("definition"),
                w.get("example_sentence"),
                w.get("etymology"),
                w.get("dialectal_notes"),
                w.get("source_reference"),
            ),
        )

    # Inserir Fauna (incloent mapeig segur de image_url)
    for fa in data.get("fauna", []):
        cursor.execute(
            """
            INSERT INTO fauna (common_name_ca, scientific_name, group_type, is_endemic, is_native_breed, conservation_status, habitat, description, curiosities, image_url, source_reference)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                fa.get("common_name_ca"),
                fa.get("scientific_name"),
                fa.get("group_type"),
                fa.get("is_endemic"),
                fa.get("is_native_breed"),
                fa.get("conservation_status"),
                fa.get("habitat"),
                fa.get("description"),
                fa.get("curiosities"),
                fa.get("image_url"),
                fa.get("source_reference"),
            ),
        )

    # Inserir Flora (incloent mapeig segur de image_url)
    for fl in data.get("flora", []):
        cursor.execute(
            """
            INSERT INTO flora (common_name_ca, scientific_name, family, is_endemic, flowering_period, habitat, traditional_uses, description, curiosities, image_url, source_reference)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                fl.get("common_name_ca"),
                fl.get("scientific_name"),
                fl.get("family"),
                fl.get("is_endemic"),
                fl.get("flowering_period"),
                fl.get("habitat"),
                fl.get("traditional_uses"),
                fl.get("description"),
                fl.get("curiosities"),
                fl.get("image_url"),
                fl.get("source_reference"),
            ),
        )

    # Inserir Negocis Emblemàtics
    for b in data.get("emblematic_businesses", []):
        cursor.execute(
            """
            INSERT INTO emblematic_businesses (name, category_type, sector, foundation_year, municipality, address, latitude, longitude, history_summary, heritage_elements, is_active, source_reference)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                b.get("name"),
                b.get("category_type"),
                b.get("sector"),
                b.get("foundation_year"),
                b.get("municipality"),
                b.get("address"),
                b.get("latitude"),
                b.get("longitude"),
                b.get("history_summary"),
                b.get("heritage_elements"),
                b.get("is_active"),
                b.get("source_reference"),
            ),
        )

    # Inserir Fets Històrics
    for ev in data.get("historical_events", []):
        cursor.execute(
            """
            INSERT INTO historical_events (title, historical_period, year_start, year_end, date_display, location_scope, summary, detailed_description, key_figures, source_reference)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                ev.get("title"),
                ev.get("historical_period"),
                ev.get("year_start"),
                ev.get("year_end"),
                ev.get("date_display"),
                ev.get("location_scope"),
                ev.get("summary"),
                ev.get("detailed_description"),
                ev.get("key_figures"),
                ev.get("source_reference"),
            ),
        )


def verify_database(conn: sqlite3.Connection, data: dict) -> None:
    """Verifica que tots els registres s'hagin inserit correctament i sense buits (post-insertion check)."""
    cursor = conn.cursor()

    # 1. Comprovació de recomptes
    for table in TABLES:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count_db = cursor.fetchone()[0]
        count_seed = len(data[table])
        if count_db != count_seed:
            raise RuntimeError(
                f"Discrepància en {table}: {count_db} a la base de dades vs {count_seed} esperats."
            )

    # 2. Comprovació de nuls i camps buits obligatoris
    integrity_checks = [
        ("words", "term IS NULL OR TRIM(term) = '' OR definition IS NULL OR TRIM(definition) = ''"),
        ("fauna", "common_name_ca IS NULL OR TRIM(common_name_ca) = '' OR group_type IS NULL OR TRIM(group_type) = '' OR description IS NULL OR TRIM(description) = ''"),
        ("flora", "common_name_ca IS NULL OR TRIM(common_name_ca) = '' OR scientific_name IS NULL OR TRIM(scientific_name) = '' OR description IS NULL OR TRIM(description) = ''"),
        ("emblematic_businesses", "name IS NULL OR TRIM(name) = '' OR municipality IS NULL OR TRIM(municipality) = '' OR history_summary IS NULL OR TRIM(history_summary) = ''"),
        ("historical_events", "title IS NULL OR TRIM(title) = '' OR year_start IS NULL OR summary IS NULL OR TRIM(summary) = ''"),
    ]

    for table, cond in integrity_checks:
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {cond}")
        invalid_count = cursor.fetchone()[0]
        if invalid_count > 0:
            raise RuntimeError(f"Trobat(s) {invalid_count} registre(s) invàlid(s) a la taula '{table}'.")


def generate_fallback_data(data: dict) -> list:
    """Genera la llista de 31 items en el format retornat per /api/curiositats per a web/app.js."""
    items = []

    # 1. Words
    for i, w in enumerate(data.get("words", []), 1):
        curiosity = ""
        if w.get("example_sentence") and w.get("etymology"):
            curiosity = f"Exemple: «{w.get('example_sentence')}» Etimologia: {w.get('etymology')}"
        elif w.get("example_sentence"):
            curiosity = f"Exemple: «{w.get('example_sentence')}»"
        elif w.get("etymology"):
            curiosity = f"Etimologia: {w.get('etymology')}"

        items.append({
            "id": i,
            "type": "words",
            "title": w["term"],
            "subtitle": w.get("ipa_pronunciation"),
            "tag": w.get("grammatical_category"),
            "definition": w["definition"],
            "example_sentence": w.get("example_sentence"),
            "etymology": w.get("etymology"),
            "dialectal_notes": w.get("dialectal_notes"),
            "curiosities": curiosity,
            "source_reference": w.get("source_reference"),
        })

    # 2. Fauna
    for i, fa in enumerate(data.get("fauna", []), 1):
        items.append({
            "id": i,
            "type": "fauna",
            "title": fa["common_name_ca"],
            "subtitle": fa.get("scientific_name"),
            "tag": fa.get("group_type"),
            "is_endemic": fa.get("is_endemic", False),
            "is_native_breed": fa.get("is_native_breed", False),
            "conservation_status": fa.get("conservation_status"),
            "habitat": fa.get("habitat"),
            "definition": fa["description"],
            "curiosities": fa.get("curiosities"),
            "source_reference": fa.get("source_reference"),
        })

    # 3. Flora
    for i, fl in enumerate(data.get("flora", []), 1):
        items.append({
            "id": i,
            "type": "flora",
            "title": fl["common_name_ca"],
            "subtitle": fl.get("scientific_name"),
            "tag": fl.get("family"),
            "is_endemic": fl.get("is_endemic", False),
            "flowering_period": fl.get("flowering_period"),
            "habitat": fl.get("habitat"),
            "traditional_uses": fl.get("traditional_uses"),
            "definition": fl["description"],
            "curiosities": fl.get("curiosities"),
            "source_reference": fl.get("source_reference"),
        })

    # 4. Emblematic Businesses
    for i, b in enumerate(data.get("emblematic_businesses", []), 1):
        items.append({
            "id": i,
            "type": "businesses",
            "title": b["name"],
            "subtitle": b.get("municipality"),
            "tag": b.get("sector"),
            "category_type": b.get("category_type"),
            "foundation_year": b.get("foundation_year"),
            "address": b.get("address"),
            "latitude": b.get("latitude"),
            "longitude": b.get("longitude"),
            "definition": b["history_summary"],
            "heritage_elements": b.get("heritage_elements"),
            "curiosities": b.get("heritage_elements"),
            "source_reference": b.get("source_reference"),
        })

    # 5. Historical Events
    for i, ev in enumerate(data.get("historical_events", []), 1):
        items.append({
            "id": i,
            "type": "history",
            "title": ev["title"],
            "subtitle": ev.get("date_display"),
            "tag": ev.get("historical_period"),
            "location_scope": ev.get("location_scope"),
            "definition": ev["summary"],
            "detailed_description": ev.get("detailed_description"),
            "curiosities": ev.get("detailed_description"),
            "key_figures": ev.get("key_figures"),
            "source_reference": ev.get("source_reference"),
        })

    return items


def init_database(
    db_path=DB_PATH,
    schema_path=SCHEMA_PATH,
    seed_path=SEED_PATH,
    dry_run=False,
    with_diec=False,
    with_viccionari=False,
    with_dcvb=False,
    export_fallback=False
):
    """Executa la inicialització o validació de la base de dades."""
    mode_text = "[DRY-RUN / VALIDACIÓ]" if dry_run else "[EXECUTANT]"
    print(f"🚀 {mode_text} Inicialitzant procés per a: {db_path}")

    # 1. Llegir i validar dades inicials
    with open(seed_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    validate_seed_data(data)
    print("✅ Pre-comprovació de dades inicials: Dades 100% vàlides.")

    # 2. Llegir esquema
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    # Si és dry-run, usem una base de dades en memòria
    target_conn = sqlite3.connect(":memory:") if dry_run else sqlite3.connect(db_path)

    try:
        cursor = target_conn.cursor()
        cursor.executescript(schema_sql)
        print("✅ Esquema SQL executat correctament.")

        insert_data(target_conn, data)
        print("✅ Inserció de dades completada.")

        verify_database(target_conn, data)
        print("✅ Post-comprovació d'integritat: Tots els registres i restriccions verificats amb èxit.")

        if not dry_run:
            target_conn.commit()
    finally:
        target_conn.close()

    total_items = sum(len(data[t]) for t in TABLES)
    print(f"🎉 Procés finalitzat amb èxit ({total_items} registres catalogats):")
    for t in TABLES:
        print(f"  - {t}: {len(data[t])}")

    # 3. Exportació opcional de FALLBACK_DATA per a web/app.js
    if export_fallback:
        fallback_items = generate_fallback_data(data)
        js_code = "const FALLBACK_DATA = " + json.dumps(fallback_items, indent=2, ensure_ascii=False) + ";\n"
        print("\n=== EXPORT FALLBACK_DATA JS ===")
        print(js_code)

    # 4. Suport opcional per al corpus DIEC2 (Milestone M1 / R3)
    if with_diec:
        print("\n📚 Executant importació del corpus DIEC2 (Milestone M1 / R3)...")
        if str(BASE_DIR) not in sys.path:
            sys.path.insert(0, str(BASE_DIR))
        from scripts.importers.import_diec import import_diec_corpus, JSON_PATH as DIEC_JSON_PATH
        if dry_run:
            mem_conn = sqlite3.connect(":memory:")
            mem_conn.executescript(schema_sql)
            insert_data(mem_conn, data)
            with open(DIEC_JSON_PATH, "r", encoding="utf-8") as f:
                diec_entries = json.load(f)
            from scripts.importers.import_diec import clean_term, clean_definition, format_dialectal_notes, CATEGORY_MAP
            mc = mem_conn.cursor()
            diec_inserted = 0
            for item in diec_entries:
                raw_term = item.get("term", "")
                term = clean_term(raw_term)
                raw_cat = item.get("grammatical_category", "").strip()
                category = CATEGORY_MAP.get(raw_cat, "altres")
                definition = clean_definition(raw_term, item.get("full_definition", ""))
                dialectal_notes = format_dialectal_notes(item.get("matched_keywords", []))
                mc.execute("SELECT id FROM words WHERE LOWER(TRIM(term)) = LOWER(TRIM(?))", (term,))
                if mc.fetchone():
                    continue
                mc.execute(
                    "INSERT INTO words (term, grammatical_category, definition, dialectal_notes, source_reference) VALUES (?, ?, ?, ?, ?)",
                    (term, category, definition, dialectal_notes, "DIEC2 (Institut d'Estudis Catalans)")
                )
                diec_inserted += 1
            mc.execute("SELECT COUNT(*) FROM words")
            total_words_mem = mc.fetchone()[0]
            mem_conn.close()
            print(f"✅ [DRY-RUN] DIEC2 validat: {diec_inserted} inserides sense col·lisions. Total paraules en memòria: {total_words_mem}")
        else:
            inserted, skipped, total_w = import_diec_corpus(db_path=db_path)
            print(f"✅ DIEC2 importat: {inserted} noves, {skipped} omeses, total paraules: {total_w}")

    # 5. Suport opcional per al corpus Viccionari (Milestone M2 / R2)
    if with_viccionari:
        print("\n📖 Executant importació del corpus Viccionari (Milestone M2 / R2)...")
        if str(BASE_DIR) not in sys.path:
            sys.path.insert(0, str(BASE_DIR))
        from scripts.importers.import_viccionari import import_viccionari_corpus, JSON_PATH as VICC_JSON_PATH
        if dry_run:
            with open(VICC_JSON_PATH, "r", encoding="utf-8") as f:
                vicc_entries = json.load(f)
            valid_vicc = [e for e in vicc_entries if (e.get("term") or "").strip()]
            print(f"✅ [DRY-RUN] Viccionari validat: {len(valid_vicc)} entrades vàlides a {VICC_JSON_PATH.name}")
        else:
            res = import_viccionari_corpus(db_path=db_path)
            print(f"✅ Viccionari importat: {res['inserted']} noves, {res['enriched']} enriquides, total paraules: {res['total_words']}")

    # 6. Suport opcional per al corpus DCVB (Milestone M3 / R1)
    if with_dcvb:
        print("\n🏛️ Executant importació del corpus DCVB (Milestone M3 / R1)...")
        if str(BASE_DIR) not in sys.path:
            sys.path.insert(0, str(BASE_DIR))
        from scripts.scrapers.dcvb_crawler import DCVBCrawler
        dcvb_json = BASE_DIR / "database" / "dcvb_extracted_entries.json"
        if dry_run:
            if dcvb_json.exists():
                with open(dcvb_json, "r", encoding="utf-8") as f:
                    dcvb_entries = json.load(f)
                valid_dcvb = [e for e in dcvb_entries if (e.get("term") or "").strip()]
                print(f"✅ [DRY-RUN] DCVB validat: {len(valid_dcvb)} entrades vàlides a {dcvb_json.name}")
        else:
            crawler = DCVBCrawler(db_path=db_path, output_file=dcvb_json)
            res = crawler.import_to_database()
            print(f"✅ DCVB importat: {res['inserted']} noves, {res['enriched']} enriquides, total paraules: {res['total_words']}")


def main():
    parser = argparse.ArgumentParser(
        description="Inicialitza o valida la base de dades SQLite 'curiositats.db' des de seed_data.json."
    )
    parser.add_argument(
        "--check",
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Valida l'esquema i les dades inicials en memòria sense modificar curiositats.db.",
    )
    parser.add_argument(
        "--with-diec",
        "--diec",
        dest="with_diec",
        action="store_true",
        help="Executa també la importació del corpus DIEC2 (91 entrades) a curiositats.db.",
    )
    parser.add_argument(
        "--with-viccionari",
        "--viccionari",
        dest="with_viccionari",
        action="store_true",
        help="Executa també la importació del corpus Viccionari (944 entrades) a curiositats.db.",
    )
    parser.add_argument(
        "--with-dcvb",
        "--dcvb",
        dest="with_dcvb",
        action="store_true",
        help="Executa també la importació del corpus DCVB (100 entrades) a curiositats.db.",
    )
    parser.add_argument(
        "--all",
        "--with-all",
        dest="with_all",
        action="store_true",
        help="Inicialitza la base de dades amb TOT el corpus dialectal complet (seed + DIEC2 + Viccionari + DCVB, 1.130 paraules).",
    )
    parser.add_argument(
        "--export-fallback",
        action="store_true",
        help="Genera i mostra l'array FALLBACK_DATA per a web/app.js a partir de seed_data.json.",
    )
    parser.add_argument("--db", default=DB_PATH, type=Path, help="Ruta al fitxer SQLite")
    parser.add_argument("--schema", default=SCHEMA_PATH, type=Path, help="Ruta al fitxer schema.sql")
    parser.add_argument("--seed", default=SEED_PATH, type=Path, help="Ruta al fitxer seed_data.json")

    args = parser.parse_args()

    with_diec = args.with_diec or args.with_all
    with_viccionari = args.with_viccionari or args.with_all
    with_dcvb = args.with_dcvb or args.with_all

    try:
        init_database(
            db_path=args.db,
            schema_path=args.schema,
            seed_path=args.seed,
            dry_run=args.dry_run,
            with_diec=with_diec,
            with_viccionari=with_viccionari,
            with_dcvb=with_dcvb,
            export_fallback=args.export_fallback,
        )
    except Exception as e:
        print(f"❌ Error crític durant la inicialització: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

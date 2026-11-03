"""
Script d'importació del corpus DIEC2 (91 entrades) a curiositats.db (Milestone M1 / R3).
Garanteix idempotència, neteja de lemes, normalització de categories i compliment de l'esquema.
"""

import sys
import json
import re
import sqlite3
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "curiositats.db"
JSON_PATH = BASE_DIR / "database" / "diec_balear_entries.json"

CATEGORY_MAP = {
    "m.": "nom masculí",
    "f.": "nom femení",
    "m.if.": "nom masculí i femení",
    "adj.": "adjectiu",
    "adj.im.if.": "adjectiu i nom",
    "adj.im.": "adjectiu i nom masculí",
    "f. pl.": "nom femení plural",
    "": "contracció",  # Cas 'as3'
}


def clean_term(raw_term: str) -> str:
    """Neteja el lema eliminant números d'homògrafs i capitalitzant el primer caràcter."""
    cleaned = re.sub(r"\d+$", "", raw_term).strip()
    return cleaned[0].upper() + cleaned[1:] if cleaned else cleaned


def clean_definition(term: str, full_text: str) -> str:
    """Neteja la definició eliminant el lema inicial, homògrafs, categories i etiquetes d'àmbit."""
    clean_t = re.sub(r"\d+$", "", term).strip()
    text = full_text.strip()

    # Eliminar capçalera del lema, números d'homògraf i abreviatures gramaticals
    pattern = rf"^{re.escape(clean_t)}(\s+-\w+|\s+{re.escape(clean_t)}\w*)?(\s+\d+)*(\s+(?:m\.|f\.|adj\.|pl\.|i|inv\.|rec\.|ext\.)+)*"
    text = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()

    # Netejar marcadors numèrics i codis d'àmbit [LC], [HO], etc.
    text = re.sub(r"^[.\s\d]+(?:m\.|f\.|adj\.|pl\.|i|inv\.)*", "", text).strip()
    text = re.sub(r"^(\[[A-Z0-9]+\]\s*)+", "", text).strip()
    text = re.sub(r"^[.\s]+", "", text).strip()

    return text[0].upper() + text[1:] if text else text


def format_dialectal_notes(keywords: list) -> str:
    """Sintetitza una nota d'àmbit geogràfic / dialectal llegible a partir de les paraules clau coincidents."""
    kw_set = set(k.lower() for k in keywords)
    places = []
    if "mallorca" in kw_set or "mallorquí" in kw_set:
        places.append("Mallorca")
    if "menorca" in kw_set or "menorquí" in kw_set:
        places.append("Menorca")
    if "eivissa" in kw_set or "eivissenc" in kw_set:
        places.append("Eivissa")
    if "formentera" in kw_set or "formenterenc" in kw_set or "formenterer" in kw_set:
        places.append("Formentera")

    if len(places) == 4 or (len(places) >= 2 and ("balears" in kw_set or "balear" in kw_set)):
        return "Àmbit balear (Mallorca, Menorca, Eivissa i Formentera)"
    elif len(places) == 1 and not ("balears" in kw_set or "balear" in kw_set):
        return f"Àmbit de {places[0]}" if places[0] != "Eivissa" else "Àmbit d'Eivissa"
    elif len(places) == 2 and not ("balears" in kw_set or "balear" in kw_set):
        return f"Àmbit de {places[0]} i {places[1]}"
    elif "balears" in kw_set or "balear" in kw_set:
        if places:
            return f"Àmbit balear ({' i '.join(places)})"
        return "Àmbit balear general"
    return "Àmbit balear"


def import_diec_corpus(db_path: Path = DB_PATH, json_path: Path = JSON_PATH):
    """Importa les entrades del DIEC2 a la taula words de curiositats.db."""
    if not json_path.exists():
        raise FileNotFoundError(f"Fitxer JSON no trobat a: {json_path}")
    if not db_path.exists():
        raise FileNotFoundError(f"Base de dades SQLite no trobada a: {db_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        entries = json.load(f)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    inserted_count = 0
    skipped_count = 0

    for item in entries:
        raw_term = item.get("term", "")
        term = clean_term(raw_term)
        raw_cat = item.get("grammatical_category", "").strip()
        category = CATEGORY_MAP.get(raw_cat, "altres")
        definition = clean_definition(raw_term, item.get("full_definition", ""))
        dialectal_notes = format_dialectal_notes(item.get("matched_keywords", []))
        source_reference = "DIEC2 (Institut d'Estudis Catalans)"

        # Comprovació de duplicats (Idempotència)
        cursor.execute("SELECT id FROM words WHERE LOWER(TRIM(term)) = LOWER(TRIM(?))", (term,))
        row = cursor.fetchone()

        if row:
            skipped_count += 1
            continue

        cursor.execute(
            """
            INSERT INTO words (
                term,
                ipa_pronunciation,
                grammatical_category,
                definition,
                example_sentence,
                etymology,
                dialectal_notes,
                source_reference
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                term,
                None,
                category,
                definition,
                None,
                None,
                dialectal_notes,
                source_reference,
            ),
        )
        inserted_count += 1

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM words")
    total_words = cursor.fetchone()[0]
    conn.close()

    print(f"✅ Importació completada: {inserted_count} entrades inserides, {skipped_count} omeses (ja existents).")
    print(f"📊 Total de paraules a curiositats.db: {total_words}")
    return inserted_count, skipped_count, total_words


if __name__ == "__main__":
    import_diec_corpus()

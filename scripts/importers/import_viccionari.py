"""
Script d'importació i enriquiment del corpus dialectal del Viccionari a curiositats.db (Milestone M2 / R2).
Carrega database/viccionari_balear_entries.json, comprova els registres existents a la taula 'words',
enriqueix camps buits/nuls (AFI, etimologia, exemples) sense duplicar files i insereix els nous termes.
"""

import sys
import json
import sqlite3
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "curiositats.db"
JSON_PATH = BASE_DIR / "database" / "viccionari_balear_entries.json"


def import_viccionari_corpus(db_path: Path = DB_PATH, json_path: Path = JSON_PATH):
    """Importa i enriqueix les entrades del Viccionari a la taula words de curiositats.db."""
    if not json_path.exists():
        raise FileNotFoundError(f"Fitxer JSON no trobat a: {json_path}")
    if not db_path.exists():
        raise FileNotFoundError(f"Base de dades SQLite no trobada a: {db_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        entries = json.load(f)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    inserted_count = 0
    enriched_count = 0
    skipped_count = 0
    seen_in_batch = set()

    for item in entries:
        raw_term = item.get("term", "").strip()
        if not raw_term:
            continue

        term_key = raw_term.lower()

        ipa = item.get("ipa_pronunciation")
        gram_cat = item.get("grammatical_category") or "terme dialectal"
        definition = (item.get("definition") or "").strip()
        example = item.get("example_sentence")
        etymology = item.get("etymology")
        dialectal_notes = item.get("dialectal_notes")
        source_ref = item.get("source_reference") or "Viccionari (ca.wiktionary.org)"

        # Fallback de seguretat per garantir que cap definició quedi buida
        if not definition:
            definition = "Terme dialectal balear documentat al Viccionari."

        # Comprovació a la base de dades
        cursor.execute(
            """
            SELECT id, ipa_pronunciation, etymology, example_sentence, grammatical_category, definition, dialectal_notes, source_reference
            FROM words
            WHERE LOWER(TRIM(term)) = LOWER(TRIM(?))
            """,
            (raw_term,),
        )
        existing = cursor.fetchone()

        if existing:
            # Paraula ja existent: enriquir camps nuls o buits
            word_id = existing[0]
            db_ipa = existing[1]
            db_etym = existing[2]
            db_ex = existing[3]
            db_notes = existing[6]

            updates = []
            params = []

            if (not db_ipa or not db_ipa.strip()) and ipa:
                updates.append("ipa_pronunciation = ?")
                params.append(ipa)
            if (not db_etym or not db_etym.strip()) and etymology:
                updates.append("etymology = ?")
                params.append(etymology)
            if (not db_ex or not db_ex.strip()) and example:
                updates.append("example_sentence = ?")
                params.append(example)
            if (not db_notes or not db_notes.strip()) and dialectal_notes:
                updates.append("dialectal_notes = ?")
                params.append(dialectal_notes)

            if updates:
                params.append(word_id)
                query = f"UPDATE words SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, tuple(params))
                enriched_count += 1
            else:
                skipped_count += 1

            seen_in_batch.add(term_key)

        elif term_key in seen_in_batch:
            # Ja processat en aquest mateix lot (e.g. variació de majúscules/minúscules com taleca/Taleca)
            skipped_count += 1

        else:
            # Paraula nova: inserir a la taula words
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
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    raw_term,
                    ipa,
                    gram_cat[:50],
                    definition,
                    example,
                    etymology,
                    dialectal_notes[:150] if dialectal_notes else None,
                    source_ref[:255] if source_ref else None,
                ),
            )
            inserted_count += 1
            seen_in_batch.add(term_key)

    conn.commit()

    # Verificacions d'integritat
    cursor.execute("SELECT COUNT(*) FROM words")
    total_words = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT LOWER(TRIM(term)), COUNT(*) 
        FROM words 
        GROUP BY LOWER(TRIM(term)) 
        HAVING COUNT(*) > 1
        """
    )
    duplicates = cursor.fetchall()

    cursor.execute(
        """
        SELECT COUNT(*) 
        FROM words 
        WHERE term IS NULL OR TRIM(term) = '' OR definition IS NULL OR TRIM(definition) = ''
        """
    )
    empty_crucial = cursor.fetchone()[0]

    conn.close()

    print("\n" + "=" * 60)
    print("✅ RESULTATS DE LA IMPORTACIÓ DEL VICCIONARI BALEAR")
    print("=" * 60)
    print(f"📥 Entrades noves inserides: {inserted_count}")
    print(f"✨ Entrades existents enriquides: {enriched_count}")
    print(f"⏭️ Entrades ja actualitzades / omeses: {skipped_count}")
    print(f"📊 Total de paraules a curiositats.db: {total_words}")
    print(f"🔍 Duplicats detectats a words: {len(duplicates)}")
    print(f"⚠️ Entrades amb terme o definició buida: {empty_crucial}")
    print("=" * 60)

    if duplicates:
        print(f"❌ ALERTA: S'han detectat duplicats: {duplicates[:5]}")
    if empty_crucial > 0:
        print(f"❌ ALERTA: S'han detectat entrades sense terme o definició: {empty_crucial}")

    return {
        "inserted": inserted_count,
        "enriched": enriched_count,
        "skipped": skipped_count,
        "total_words": total_words,
        "duplicates": len(duplicates),
        "empty_crucial": empty_crucial,
    }


if __name__ == "__main__":
    import_viccionari_corpus()

"""
Crawler dirigit al Diccionari Català-Valencià-Balear (Alcover-Moll / DCVB) - Milestone M3 / Requirement R1.

Extreu lemes, accepcions, etimologia, transcripció fonètica i dites mallorquines/balears
mitjançant el motor BDLEX de l'Institut d'Estudis Catalans (IEC) i la interfície clàssica
del DCVB en fallback, amb memòria cau local en disc, control de concurrència i freqüència,
i persistència estructurada tant a fitxer JSON com a curiositats.db.
"""

import argparse
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import warnings
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore", category=UserWarning)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Endpoints oficials del DCVB / BDLEX
BDLEX_API_URL = "https://motor-bdlex.iec.cat/bdlex"
DCVB_LEGACY_URL = "https://dcvb.iec.cat/results.asp"

USER_AGENT = "CuriositatsBot/1.0 (Recerca dialectal; contacte@curiositats.cat)"
DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/xml, text/xml, */*",
}

# Regex per detectar marques dialectals balears / mallorquines
BALEARIC_GEO_PATTERN = re.compile(
    r"\b(mall|bal|men|eiv|forment|felanitx|manacor|palma|s[oó]ller|inquer|pollenc|ciutadella|eiviss)\w*",
    re.IGNORECASE,
)

# Normalització de categories gramaticals a català estàndard
POS_NORMALIZATION = {
    "m.": "nom masculí",
    "m": "nom masculí",
    "m.:": "nom masculí",
    "f.": "nom femení",
    "f": "nom femení",
    "f.:": "nom femení",
    "m. i f.": "nom masculí i femení",
    "m. i f.:": "nom masculí i femení",
    "mf.": "nom masculí i femení",
    "adj.": "adjectiu",
    "adj": "adjectiu",
    "adj.:": "adjectiu",
    "adj. i m.": "adjectiu i nom masculí",
    "adj. i f.": "adjectiu i nom femení",
    "v. tr.": "verb transitiu",
    "v. tr.:": "verb transitiu",
    "tr.": "verb transitiu",
    "v. intr.": "verb intransitiu",
    "v. intr.:": "verb intransitiu",
    "intr.": "verb intransitiu",
    "v. pron.": "verb pronominal",
    "v. pron.:": "verb pronominal",
    "v. refl.": "verb pronominal",
    "refl.": "verb pronominal",
    "v. tr. i intr.": "verb transitiu i intransitiu",
    "v.": "verb",
    "v.:": "verb",
    "adv.": "adverbi",
    "adv.:": "adverbi",
    "prep.": "preposició",
    "prep.:": "preposició",
    "interj.": "interjecció",
    "interj.:": "interjecció",
    "conj.": "conjunció",
    "conj.:": "conjunció",
    "loc. adv.": "locució adverbial",
    "loc. prep.": "locució prepositiva",
    "loc. conj.": "locució conjuntiva",
    "expr.": "expressió / frase feta",
    "frase feta": "expressió / frase feta",
    "refr.": "dita / refrany",
}


def clean_headword(raw_term: str) -> str:
    """Neteja el lema eliminant números d'homògrafs, sufixos secundaris i lletres sobrants."""
    if not raw_term:
        return ""
    # Si conté coma per a la forma femenina (ex. 'abacuador, -ora'), prendre la primera part
    term = raw_term.split(",")[0].strip()
    # Eliminar números d'homògrafs al final
    term = re.sub(r"\d+$", "", term).strip()
    # Eliminar signes de puntuació sobrants
    term = term.rstrip(";:.-, ")
    if not term:
        return ""
    # Capitalitzar la primera lletra
    return term[0].upper() + term[1:]


def normalize_pos(raw_pos: str) -> str:
    """Normalitza la categoria gramatical extreta del DCVB."""
    if not raw_pos:
        return "terme dialectal"
    cleaned = raw_pos.strip().lower()
    if cleaned in POS_NORMALIZATION:
        return POS_NORMALIZATION[cleaned]
    # Comprovar coincidències parcials
    for prefix, mapped in POS_NORMALIZATION.items():
        if cleaned.startswith(prefix):
            return mapped
    return "terme dialectal"


def format_dialectal_notes(geo_marks: list) -> str:
    """Formatta les marques geogràfiques trobades en una nota dialectal coherent."""
    places = []
    seen = set()
    for m in geo_marks:
        m_lower = m.lower()
        if "mall" in m_lower and "Mallorca" not in seen:
            seen.add("Mallorca")
            places.append("Mallorca")
        if "men" in m_lower and "Menorca" not in seen:
            seen.add("Menorca")
            places.append("Menorca")
        if "eiv" in m_lower and "Eivissa" not in seen:
            seen.add("Eivissa")
            places.append("Eivissa")
        if "forment" in m_lower and "Formentera" not in seen:
            seen.add("Formentera")
            places.append("Formentera")
        if "bal" in m_lower and "Balears" not in seen and not places:
            seen.add("Balears")
            places.append("Balears")

    if not places:
        return "Àmbit balear"
    if len(places) == 1:
        p = places[0]
        return f"Àmbit d'{p}" if p == "Eivissa" else f"Àmbit de {p}"
    return f"Àmbit balear ({', '.join(places)})"


def http_get(url: str, headers: dict = None, retries: int = 3, backoff: float = 2.0) -> bytes:
    """Executa una petició HTTP GET amb gestió de reintents i capçaleres personals."""
    req_headers = dict(DEFAULT_HEADERS)
    if headers:
        req_headers.update(headers)

    req = urllib.request.Request(url, headers=req_headers)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait_sec = float(e.headers.get("Retry-After", backoff * (attempt + 1)))
                time.sleep(wait_sec)
            elif attempt == retries - 1:
                raise
            else:
                time.sleep(backoff * (attempt + 1))
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(backoff * (attempt + 1))
    return b""


class DCVBCrawler:
    """Crawler dirigit per a l'extracció i processament de lemes balears del DCVB."""

    def __init__(
        self,
        cache_dir: Path = None,
        output_file: Path = None,
        db_path: Path = None,
        delay: float = 1.2,
        batch_size: int = 30,
    ):
        self.cache_dir = cache_dir or (PROJECT_ROOT / "database" / "dcvb_cache")
        self.output_file = output_file or (PROJECT_ROOT / "database" / "dcvb_extracted_entries.json")
        self.db_path = db_path or (PROJECT_ROOT / "curiositats.db")
        self.delay = delay
        self.batch_size = batch_size

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def fetch_dialect_entry_ids(self, force: bool = False) -> list:
        """Obté i deduplica els IDs de les entrades amb marques 'Mall' i 'Bal' del BDLEX."""
        ids_cache_file = self.cache_dir / "dcvb_dialect_ids.json"
        if not force and ids_cache_file.exists():
            try:
                with open(ids_cache_file, "r", encoding="utf-8") as f:
                    cached_ids = json.load(f)
                    if isinstance(cached_ids, list) and len(cached_ids) > 0:
                        print(f"📦 Carregats {len(cached_ids)} IDs des de la memòria cau ({ids_cache_file.name}).")
                        return cached_ids
            except Exception as e:
                print(f"  ⚠️ Error llegint cache d'IDs ({e}), es descarregaran de nou...")

        print("🔍 Consultant motor BDLEX per obtenir la llista d'IDs dialectals...")
        endpoints = [
            ("Mall", f"{BDLEX_API_URL}?text[]=Mall&dict[]=DCVB&element=entry&result_type=ids"),
            ("Bal", f"{BDLEX_API_URL}?text[]=Bal&dict[]=DCVB&element=entry&result_type=ids"),
        ]

        combined_ids = []
        seen = set()

        for label, url in endpoints:
            print(f"  • Descarregant IDs per a '{label}'...")
            raw_xml = http_get(url)
            time.sleep(self.delay)

            try:
                root = ET.fromstring(raw_xml.decode("utf-8", errors="replace"))
                entries = root.findall("entry")
                found_count = 0
                for el in entries:
                    if el.text:
                        eid = el.text.strip()
                        if eid and eid not in seen:
                            seen.add(eid)
                            combined_ids.append(eid)
                            found_count += 1
                print(f"    ✓ {len(entries)} IDs rebuts ({found_count} nous únics per a '{label}').")
            except Exception as e:
                print(f"    ❌ Error processant XML d'IDs per a '{label}': {e}")

        print(f"📊 Total d'IDs únics combinats preservant ordre: {len(combined_ids)}")
        try:
            with open(ids_cache_file, "w", encoding="utf-8") as f:
                json.dump(combined_ids, f, indent=2)
        except Exception as e:
            print(f"  ⚠️ No s'ha pogut guardar la memòria cau d'IDs: {e}")

        return combined_ids

    def fetch_entry_batch(self, batch_ids: list) -> list:
        """Descarrega un lot d'entrades per ID des del BDLEX o des de la memòria cau."""
        entries_xml = []
        missing_ids = []

        # 1. Comprovar cache per a cada ID
        for eid in batch_ids:
            entry_cache_file = self.cache_dir / f"{eid}.xml"
            if entry_cache_file.exists():
                try:
                    with open(entry_cache_file, "r", encoding="utf-8") as f:
                        entries_xml.append((eid, f.read()))
                except Exception:
                    missing_ids.append(eid)
            else:
                missing_ids.append(eid)

        # 2. Descarregar els IDs que falten en un únic batch request
        if missing_ids:
            query_str = "&".join(f"entry_id[]={eid}" for eid in missing_ids) + "&element=entry"
            url = f"{BDLEX_API_URL}?{query_str}"

            try:
                raw_data = http_get(url)
                time.sleep(self.delay)
                root = ET.fromstring(raw_data.decode("utf-8", errors="replace"))

                for entry_el in root.findall("entry"):
                    eid = entry_el.get("id")
                    if not eid:
                        continue
                    xml_str = ET.tostring(entry_el, encoding="unicode")
                    entries_xml.append((eid, xml_str))

                    # Guardar a la memòria cau
                    entry_cache_file = self.cache_dir / f"{eid}.xml"
                    try:
                        with open(entry_cache_file, "w", encoding="utf-8") as f:
                            f.write(xml_str)
                    except Exception:
                        pass
            except Exception as e:
                print(f"  ⚠️ Error descarregant lot de {len(missing_ids)} IDs: {e}")

        return entries_xml

    def parse_entry_xml(self, xml_content: str) -> dict:
        """Analitza l'XML TEI d'una entrada del DCVB i extreu l'estructura de dades."""
        try:
            entry = ET.fromstring(xml_content)
        except Exception:
            return None

        entry_id = entry.get("id")
        headword_attr = entry.get("headword", "")

        # 1. Lema / Terme
        orth_el = entry.find(".//orth")
        norm_attr = orth_el.attrib.get("norm") if orth_el is not None else None
        orth_text = orth_el.text.strip() if orth_el is not None and orth_el.text else ""
        raw_term = norm_attr or orth_text or headword_attr
        term = clean_headword(raw_term)
        if not term:
            return None

        # 2. Categoria gramatical
        pos_el = entry.find(".//gramGrp/pos")
        raw_pos = "".join(pos_el.itertext()).strip() if pos_el is not None else ""
        gram_cat = normalize_pos(raw_pos)

        # 3. Marques dialectals i filtratge
        geo_marks = set()
        for u in entry.findall(".//usg"):
            txt = "".join(u.itertext()).strip()
            if BALEARIC_GEO_PATTERN.search(txt):
                geo_marks.add(txt)
        for f in entry.findall(".//facet"):
            if f.attrib.get("name") == "geo":
                val = f.attrib.get("val", "")
                if BALEARIC_GEO_PATTERN.search(val):
                    geo_marks.add(val)

        # Si no conté cap marca geogràfica balear, descartar
        if not geo_marks:
            return None

        dialectal_notes = format_dialectal_notes(list(geo_marks))

        # 4. Accepcions i definicions
        definitions = []
        for s in entry.findall("sense"):
            loc = s.attrib.get("loc")
            if loc in ("FON", "ETI", "CUP"):
                continue

            def_el = s.find("def")
            dfse_el = s.find(".//dfse")
            target_el = def_el if def_el is not None else dfse_el

            if target_el is not None:
                def_text = "".join(target_el.itertext()).strip()
                def_text = def_text.rstrip(";,-. ")
                if def_text:
                    definitions.append(def_text)

        if not definitions:
            full_definition = "Terme dialectal balear documentat al Diccionari Català-Valencià-Balear."
        elif len(definitions) == 1:
            full_definition = definitions[0]
            if not full_definition.endswith("."):
                full_definition += "."
        else:
            numbered = [f"{i}. {d.rstrip('.') + '.'}" for i, d in enumerate(definitions[:6], 1)]
            full_definition = " ".join(numbered)

        # 5. Transcripció fonètica (AFI/IPA)
        ipa_pronunciation = None
        fon_senses = [s for s in entry.findall("sense") if s.attrib.get("loc") == "FON"]
        if fon_senses:
            # Buscar si hi ha una pron específica balear/mallorquina
            bal_pron = None
            gen_pron = None
            for form in fon_senses[0].findall(".//form"):
                usg_el = form.find(".//usg")
                usg_text = "".join(usg_el.itertext()).strip() if usg_el is not None else ""
                f1_el = form.find(".//f1")
                pron_el = form.find(".//pron")
                target_p = f1_el if f1_el is not None else pron_el
                if target_p is not None:
                    p_text = "".join(target_p.itertext()).strip()
                    if p_text:
                        if not gen_pron:
                            gen_pron = p_text
                        if BALEARIC_GEO_PATTERN.search(usg_text):
                            bal_pron = p_text
                            break

            selected_pron = bal_pron or gen_pron
            if selected_pron:
                ipa_pronunciation = f"[{selected_pron}]" if not selected_pron.startswith("[") else selected_pron

        # 6. Etimologia
        etymology = None
        eti_senses = [s for s in entry.findall("sense") if s.attrib.get("loc") == "ETI"]
        if eti_senses:
            etym_el = eti_senses[0].find(".//etym")
            if etym_el is not None:
                etym_text = "".join(etym_el.itertext()).strip()
                etym_text = re.sub(r"^Etim\.?:\s*", "", etym_text, flags=re.IGNORECASE).strip()
                if etym_text:
                    etymology = etym_text[0].upper() + etym_text[1:]

        # 7. Dites, refranys i exemples
        sayings = []
        for eg in entry.findall(".//eg"):
            for child in eg.iter():
                if child.tag == "quote":
                    q_text = "".join(child.itertext()).strip()
                    if q_text and q_text not in sayings:
                        sayings.append(q_text)
                elif child.tag == "q" and child.attrib.get("type") in ("RF", "EX"):
                    q_text = "".join(child.itertext()).strip()
                    if q_text and q_text not in sayings:
                        sayings.append(q_text)

        example_sentence = None
        if sayings:
            # Preferir refranys o dites
            example_sentence = sayings[0].strip()
            # Netejar barres verticals internes de versos (' | ')
            example_sentence = re.sub(r"\s*\|\s*", " / ", example_sentence)

        dcvb_url = f"https://dcvb.iec.cat/results.asp?Word={urllib.parse.quote(term.lower())}"

        return {
            "id": entry_id,
            "term": term,
            "raw_term": raw_term,
            "grammatical_category": gram_cat,
            "raw_pos": raw_pos,
            "definition": full_definition,
            "ipa_pronunciation": ipa_pronunciation,
            "etymology": etymology,
            "dialectal_notes": dialectal_notes,
            "sayings": sayings,
            "example_sentence": example_sentence,
            "source_reference": "Diccionari Català-Valencià-Balear (Alcover-Moll)",
            "dcvb_url": dcvb_url,
        }

    def fetch_legacy_dcvb(self, term: str) -> dict:
        """Cerca un terme directament a la interfície clàssica dcvb.iec.cat (ISO-8859-1)."""
        print(f"🌐 Consultant interfície clàssica DCVB per a '{term}'...")
        encoded_term = urllib.parse.quote(term.encode("latin1", errors="replace"))
        url = f"{DCVB_LEGACY_URL}?Word={encoded_term}"

        try:
            raw_bytes = http_get(url)
            html_text = raw_bytes.decode("latin1", errors="replace")
            soup = BeautifulSoup(html_text, "html.parser")

            body_text = soup.get_text()
            if "No s'ha trobat cap article" in body_text:
                print(f"  ❌ Cap article trobat al DCVB per a '{term}'.")
                return None

            clean_t = clean_headword(term)

            # Extracció de fonètica
            ipa = None
            font_tags = soup.find_all("font")
            for ft in font_tags:
                txt = ft.get_text().strip()
                if txt and any(c in txt for c in "əβðɣʃʒɔɛ"):
                    ipa = f"[{txt}]"
                    break

            # Extracció de definició
            definition = "Terme documentat al Diccionari Català-Valencià-Balear (Alcover-Moll)."
            lines = [line.strip() for line in body_text.splitlines() if line.strip()]
            for line in lines:
                if (
                    clean_t.upper() in line
                    and "||" in line
                    and not line.startswith("Consulta")
                ):
                    parts = line.split("||", 1)
                    if len(parts) > 1:
                        definition = parts[1].strip()
                        break

            return {
                "id": f"DCVB_LEGACY_{clean_t}",
                "term": clean_t,
                "raw_term": term,
                "grammatical_category": "terme dialectal",
                "raw_pos": "",
                "definition": definition,
                "ipa_pronunciation": ipa,
                "etymology": None,
                "dialectal_notes": "Àmbit balear",
                "sayings": [],
                "example_sentence": None,
                "source_reference": "Diccionari Català-Valencià-Balear (Alcover-Moll)",
                "dcvb_url": url,
            }
        except Exception as e:
            print(f"  ⚠️ Error en la consulta clàssica del DCVB: {e}")
            return None

    def crawl(self, limit: int = 100, force_ids: bool = False) -> list:
        """Execució del crawler amb control de freqüència, extracció i persistència JSON."""
        print("=" * 70)
        print("  INICIANT CRAWLER DEL DCVB (ALCOVER-MOLL)")
        print("=" * 70)
        print(f"  Objectiu        : {'Tots els lemes' if limit is None else f'{limit} entrades'}")
        print(f"  Mida del lot    : {self.batch_size} IDs/petició")
        print(f"  Pausa de cortesia: {self.delay}s entre peticions")
        print(f"  Memòria cau     : {self.cache_dir}")
        print(f"  Sortida JSON    : {self.output_file}")
        print("=" * 70)

        start_time = time.time()
        all_ids = self.fetch_dialect_entry_ids(force=force_ids)

        extracted_entries = []
        seen_terms = set()
        processed_ids = 0

        # Iterar en blocs segons self.batch_size
        for i in range(0, len(all_ids), self.batch_size):
            chunk = all_ids[i : i + self.batch_size]
            processed_ids += len(chunk)

            raw_batch = self.fetch_entry_batch(chunk)
            for eid, xml_str in raw_batch:
                parsed = self.parse_entry_xml(xml_str)
                if parsed:
                    term_key = parsed["term"].lower()
                    if term_key not in seen_terms:
                        seen_terms.add(term_key)
                        extracted_entries.append(parsed)

                if limit is not None and len(extracted_entries) >= limit:
                    break

            elapsed = time.time() - start_time
            print(
                f"  -> Processats {processed_ids}/{len(all_ids)} IDs | "
                f"Extretes {len(extracted_entries)}{f'/{limit}' if limit else ''} entrades balears "
                f"({elapsed:.1f}s)..."
            )

            if limit is not None and len(extracted_entries) >= limit:
                print(f"🎯 S'ha assolit el límit d'entrades sol·licitat ({limit}).")
                break

        # Persistència JSON
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(extracted_entries, f, ensure_ascii=False, indent=2)

        total_time = time.time() - start_time
        print("\n" + "=" * 70)
        print("  RESUM DE L'EXTRACCIÓ DEL DCVB")
        print("=" * 70)
        print(f"  Total d'entrades vàlides extretes: {len(extracted_entries)}")
        print(f"  Temps transcorregut               : {total_time:.2f} segons")
        print(f"  Fitxer de resultats generat       : {self.output_file}")
        print("=" * 70)

        return extracted_entries

    def import_to_database(self, entries: list = None) -> dict:
        """Importa i enriqueix les entrades del DCVB a la taula 'words' de curiositats.db."""
        if entries is None:
            if not self.output_file.exists():
                raise FileNotFoundError(f"No s'ha trobat el fitxer {self.output_file}")
            with open(self.output_file, "r", encoding="utf-8") as f:
                entries = json.load(f)

        if not self.db_path.exists():
            raise FileNotFoundError(f"No s'ha trobat la base de dades SQLite a {self.db_path}")

        print("\n💾 Iniciant importació / enriquiment a curiositats.db...")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        inserted_count = 0
        enriched_count = 0
        skipped_count = 0
        seen_in_batch = set()

        for item in entries:
            term = item.get("term", "").strip()
            if not term:
                continue

            term_key = term.lower()
            if term_key in seen_in_batch:
                skipped_count += 1
                continue

            ipa = item.get("ipa_pronunciation")
            gram_cat = item.get("grammatical_category") or "terme dialectal"
            definition = (item.get("definition") or "").strip()
            if not definition:
                definition = "Terme dialectal balear documentat al Diccionari Català-Valencià-Balear."
            example = item.get("example_sentence")
            etymology = item.get("etymology")
            dialectal_notes = item.get("dialectal_notes")
            source_ref = item.get("source_reference") or "Diccionari Català-Valencià-Balear (Alcover-Moll)"

            cursor.execute(
                """
                SELECT id, ipa_pronunciation, etymology, example_sentence, dialectal_notes, source_reference
                FROM words
                WHERE LOWER(TRIM(term)) = LOWER(TRIM(?))
                """,
                (term,),
            )
            existing = cursor.fetchone()

            if existing:
                word_id, db_ipa, db_etym, db_ex, db_notes, db_source = existing
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

            else:
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
                        term,
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

        # Verificacions d'integritat immediates
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
        empty_records = cursor.fetchone()[0]

        conn.close()

        print("=" * 70)
        print("  RESULTATS DE LA INGESTA A CURIOSITATS.DB")
        print("=" * 70)
        print(f"  Noves entrades DCVB inserides : {inserted_count}")
        print(f"  Entrades existents enriquides  : {enriched_count}")
        print(f"  Entrades ja completes / omeses : {skipped_count}")
        print(f"  Total actual de paraules       : {total_words}")
        print(f"  Duplicats detectats            : {len(duplicates)}")
        print(f"  Camps obligatoris buits/nuls   : {empty_records}")
        print("=" * 70)

        if duplicates:
            raise ValueError(f"S'han detectat duplicats després de la ingesta: {duplicates}")
        if empty_records > 0:
            raise ValueError(f"S'han detectat entrades amb lema o definició buits: {empty_records}")

        return {
            "inserted": inserted_count,
            "enriched": enriched_count,
            "skipped": skipped_count,
            "total_words": total_words,
            "duplicates": len(duplicates),
            "empty_records": empty_records,
        }


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Crawler dirigit al DCVB (Alcover-Moll) per a 'Una teringa de curiositats'"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Límit d'entrades balears a extreure (per defecte: 100 per al lot inicial representatiu)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Executar l'extracció massiva completa de tots els lemes balears",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=30,
        help="Nombre d'IDs per petició al BDLEX (per defecte: 30)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.2,
        help="Segons d'espera entre peticions per respectar el servidor de l'IEC (per defecte: 1.2s)",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=PROJECT_ROOT / "database" / "dcvb_cache",
        help="Ruta al directori de memòria cau per als fitxers XML (per defecte: database/dcvb_cache)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "database" / "dcvb_extracted_entries.json",
        help="Ruta al fitxer JSON de sortida (per defecte: database/dcvb_extracted_entries.json)",
    )
    parser.add_argument(
        "--import-to-db",
        action="store_true",
        help="Importar i enriquir les dades extretes directament a curiositats.db",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=PROJECT_ROOT / "curiositats.db",
        help="Ruta a la base de dades SQLite curiositats.db",
    )
    parser.add_argument(
        "--term",
        type=str,
        default=None,
        help="Cercar un terme individual (utilitza BDLEX i fallback al DCVB clàssic)",
    )
    parser.add_argument(
        "--force-ids",
        action="store_true",
        help="Forçar la recàrrega de la llista d'IDs sense utilitzar la memòria cau",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    crawler = DCVBCrawler(
        cache_dir=args.cache_dir,
        output_file=args.output,
        db_path=args.db_path,
        delay=args.delay,
        batch_size=args.batch_size,
    )

    if args.term:
        print(f"🔎 Cerca individual per al terme '{args.term}'...")
        # Primer provar a BDLEX
        term_enc = urllib.parse.quote(args.term)
        url = f"{BDLEX_API_URL}?text[]={term_enc}&dict[]=DCVB&element=entry"
        raw_xml = http_get(url)
        parsed = None

        try:
            root = ET.fromstring(raw_xml.decode("utf-8", errors="replace"))
            for entry_el in root.findall("entry"):
                hw = entry_el.get("headword", "")
                orth = entry_el.find(".//orth")
                ot = orth.text.strip() if orth is not None and orth.text else ""
                if (
                    args.term.lower() == hw.lower()
                    or args.term.lower() == ot.lower()
                    or args.term.lower() in hw.lower()
                ):
                    parsed = crawler.parse_entry_xml(ET.tostring(entry_el, encoding="unicode"))
                    if parsed:
                        break
        except Exception:
            pass

        if not parsed:
            parsed = crawler.fetch_legacy_dcvb(args.term)

        if parsed:
            print(f"\n✅ Resultat trobat per a '{args.term}':")
            print(json.dumps(parsed, ensure_ascii=False, indent=2))
            if args.import_to_db:
                crawler.import_to_database([parsed])
        else:
            print(f"❌ No s'ha trobat cap entrada per a '{args.term}'.")
        return

    limit = None if args.all else args.limit
    extracted = crawler.crawl(limit=limit, force_ids=args.force_ids)

    if args.import_to_db:
        crawler.import_to_database(extracted)


if __name__ == "__main__":
    main()

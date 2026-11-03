"""
Scraper per extreure el corpus dialectal del Viccionari (Milestone M2 / R2).
Extreu la totalitat de lemes de les categories 'Mallorquí' i 'Balear' de ca.wiktionary.org,
analitza l'HTML de cada pàgina (AFI/IPA, definicions, exemples, etimologia, categoria gramatical,
marques dialectals i enllaços al DCVB) i persisteix les dades estructurades a
database/viccionari_balear_entries.json.
"""

import sys
import json
import time
import re
import copy
import urllib.request
import urllib.error
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from bs4 import BeautifulSoup

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_FILE = BASE_DIR / "database" / "viccionari_balear_entries.json"

API_URL = "https://ca.wiktionary.org/w/api.php"
USER_AGENT = "CuriositatsBot/1.0 (contact@curiositats.cat)"
HEADERS = {"User-Agent": USER_AGENT}

CATEGORIES = ["Categoria:Mallorquí", "Categoria:Balear"]
MAX_WORKERS = 4
REQUEST_DELAY = 0.35


def fetch_category_members(category_title: str) -> list:
    """Obté la llista de membres (pàgines canòniques) d'una categoria del Viccionari."""
    members = []
    cmcontinue = None

    print(f"🔍 Obtenint membres de '{category_title}'...")
    while True:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": category_title,
            "cmlimit": "500",
            "cmtype": "page",
            "format": "json",
        }
        if cmcontinue:
            params["cmcontinue"] = cmcontinue

        url = f"{API_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers=HEADERS)

        for attempt in range(5):
            try:
                with urllib.request.urlopen(req, timeout=20) as res:
                    data = json.loads(res.read().decode("utf-8"))
                    new_members = data.get("query", {}).get("categorymembers", [])
                    members.extend(new_members)
                    if "continue" in data and "cmcontinue" in data["continue"]:
                        cmcontinue = data["continue"]["cmcontinue"]
                    else:
                        cmcontinue = None
                    break
            except Exception as e:
                wait_time = 3.0 * (attempt + 1)
                if isinstance(e, urllib.error.HTTPError) and e.code == 429:
                    retry_after = e.headers.get("Retry-After")
                    wait_time = int(retry_after) + 1 if retry_after else 6.0 * (attempt + 1)
                if attempt == 4:
                    raise RuntimeError(f"Error obtenint membres de {category_title}: {e}")
                time.sleep(wait_time)

        if not cmcontinue:
            break

    print(f"  • {category_title}: {len(members)} pàgines trobades.")
    return members


def collect_unique_pages():
    """Recull i combina els membres de Mallorquí i Balear deduplicant per pageid."""
    pages_by_id = {}

    for cat_name in CATEGORIES:
        short_name = "Mallorquí" if "Mallorquí" in cat_name else "Balear"
        members = fetch_category_members(cat_name)
        for m in members:
            pid = m["pageid"]
            title = m["title"]
            if pid not in pages_by_id:
                pages_by_id[pid] = {
                    "pageid": pid,
                    "term": title,
                    "categories": [short_name],
                }
            else:
                if short_name not in pages_by_id[pid]["categories"]:
                    pages_by_id[pid]["categories"].append(short_name)

    print(f"\n📊 Total de pàgines úniques deduplicades: {len(pages_by_id)}")
    return list(pages_by_id.values())


def isolate_catalan_section(soup: BeautifulSoup) -> BeautifulSoup:
    """Aïlla els elements DOM que pertanyen a la secció en català (== Català ==)."""
    cat_h2 = soup.find(
        lambda tag: tag.name == "h2"
        and ("Català" in tag.get_text() or tag.get("id") == "Català")
    )
    if not cat_h2:
        return soup

    container = (
        cat_h2.parent
        if cat_h2.parent and "mw-heading2" in cat_h2.parent.get("class", [])
        else cat_h2
    )

    nodes = []
    for sib in container.next_siblings:
        if getattr(sib, "name", None):
            if (
                sib.name == "h2"
                or "mw-heading2" in sib.get("class", [])
                or sib.find("h2")
            ):
                break
        nodes.append(str(sib))

    return BeautifulSoup("<div>" + "".join(nodes) + "</div>", "html.parser")


def extract_ipa_pronunciation(cat_soup: BeautifulSoup) -> str | None:
    """Extreu la transcripció fonètica AFI/IPA prioritzant les marques Balear/Mallorquí/Oriental."""
    candidates = []
    for span in cat_soup.find_all("span", class_="IPA"):
        ipa_text = span.get_text().strip()
        if not ipa_text:
            continue

        context = ""
        p = span
        for _ in range(3):
            if p.parent:
                p = p.parent
                context += " " + p.get_text()
            else:
                break
        context_lower = context.lower()

        priority = 3
        if any(d in context_lower for d in ["balear", "mallorqu", "menorqu", "eiviss"]):
            priority = 1
        elif "oriental" in context_lower:
            priority = 2

        candidates.append((priority, ipa_text))

    if candidates:
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]
    return None


def extract_grammatical_category(cat_soup: BeautifulSoup) -> str:
    """Extreu la categoria gramatical a partir de l'encapçalament i de les etiquetes abbr."""
    valid_headings = [
        ("nom propi", "nom propi"),
        ("nom", "nom"),
        ("verb", "verb"),
        ("adjectiu", "adjectiu"),
        ("adverbi", "adverbi"),
        ("interjecció", "interjecció"),
        ("conjunció", "conjunció"),
        ("preposició", "preposició"),
        ("pronom", "pronom"),
        ("article", "article"),
        ("contracció", "contracció"),
        ("numeral", "numeral"),
        ("locució nominal", "locució nominal"),
        ("locució verbal", "locució verbal"),
        ("locució adverbial", "locució adverbial"),
        ("locució adjectival", "locució adjectival"),
        ("locució interjectiva", "locució interjectiva"),
        ("locució", "locució"),
        ("expressió", "expressió"),
        ("frase feta", "frase feta"),
        ("dita", "dita"),
        ("refrany", "dita"),
    ]

    for h in cat_soup.find_all(["h3", "h4", "h5"]):
        h_text = h.get_text().strip().lower()
        matched_cat = None
        for pattern, label in valid_headings:
            if pattern in h_text:
                matched_cat = label
                break

        if matched_cat:
            container = (
                h.parent
                if h.parent and "mw-heading" in h.parent.get("class", [])
                else h
            )
            p = container.find_next_sibling("p")
            abbr_info = []
            if p:
                for abbr in p.find_all("abbr"):
                    title = abbr.get("title", "").lower()
                    text = abbr.get_text().strip().lower()
                    abbr_info.append((text, title))

            gender = ""
            for txt, title in abbr_info:
                if "femení" in title or "femení" in txt:
                    if "masculí" in title or "masculí" in txt:
                        gender = "masculí i femení"
                    else:
                        gender = "femení"
                elif "masculí" in title or "masculí" in txt:
                    gender = "masculí"
                elif "intransitiu" in title or "intr." in txt:
                    gender = "intransitiu"
                elif "transitiu" in title or "trans." in txt:
                    gender = "transitiu"
                elif "pronominal" in title or "pron." in txt:
                    gender = "pronominal"

            if matched_cat == "nom":
                return f"nom {gender}".strip() if gender else "nom"
            elif matched_cat == "verb":
                return f"verb {gender}".strip() if gender else "verb"
            elif matched_cat == "adjectiu":
                return f"adjectiu {gender}".strip() if gender and "femení" in gender else "adjectiu"
            else:
                return matched_cat

    return "terme dialectal"


def clean_text_formatting(text: str) -> str:
    """Neteja espais redundants i puntuació en text extret."""
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^\(\s*\)\s*", "", text).strip()
    text = re.sub(r"\s+([,.:;?!])", r"\1", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(r"‘\s+", "‘", text)
    text = re.sub(r"\s+’", "’", text)
    text = text.replace("\u200e", "").replace("\xa0", " ").strip()
    return text


def extract_definitions_and_examples(cat_soup: BeautifulSoup, fallback_soup: BeautifulSoup):
    """Extreu la definició (o definicions unides) i oracions d'exemple, a més de marques dialectals."""
    defs = []
    examples = []
    dialect_tags = set()

    target_soup = cat_soup if cat_soup.find("ol") else fallback_soup

    for ol in target_soup.find_all("ol"):
        for rli in ol.find_all("li", recursive=False):
            li = copy.copy(rli)

            # 1. Extreure etiquetes dialectals de marques de context (span.ib-content)
            for ib in li.find_all("span", class_="ib-content"):
                tag_txt = ib.get_text().strip()
                if tag_txt:
                    for part in re.split(r"[,;]+", tag_txt):
                        p_clean = part.strip().capitalize()
                        if p_clean and p_clean.lower() in [
                            "mallorquí",
                            "balear",
                            "menorquí",
                            "eivissenc",
                            "formenterer",
                            "valencià",
                        ]:
                            dialect_tags.add(p_clean)

            # 2. Extreure exemples abans de modificar li
            for ex in li.find_all(class_="h-usage-example"):
                txt = clean_text_formatting(ex.get_text())
                if txt and txt not in examples:
                    examples.append(txt)
            for dl in li.find_all("dl"):
                for i_tag in dl.find_all("i"):
                    txt = clean_text_formatting(i_tag.get_text())
                    if txt and txt not in examples:
                        examples.append(txt)

            # 3. Eliminar elements auxiliars, llistes niades i exemples
            selectors_to_remove = [
                "dl",
                "ul",
                "ol",
                "table",
                ".ib-brac",
                ".ib-content",
                ".h-usage-example",
                ".e-example",
            ]
            for selector in selectors_to_remove:
                for t in li.select(selector):
                    t.decompose()

            clean_def = clean_text_formatting(li.get_text(separator=" "))
            if clean_def:
                defs.append(clean_def)

    # Fallback si <ol> no conté definicions vàlides
    if not defs:
        for p in target_soup.find_all("p"):
            p_text = clean_text_formatting(p.get_text())
            if p_text and len(p_text) > 10 and not p_text.startswith("Pronúncia"):
                defs.append(p_text)
                break

    full_definition = " / ".join(defs) if defs else "Terme documentat al Viccionari dialectal balear."
    example_sentence = " / ".join(examples) if examples else None

    return full_definition, example_sentence, list(dialect_tags)


def extract_etymology(cat_soup: BeautifulSoup, fallback_soup: BeautifulSoup) -> str | None:
    """Extreu l'etimologia a partir de la secció o paràgraf corresponent."""
    for soup in [cat_soup, fallback_soup]:
        for tag in soup.find_all(["li", "p", "dd", "div"]):
            txt = tag.get_text().strip()
            m = re.match(r"^(?:[-*•\s]*)\bEtimologia\b\s*[:.-]?\s*(.*)", txt, flags=re.IGNORECASE)
            if m:
                etym = clean_text_formatting(m.group(1))
                etym = re.sub(r"^[–:.-]\s*", "", etym).strip()
                if etym:
                    return etym
    return None


def extract_dcvb_info(soup: BeautifulSoup) -> tuple[str | None, str]:
    """Cerca enllaços directes al Diccionari Català-Valencià-Balear (Alcover-Moll)."""
    for a in soup.find_all("a"):
        href = a.get("href", "")
        if "dcvb.iec.cat" in href or ("dcvb" in href and "results.asp" in href):
            clean_href = href.strip()
            return clean_href, f"Viccionari [DCVB: {clean_href}]"

    return None, "Viccionari (ca.wiktionary.org)"


def parse_page(page_info: dict) -> dict | None:
    """Descarrega i analitza les dades d'una pàgina específica del Viccionari."""
    time.sleep(REQUEST_DELAY)

    pageid = page_info["pageid"]
    term = page_info["term"]
    base_cats = page_info["categories"]

    params = {
        "action": "parse",
        "pageid": pageid,
        "prop": "text|categories|sections",
        "format": "json",
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers=HEADERS)

    data = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=20) as res:
                data = json.loads(res.read().decode("utf-8"))
                break
        except Exception as e:
            wait_time = 2.0 * (attempt + 1)
            if isinstance(e, urllib.error.HTTPError) and e.code == 429:
                retry_after = e.headers.get("Retry-After")
                wait_time = int(retry_after) + 1 if retry_after else 5.0 * (attempt + 1)
            if attempt == 4:
                print(f"❌ Error descarregant pàgina {pageid} ({term}): {e}")
                return None
            time.sleep(wait_time)

    if not data or "parse" not in data:
        return None

    parse_data = data["parse"]
    raw_html = parse_data.get("text", {}).get("*", "")
    full_soup = BeautifulSoup(raw_html, "html.parser")
    cat_soup = isolate_catalan_section(full_soup)

    ipa = extract_ipa_pronunciation(cat_soup)
    gram_cat = extract_grammatical_category(cat_soup)
    definition, example_sentence, extra_tags = extract_definitions_and_examples(cat_soup, full_soup)
    etymology = extract_etymology(cat_soup, full_soup)
    dcvb_url, source_reference = extract_dcvb_info(full_soup)

    # Combinació ordenada de notes dialectals
    all_notes = list(base_cats)
    for tag in extra_tags:
        if tag not in all_notes:
            all_notes.append(tag)
    dialectal_notes = ", ".join(all_notes)
    if len(dialectal_notes) > 150:
        dialectal_notes = dialectal_notes[:147] + "..."

    return {
        "pageid": pageid,
        "term": term,
        "categories": base_cats,
        "ipa_pronunciation": ipa,
        "grammatical_category": gram_cat[:50],
        "definition": definition,
        "example_sentence": example_sentence,
        "etymology": etymology,
        "dialectal_notes": dialectal_notes,
        "dcvb_url": dcvb_url,
        "source_reference": source_reference[:255],
    }


def load_cached_entries() -> dict:
    """Carrega les entrades ja extretes prèviament per permetre execució incremental / resumable."""
    if not OUTPUT_FILE.exists():
        return {}
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            cached = {}
            for item in data:
                if item.get("pageid") and item.get("definition"):
                    cached[item["pageid"]] = item
            return cached
    except Exception:
        return {}


def scrape_all_viccionari_balear():
    """Execució principal de l'extracció massiva del corpus dialectal."""
    print("🚀 Iniciant l'extracció del corpus dialectal del Viccionari (M2 / R2)...")
    start_time = time.time()

    pages = collect_unique_pages()
    total_pages = len(pages)

    cached_entries = load_cached_entries()
    print(f"📦 Entrades vàlides ja existents en memòria cau: {len(cached_entries)}/{total_pages}")

    missing_pages = [p for p in pages if p["pageid"] not in cached_entries]
    print(f"📥 Descarregant i analitzant {len(missing_pages)} entrades pendents amb {MAX_WORKERS} fils concurrents...")

    extracted_dict = dict(cached_entries)
    completed_count = len(cached_entries)

    if missing_pages:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_page = {executor.submit(parse_page, p): p for p in missing_pages}
            for future in as_completed(future_to_page):
                entry = future.result()
                completed_count += 1
                if entry:
                    extracted_dict[entry["pageid"]] = entry

                if completed_count % 50 == 0 or completed_count == total_pages:
                    elapsed = time.time() - start_time
                    print(f"  -> Total processat: {completed_count}/{total_pages} ({elapsed:.1f}s)...")
                    # Desa un punt de control intermedi
                    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                        json.dump(list(extracted_dict.values()), f, ensure_ascii=False, indent=2)

    all_entries = list(extracted_dict.values())
    all_entries.sort(key=lambda x: x["term"].lower())

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)

    total_time = time.time() - start_time
    dcvb_count = sum(1 for e in all_entries if e.get("dcvb_url"))
    ipa_count = sum(1 for e in all_entries if e.get("ipa_pronunciation"))
    etym_count = sum(1 for e in all_entries if e.get("etymology"))

    print(f"\n✅ Extracció completada amb èxit en {total_time:.2f} segons.")
    print(f"📄 Fitxer generat: {OUTPUT_FILE}")
    print(f"📊 Estadístiques:")
    print(f"  • Total d'entrades persistides: {len(all_entries)}/{total_pages}")
    print(f"  • Entrades amb enllaç al DCVB: {dcvb_count} ({dcvb_count/len(all_entries)*100:.1f}%)")
    print(f"  • Entrades amb transcripció AFI/IPA: {ipa_count} ({ipa_count/len(all_entries)*100:.1f}%)")
    print(f"  • Entrades amb etimologia: {etym_count} ({etym_count/len(all_entries)*100:.1f}%)")

    return all_entries


if __name__ == "__main__":
    scrape_all_viccionari_balear()

"""
Script per consultar i extreure les entrades del DIEC2 que contenen referències explícites
a l'àmbit balear (Mallorca, Menorca, Eivissa, Formentera, Balears).
"""

import sys
import json
import time
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_FILE = BASE_DIR / "database" / "diec_balear_entries.json"

KEYWORDS = [
    "Mallorca",
    "Menorca",
    "Eivissa",
    "Formentera",
    "Balears",
    "balear",
    "mallorquí",
    "menorquí",
    "eivissenc",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "X-Requested-With": "XMLHttpRequest",
}


def search_diec_keywords():
    found_entries = {}
    print("🔍 Cercant termes al DIEC2 amb criteris geogràfics balears...")

    for kw in KEYWORDS:
        data = urllib.parse.urlencode({"DefinicioText": kw, "OperDef": "2"}).encode("utf-8")
        req = urllib.request.Request(
            "https://dlc.iec.cat/AdvancedSearch/Search",
            data=data,
            headers={"User-Agent": HEADERS["User-Agent"]},
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as res:
                soup = BeautifulSoup(res.read(), "html.parser")
                anchors = soup.find_all("a", {"class": "resultAnchor"})
                print(f"  • Cerca '{kw}': {len(anchors)} entrades trobades.")
                for a in anchors:
                    term = a.get_text(strip=True)
                    entry_id = a.get("id")
                    if entry_id not in found_entries:
                        found_entries[entry_id] = {
                            "id": entry_id,
                            "term": term,
                            "matched_keywords": [kw],
                        }
                    else:
                        if kw not in found_entries[entry_id]["matched_keywords"]:
                            found_entries[entry_id]["matched_keywords"].append(kw)
        except Exception as e:
            print(f"  ❌ Error cercant '{kw}': {e}")
        time.sleep(0.3)

    print(f"\n📊 Total d'entrades úniques trobades al DIEC2: {len(found_entries)}")
    return found_entries


def fetch_definitions(entries):
    print("\n📥 Descarregant les definicions completes del DIEC2...")
    enriched = []
    total = len(entries)

    for i, (entry_id, info) in enumerate(entries.items(), start=1):
        url = "https://dlc.iec.cat/Results/Accepcio"
        post_data = urllib.parse.urlencode({"id": entry_id}).encode("utf-8")
        req = urllib.request.Request(url, data=post_data, headers=HEADERS)

        try:
            with urllib.request.urlopen(req, timeout=15) as res:
                payload = json.loads(res.read().decode("utf-8"))
                html_content = payload.get("content", "")
                soup = BeautifulSoup(html_content, "html.parser")

                title_tag = soup.find("span", {"class": "title"})
                title = title_tag.get_text(strip=True) if title_tag else info["term"]

                tagline_tag = soup.find("span", {"class": "tagline"})
                gram_cat = tagline_tag.get_text(strip=True) if tagline_tag else ""

                full_text = soup.get_text(separator=" ", strip=True)

                enriched.append({
                    "id": entry_id,
                    "term": title,
                    "grammatical_category": gram_cat,
                    "full_definition": full_text,
                    "matched_keywords": info["matched_keywords"],
                    "source": "DIEC2 (Institut d'Estudis Catalans)",
                })
        except Exception as e:
            print(f"  ⚠️ Error a {info['term']} ({entry_id}): {e}")

        if i % 15 == 0 or i == total:
            print(f"  -> Processades {i}/{total} entrades...")
        time.sleep(0.15)

    return enriched


def main():
    entries = search_diec_keywords()
    enriched = fetch_definitions(entries)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Fitxer generat amb èxit a: {OUTPUT_FILE}")
    print("Mostra dels primers 5 termes extrets:")
    for item in enriched[:5]:
        print(f"  • {item['term']} ({item['grammatical_category']}): {item['full_definition'][:100]}...")


if __name__ == "__main__":
    main()

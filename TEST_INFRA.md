# Infraestructura de Proves E2E — Una teringa de curiositats

Aquest document descriu l'arquitectura, metodologia i procediments d'execució de la suite de proves automatitzades de caixa opaca (opaque-box testing) per al projecte **«Una teringa de curiositats»**.

---

## 1. Visió General i Filosofia

La infraestructura de proves s'ha dissenyat per oferir una verificació independent, estricta i exhaustiva de tots els requisits del projecte (**R1 a R5**), seguint els principis següents:

1. **Zero dependències externes**: S'executa exclusivament sobre la biblioteca estàndard de Python 3 (`unittest`, `sqlite3`, `urllib.request`, `json`, `threading`, `subprocess`), sense necessitat de paquets externs com `pytest` o `requests`.
2. **Caixa opaca (Opaque-box)**: Avalua el comportament observable externament (respostes HTTP, codis d'estat, contractes JSON, persistència a SQLite, paritat del frontend estàtic) sense dependre de la implementació interna del codi font.
3. **Servidor efímer integrat**: Inicialitza automàticament un servidor HTTP en un fil en segon pla (daemon thread) en un port dinàmic assignat pel sistema operatiu (`127.0.0.1:0`). Això garanteix que les proves siguin 100% autònomes, sense conflictes de ports (com el 8080) i sense necessitat d'engegar el servidor prèviament.
4. **Verificació progressiva i mode estricte**:
   - **Mode progressiu (per defecte)**: Permet que la suite s'executi durant el desenvolupament incremental de fites (M1 a M5). Les proves de fites no implementades s'ometen amb claredat (`skipped`) i el runner finalitza amb codi d'èxit `0`.
   - **Mode estricte (`--strict` / `CURIOSTATS_E2E_STRICT=1`)**: Deshabilita totes les omissions condicionals i exigeix el compliment del 100% dels requisits R1 a R5 (utilitzat per a la fita M6 / Victory Audit).

---

## 2. Metodologia de 4 Nivells (4-Tier Architecture)

La suite està dividida en 4 nivells de proves jeràrquics i complementaris:

| Nivell | Fitxer | Descripció i Cobertura |
| :--- | :--- | :--- |
| **Tier 1** | `tests/test_tier1_features.py` | **Cobertura de Funcionalitats**: Verificació de taules SQLite, recompte mínim de 31 registres, neteja de dades (`Ca de Bou`), normalització de `group_type`, endpoints REST (`/api/curiositats`, `/api/random`, `/api/stats`), documentació (README, ARCHITECTURE, SOURCES), AI Skill (`SKILL.md`), OpenAPI/Swagger i apartats de contacte/privadesa. |
| **Tier 2** | `tests/test_tier2_boundaries.py` | **Límits i Casos Extrems**: Cerca amb caràcters diacrítics catalans (`ç`, `l·l`, accents oberts/tancats), cerques buides i d'espais en blanc, resistència a injeccions SQL i càrregues XSS, límits geogràfics de coordenades (Mallorca [39.0, 40.2] / [2.2, 3.6]), ordre cronològic d'esdeveniments i auditoria d'integritat de codificació UTF-8 (zero mojibake / `U+FFFD`). |
| **Tier 3** | `tests/test_tier3_interactions.py` | **Interaccions entre Mòduls**: Concordança exacta entre `/api/stats` i el volum d'elements a `/api/curiositats`, partició disjunta per categories, intersecció de filtres de categoria i cerca, correspondència 1:1 entre `seed_data.json` i `curiositats.db`, paritat entre la base de dades i `FALLBACK_DATA` a `web/app.js`, i validació de contractes OpenAPI 3.x contra el servidor en viu. |
| **Tier 4** | `tests/test_tier4_workflows.py` | **Fluxos d'Usuari Reals**: Flux complet d'arrencada i diagnòstic de dades, navegació simulada pel catàleg amb filtratge i obertura de targetes, exploració aleatòria ("Una a la sort") avaluant entropia i diversitat, simulació de client estàtic offline a Firebase CDN i cicle complet de regeneració de base de dades amb `init_db.py`. |

---

## 3. Estructura de Fitxers de Prova

```text
tests/
├── __init__.py                  # Paquet de proves
├── base.py                      # Utilitats comunes, servidor efímer i gestió de fites
├── test_tier1_features.py       # 20 proves de cobertura de funcionalitats R1-R5
├── test_tier2_boundaries.py     # 16 proves de límits, caràcters catalans i seguretat
├── test_tier3_interactions.py   # 6 proves d'interacció creuada i sincronització
├── test_tier4_workflows.py      # 6 proves de fluxos d'usuari i cicles operatius
└── run_tests.py                 # Runner unificat CLI amb filtratge i informes
```

---

## 4. Instruccions d'Execució

### 4.1 Execució Estàndard de Tota la Suite

Pots executar la suite completa mitjançant el runner unificat o a través del mòdul estàndard `unittest`:

```powershell
# Mitjançant el runner personalitzat (amb informe resum estructurat)
python tests/run_tests.py

# O bé mitjançant descoberta nativa de Python unittest
python -m unittest discover tests
```

### 4.2 Execució per Nivell (Tier)

Per centrar la validació en un nivell concret:

```powershell
python tests/run_tests.py --tier 1    # Només funcionalitats bàsiques R1-R5
python tests/run_tests.py --tier 2    # Només límits i robustesa
python tests/run_tests.py --tier 3    # Només interaccions i sincronització
python tests/run_tests.py --tier 4    # Només fluxos d'aplicació complets
```

### 4.3 Mode Estricte (Final Hardening / Milestone M6)

Per forçar la comprovació estricta del 100% dels requisits (prohibint qualsevol omissió de fita):

```powershell
python tests/run_tests.py --strict
```

O definint la variable d'entorn:
```powershell
$env:CURIOSTATS_E2E_STRICT = "1"
python -m unittest discover tests
```

---

## 5. Matriu de Traçabilitat de Requisits

| Requisit | Nom del Requisit | Proves Associades (Exemples) | Nivell |
| :--- | :--- | :--- | :--- |
| **R1** | Neteja i integritat de dades | `test_r1_database_record_counts`, `test_r1_ca_de_bou_homogenization`, `test_r1_group_type_normalization`, `test_r1_no_null_or_empty_critical_fields` | Tier 1, 2, 3 |
| **R1** | Endpoints de l'API REST | `test_r1_api_curiositats_unfiltered`, `test_r1_api_curiositats_category_filtering`, `test_r1_api_random`, `test_r1_api_stats` | Tier 1, 3, 4 |
| **R2** | Documentació de creació | `test_r2_readme_documentation_exists`, `test_r2_architecture_documentation_accurate`, `test_r2_sources_documentation_exists` | Tier 1 |
| **R3** | Skill per afegir referències | `test_r3_skill_file_structure_and_frontmatter` | Tier 1 |
| **R4** | OpenAPI i Swagger UI | `test_r4_openapi_json_specification`, `test_r4_swagger_ui_html_exists`, `test_r4_server_serves_swagger_ui`, `test_openapi_spec_contracts_match_server_responses` | Tier 1, 3 |
| **R5** | Contacte, Privadesa i Git | `test_r5_web_contact_and_privacy_notice`, `test_r5_git_configuration_files` | Tier 1 |

---
*Fitxer generat pel Test Writer (E2E Testing Track).*

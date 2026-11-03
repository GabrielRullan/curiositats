# Una teringa de curiositats 📜🌿🦎🥖🏛️

> **«Teringa»** (*f.*): Filera, renglera o successió continuada de coses o persones que van l'una darrere l'altra (*Diccionari Català-Valencià-Balear*, Alcover-Moll).  
> **Una teringa de curiositats** és la plataforma digital lliure que enfila, una darrere l'altra com les perles d'un collaret, el patrimoni lingüístic, biològic, comercial i històric de l'illa de Mallorca.

---

## 1. Visió General i Filosofia del Projecte

Mallorca posseeix un patrimoni cultural i etnogràfic d'un valor incalculable que massa sovint roman dispers en arxius especialitzats, monografies erudites, inventaris administratius o diccionaris de referència d'accés complex per a la ciutadania. 

**«Una teringa de curiositats»** neix per reunir i divulgar aquest tresor col·lectiu mitjançant una experiència d'usuari intuïtiva, immersiva i accessible tant des de qualsevol navegador web modern com a través d'una interfície de programació (API) oberta.

El concepte clau del projecte es reflecteix en el seu propi nom: una **filera infinita de descobriments** estructurada en cinc grans pilars temàtics:

* 🗣️ **De la llengua (Paraules & Dites)**: Lèxic genuí, etimologia mossàrab, àrab i llatina, locucions populars, refranys agrícoles i frases fetes de la tradició oral mallorquina.
* 🦎 **De la garriga i la mar (Fauna)**: Espècies salvatges endèmiques (com el ferreret o el virot petit) i les 14 races domèstiques autòctones reconegudes oficialment (ca de bestiar, ca de bou, porc negre, ase balear, etc.).
* 🌿 **De la terra i els penyals (Flora)**: Botànica de la Serra de Tramuntana, garriga i litoral marí, destacant els usos etnobotànics tradicionals (remeiers, culinaris i artesanals).
* 🥖 **De cal menestral (Comerços Emblemàtics)**: Establiments centenaris, forns d'ensaïmades tradicionals, teixits de llengües, cellers, cereries i tallers artesans protegits pel projecte Emblemàtics Balears.
* 📜 **De temps ha (Història & Cronologia)**: Des dels poblaments talaiòtics i la fundació romana de Pol·lèntia fins a la conquesta de 1229, les Germanies de 1521 i les fites de la Mallorca contemporània.

---

## 2. Com es va Crear el Projecte: Metodologia de Dades i Curació

El projecte s'ha construït seguint un rigorós procés d'enginyeria de dades i investigació històrica i lingüística dividit en tres etapes:

### 2.1. Identificació de Fonts Autoritatives Balears
Es va dur a terme una prospecció exhaustiva d'institucions acadèmiques, museístiques i administratives de les Illes Balears. D'aquest treball va sorgir el catàleg mestre de **60 fons de referència** (`docs/SOURCES.md` i `database/reference_sources.json`), destacant:
- **Lexicografia i Oralitat**: El *Diccionari Català-Valencià-Balear* (DCVB d'Antoni M. Alcover i Francesc de B. Moll), el DIEC2 de l'IEC, el *Cançoner Popular de Mallorca* de Rafel Ginard (Mallorca Oral) i el corpus del Viccionari balear.
- **Biodiversitat i Races**: *Biodibal / BioBal* (UIB / Redeia), l'*Herbari Virtual del Mediterrani Occidental* (UIB) i l'*IRFAP* (Institut de Recerca i Formació Agroalimentària i Pesquera).
- **Patrimoni Històric i Comercial**: El *Catàleg d'Emblemàtics Balears* (IDI / ADR Balears), l'*Arxiu del Regne de Mallorca* (ARM) i la *Gran Enciclopèdia de Mallorca* (GEM).

### 2.2. Disseny de l'Esquema Relacional i Normalització
Per garantir la integritat de les dades, es va dissenyar un esquema relacional SQL (`database/schema.sql`) amb taules independents per a cada domini (`words`, `fauna`, `flora`, `emblematic_businesses`, `historical_events`), dotades de restriccions `CHECK` geogràfiques i temporals, claus úniques (`UNIQUE`) i índexs de rendiment per a consultes per municipi, categoria o època històrica.

Totes les entrades van ser sotmeses a un procés d'estandardització:
- Correcció d'inconsistències ortogràfiques i eliminació de caràcters corruptes o errors d'encoding (*mojibake*).
- Eliminació de glosses foranes o no normatives en favor de la denominació popular pròpia de Mallorca.
- Normalització de categories gramaticals i tipologies biològiques en català estàndard.

### 2.3. Pipeline d'Ingesta i Enriquiment Dialectal
El projecte incorpora pipelines dedicats a l'adquisició contínua de dades:
1. **Script mestre d'inicialització (`scripts/importers/init_db.py`)**: Valida prèviament les dades de `database/seed_data.json` abans d'escriure a disc i efectua una post-comprovació automatitzada que certifica que no existeixen registres nuls ni camps buits.
2. **Ingestor DIEC2 (`scripts/importers/import_diec.py`)**: Importa entrades dialectals balears garantint idempotència.
3. **Scraper del Viccionari Balear (`scripts/scrapers/viccionari_balear_scraper.py` i `scripts/importers/import_viccionari.py`)**: Extreu dades semàntiques de l'API de Wikimedia per a les categories «Mallorquí» i «Balear».
4. **Crawler respectuós del DCVB (`scripts/scrapers/dcvb_crawler.py`)**: Consulta l'API XML de `motor-bdlex.iec.cat` amb control de freqüència (*throttling*) per extreure lemes amb marca dialectal insular.

---

## 3. Arquitectura de Runtime Dual (Dual Runtime Mode)

Per assolir la màxima versatilitat i resiliència, «Una teringa de curiositats» està dissenyada per funcionar de manera transparent sota **dues modalitats de runtime**:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                            UNA TERINGA DE CURIOSITATS                       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
┌───────────────────────────────┐             ┌───────────────────────────────┐
│     MODE SERVIDOR DINÀMIC     │             │     MODE CLIENT ESTÀTIC       │
│      (Desenvolupament local)  │             │   (Producció Firebase/CDN)    │
├───────────────────────────────┤             ├───────────────────────────────┤
│ • Python 3 stdlib http.server │             │ • Single-Page Application     │
│ • Zero dependències externes  │             │ • Vanilla HTML5 / CSS3 / ES6  │
│ • Base de dades curiositats.db│             │ • Resiliència FALLBACK_DATA   │
│ • REST API (/api/curiositats) │             │ • Execució sense backend      │
│ • Swagger UI interactiva      │             │ • Hostatjat a Firebase Global │
└───────────────────────────────┘             └───────────────────────────────┘
```

### A. Mode Servidor Dinàmic Local (`python server.py`)
* **Tecnologia**: Desenvolupat exclusivament sobre la biblioteca estàndard de Python 3 (`http.server.HTTPServer` i `sqlite3`). No requereix `pip install` ni cap dependència externa de tercers.
* **Capacitats**:
  - Connecta directament amb la base de dades SQLite relacional `curiositats.db`.
  - Serveix els fitxers estàtics de la interfície web (`web/`).
  - Proporciona una **API REST completa** amb endpoints per llistar curiositats (`GET /api/curiositats`), obtenir elements aleatoris (`GET /api/random`) i consultar mètriques globals (`GET /api/stats`).
  - Serveix l'especificació **OpenAPI 3.x** (`GET /openapi.json`) i la consola interactiva **Swagger UI** (`/swagger/`).

### B. Mode Client Estàtic / Offline SPA (Firebase Hosting & GitHub Pages)
* **Tecnologia**: Single-Page Application (SPA) construïda amb tecnologies web pures (HTML5 semàntic, CSS3 amb variables i components visuals mediterranis, i JavaScript modern ES6).
* **Mecanisme de Fallback Transparent (`FALLBACK_DATA`)**:
  - Quan l'aplicació s'inicia al navegador, la funció `loadData()` intenta sol·licitar el catàleg a l'API dinàmica (`/api/curiositats`).
  - Si l'aplicació està desplegada en un allotjament estàtic (com Firebase Hosting, GitHub Pages o una sessió sense connexió `file://`), la petició fallarà de manera controlada i el client utilitzarà immediatament el conjunt de dades integrat `FALLBACK_DATA`.
  - L'usuari gaudeix d'una experiència fluida, ràpida i sense cap mena d'interrupció ni pantalla d'error.

---

## 4. Guia Ràpida d'Instal·lació i Ús

### 4.1. Requisits Previs
- **Python 3.8 o superior** instal·lat al sistema operatiu.
- No es requereix cap entorn virtual ni comanda `pip`, ja que s'empra exclusivament la llibreria estàndard.

### 4.2. Inicialització i Verificació de la Base de Dades
Per regenerar la base de dades SQLite `curiositats.db` a partir de les dades canòniques validades de `database/seed_data.json`:

```bash
# Validació prèvia en memòria (sense tocar curiositats.db)
python scripts/importers/init_db.py --check

# Inicialització i generació de la base de dades física
python scripts/importers/init_db.py
```

### 4.3. Execució del Servidor Web i API Local
Executeu el servidor HTTP nadiu:

```bash
python server.py
```

El servidor s'iniciarà per defecte al port `8080`:
- 🌐 **Interfície d'usuari**: [http://localhost:8080](http://localhost:8080)
- 📜 **Documentació de l'API (Swagger UI)**: [http://localhost:8080/swagger/](http://localhost:8080/swagger/)
- 📄 **Especificació OpenAPI**: [http://localhost:8080/openapi.json](http://localhost:8080/openapi.json)

### 4.4. Execució de la Suite de Proves
El projecte inclou una suite exhaustiva de proves automatitzades (`tests/`) que verifica la integritat de la base de dades, els contractes de l'API, les condicions de contorn i la sincronització de dades:

```bash
# Execució de totes les proves
python -m unittest discover tests

# Execució específica del Tier 1 (Cobertura de requeriments)
python -m unittest tests/test_tier1_features.py

# Execució específica del Tier 2 (Resiliència i diacrítics catalans)
python -m unittest tests/test_tier2_boundaries.py

# Execució específica del Tier 3 (Interaccions creuades i fallback)
python -m unittest tests/test_tier3_interactions.py
```

### 4.5. Desplegament a Producció (Firebase Hosting)
El projecte està preparat per desplegar-se en qüestió de segons a Firebase Hosting:

```bash
# Desplegament directe utilitzant npx
npx -y firebase-tools@latest deploy --only hosting
```

---

## 5. Adreces Oficials en Producció 🚀

L'aplicació es troba desplegada i accessible públicament a la xarxa CDN d'alt rendiment de Firebase:

* 🌍 **Adreça oficial (Domini personalitzat)**: **[https://teringa.balears.tech](https://teringa.balears.tech)**
* 🌐 **URL de Firebase Hosting**: [https://teringa-curiositats.web.app](https://teringa-curiositats.web.app)
* 🔒 **URL secundària**: [https://teringa-curiositats.firebaseapp.com](https://teringa-curiositats.firebaseapp.com)
* 🎛️ **Consola de control de Firebase**: [https://console.firebase.google.com/project/teringa-curiositats/overview](https://console.firebase.google.com/project/teringa-curiositats/overview)

---

## 6. Experiència Web i Interfície d'Usuari

La interfície d'usuari posa a disposició dues modalitats complementàries d'exploració:

1. **Modalitat «Una a la sort» (Spotlight destacat - per defecte)**:
   - Presenta una gran targeta d'impacte visual amb una curiositat triada a l'atzar cada vegada que s'entra al lloc web.
   - Mitjançant el botó **«🎲 Treu-ne una altra a la sort!»**, l'usuari pot anar passant d'una perla a l'altra amb una transició visual suau.
2. **Modalitat «Tota sa teringa» (Catàleg complet i filtres)**:
   - Permet visualitzar la filera completa d'elements catalogats.
   - **Filtres per pilars**: Píndoles interactives per filtrar instantàniament per Llengua, Fauna, Flora, Comerços o Història.
   - **Cercador en temps real**: Cerca insensible a majúscules i minúscules, perfectament compatible amb caràcters diacrítics i particularitats del català (*ela geminada* `l·l`, ce trencada `ç`, accents greus i aguts).
   - **Finestres de detall**: Implementades mitjançant l'element natiu de la web moderna `<dialog>` per oferir màxima accessibilitat (teclat, lectors de pantalla) sense llibreries pesants.
3. **Privadesa sense cookies i Contacte**:
   - La plataforma respecta escrupolosament la intimitat de qui la visita: **no utilitza cookies pròpies ni de tercers, ni emmagatzema dades personals**.
   - Inclou una secció visible de contacte i col·laboració per rebre noves propostes de la comunitat.

---

## 7. Estructura del Repositori

```text
curiositats/
├── README.md                      # Document mestre del projecte i guia d'inici
├── LICENSE                        # Llicència de codi obert del projecte
├── .gitignore                     # Exclusió d'arxius temporals, caches i metadades
├── firebase.json                  # Configuració de rutes i CDN de Firebase Hosting
├── .firebaserc                    # Projecte actiu a Firebase (teringa-curiositats)
├── server.py                      # Servidor HTTP i API REST nadiu (Python 3 stdlib)
├── curiositats.db                 # Base de dades relacional SQLite 3
├── database/
│   ├── schema.sql                 # Esquema relacional DDL (taules, índexs, checks)
│   ├── seed_data.json             # Dades inicials representatives canòniques (31 items)
│   ├── reference_sources.json     # Catàleg de 60 fons de referència documental
│   └── diec_balear_entries.json   # Corpus de 91 entrades dialectals del DIEC2
├── web/                           # Aplicació web (SPA) servida pel servidor i Firebase
│   ├── index.html                 # Estructura semàntica HTML5 i diàlegs natius
│   ├── style.css                  # Disseny mediterrani, tipografia Cinzel i CSS variables
│   ├── app.js                     # Controlador client, filtres, spotlight i FALLBACK_DATA
│   ├── openapi.json               # Especificació OpenAPI 3.x dels endpoints
│   └── swagger/                   # Consola interactiva Swagger UI
│       └── index.html             # Interfície visual per provar l'API
├── docs/                          # Documentació tècnica i acadèmica
│   ├── ARCHITECTURE.md            # Arquitectura tècnica, esquema i API
│   ├── SOURCES.md                 # Guia exhaustiva dels 60 fons i autoritats balears
│   ├── dcvb_open_datasets_research.md # Investigació sobre datasets del DCVB i propietat
│   └── mass_absorption_strategy.md    # Estratègia d'absorció massiva de fraseologia
├── scripts/
│   ├── importers/                 # Eines d'ingesta i validació
│   │   ├── init_db.py             # Inicialització i verificació automàtica de la BBDD
│   │   └── import_diec.py         # Importador dialectal del DIEC2
│   └── scrapers/                  # Eines d'extracció controlada
│       └── diec_balear_scraper.py # Extracció de dades dialectals
└── tests/                         # Suite de proves unitàries i d'integració (unittest)
    ├── __init__.py
    ├── base.py                    # Servidor de proves, assercions i utilitats comunes
    ├── test_tier1_features.py     # Cobertura funcional (R1 a R5)
    ├── test_tier2_boundaries.py   # Casos de contorn, diacrítics i injeccions
    └── test_tier3_interactions.py # Proves d'interacció, recomptes i sincronia
```

---

## 8. Llicència i Reconeixement

Aquest projecte ha estat creat com a iniciativa oberta per a la difusió i salvaguarda del patrimoni cultural i immaterial de les Illes Balears.  
Les dades lexicogràfiques, botàniques, faunístiques i històriques pertanyen als seus respectius autors i fons institucionals (Institut d'Estudis Catalans, Universitat de les Illes Balears, Govern de les Illes Balears, Consell de Mallorca, IDI i arxius històrics). Cada registre de la plataforma conté la seva referència canònica corresponent.

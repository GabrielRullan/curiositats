---
name: afegir-referencies
description: Procediment estructurat, criteris de qualitat i passos per afegir noves entrades i referències al catàleg de curiositats de les Illes Balears ('Una teringa de curiositats').
---

# Skill: Afegir Noves Referències a «Una teringa de curiositats»

## 1. Objectiu i Context del Projecte

**«Una teringa de curiositats»** és una plataforma digital, catàleg cultural i repositori de dades dedicat a la recopilació, preservació i divulgació de la riquesa dialectal, etnològica, botànica, faunística, patrimonial i històrica de Mallorca i de les Illes Balears.

El projecte manté la informació mitjançant una arquitectura articulada en tres nivells de persistència i distribució:
1. **Base de Dades SQLite (`curiositats.db`)**: Motor relacional transaccional que allotja les taules principals (`words`, `fauna`, `flora`, `emblematic_businesses`, `historical_events`) utilitzades pel servidor API (`http.server` a Python).
2. **Fitxer Mestre de Dades Inicials (`database/seed_data.json`)**: Dipòsit canònic en format JSON que conté el conjunt base de registres validats, garantint la reproduïbilitat, la sincronització i la regeneració de la base de dades mitjançant `scripts/importers/init_db.py`.
3. **Reserva estàtica del client (`web/app.js` - `FALLBACK_DATA`)**: Estructura mínima de dades autònomes integrada en el codi JavaScript del navegador, que assegura que l'aplicació web continuï sent totalment operativa en absència de connectivitat o quan s'obre directament mitjançant el protocol local (`file://`).

L'objectiu d'aquesta skill és establir un **procediment formal** i uns **criteris de qualitat** estrictes per guiar els agents d'intel·ligència artificial i desenvolupadors a l'hora d'incorporar noves entrades, assegurant la màxima versemblança documental, el rigor lingüístic i la coherència relacional.

---

## 2. Tipologies d'Elements Acceptats

El catàleg admet exclusivament informació estructurada dins de les **cinc tipologies** (taules) següents:

1. **`words` (Paraules, Expressions i Dites Balears)**:
   - **Termes dialectals**: Mots genuïns d'ús viu o històric a Mallorca i les Illes Balears (p. ex., *teringa*, *ullprès*, *cap-ficat*, *xerec / xereca*, *burballa*, *cap-romput*).
   - **Locucions i Frases Fetes**: Expressions idiomàtiques pròpies (p. ex., *fer un gafet*, *al bell mig*, *fer es sopes*, *tenir llapissol*).
   - **Refranys i Dites**: Fórmules sapiencials de la tradició oral balear (p. ex., *qui no té feina el moix pentina*).
   - *Exclusions*: No s'admeten barbarismes sense arrelament històric, castellanismes recents ni termes d'ús panromànic que no aportin valor diferencial illenc.

2. **`fauna` (Animals Salvatges i Races Autòctones)**:
   - **Espècies salvatges**: Fauna vertebrada o invertebrada autòctona o migratòria de les Balears (p. ex., *ferreret*, *virot petit*, *voltor negre*, *sargantana balear*).
   - **Endemismes**: Espècies o subespècies evolutivament aïllades a Mallorca o als seus illots costaners (Cabrera, Dragonera, etc.).
   - **Races autòctones domèstiques**: Les 14 races oficialment catalogades i protegides per l'Institut de Recerca i Formació Agroalimentària i Pesquera (IRFAP): *Porc Negre Mallorquí*, *Ca de Bestiar*, *Ca de Bou*, *Ca Mè*, *Ase Balear*, *Cavall Mallorquí*, *Ovella Mallorquina*, etc.

3. **`flora` (Plantes, Arbres i Etnobotànica)**:
   - **Espècies botàniques**: Flora vascular autòctona de les Balears, especialment adaptada als hàbitats illencs (p. ex., *fonoll marí*, *garrofer*, *mata / lentisc*).
   - **Endemismes vegetals**: Espècies que només creixen de forma natural a les Balears (p. ex., *estepa joana / Hypericum balearicum*, *cresta de gall o didalera menor / Digitalis minor*).
   - **Etnobotànica i Usos Tradicionals**: Aplicacions populars medicinals (*oli de cop*), gastronòmiques (*adobar olives i tàperes*, *trempar ensalades*), artesanals (*trenat de garballó per a la llatra*) o agrícoles.

4. **`emblematic_businesses` (Negocis, Comerços i Oficis Tradicionals)**:
   - Establiments amb un arrelament històric certificat (generalment superior a 75 anys d'activitat ininterrompuda) o inscrits al catàleg d'*Emblemàtics Balears* de l'Institut d'Innovació Empresarial (IDI / ADR Balears).
   - Categories oficials: *Comerç arrelat*, *Comerç amb història*, *Comerç amb patrimoni*.
   - Sectors admesos: Forns i pastisseries tradicionals (ensaïmades, panades), tallers d'artesania (vidre bufat, teixits de llengües ikat, sabateria i marroquineria), cellers i restauració històrica, merceries i comerços centenaris.

5. **`historical_events` (Fets Històrics i Fites Cronològiques)**:
   - Fets i processos decisius per a la societat, la cultura o el territori balear des de la Prehistòria fins al segle XX.
   - Períodes històrics reconeguts:
     - *Prehistòria i Talaiòtic* (c. 1000 a. C. - 123 a. C.)
     - *Època Romana* (123 a. C. - 902 d. C.)
     - *Època Islàmica (Mayûrqa)* (902 d. C. - 1229)
     - *Reialme de Mallorca (Edat Mitjana)* (1229 - 1516)
     - *Edat Moderna* (1516 - 1789 / 1808)
     - *Edat Contemporània* (1808 - segle XX)
   - Cal vincular-los a personatges documentats i arxius històrics de primer ordre.

---

## 3. Esquema i Camps Obligatoris (`database/schema.sql`)

Tota dada incorporada ha de respectar escrupolosament l'esquema relacional definit a `database/schema.sql`. A continuació se'n detallen els camps, restriccions i tipus:

### Taula `words`
| Camp | Tipus SQL | Obligatori | Restriccions i Valors per Defecte | Descripció |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `INTEGER` | Sí (PK) | `PRIMARY KEY AUTOINCREMENT` | Clau primària numèrica |
| `term` | `VARCHAR(150)` | **SÍ** | `NOT NULL UNIQUE`, text no buit | Lema, mot o frase feta |
| `ipa_pronunciation` | `VARCHAR(100)` | No | Cadena entre claudàtors `[...]` | Transcripció fonètica AFI dialectal |
| `grammatical_category` | `VARCHAR(50)` | No | Ex: *nom masculí*, *nom femení*, *verb*, *adjectiu*, *frase feta*, *dita / refrany* | Categoria gramatical |
| `definition` | `TEXT` | **SÍ** | `NOT NULL`, text no buit | Definició precisa i exhaustiva |
| `example_sentence` | `TEXT` | No | Text lliure | Exemple d'ús quotidià o cita literària |
| `etymology` | `TEXT` | No | Text lliure | Origen etimològic i lingüístic |
| `dialectal_notes` | `VARCHAR(150)` | No | Ex: *Mallorquí general*, *Pla de Mallorca*, *Sóller*, *Manacor* | Zona d'ús o distribució geolingüística |
| `source_reference` | `VARCHAR(255)` | No | `DEFAULT 'Diccionari Català-Valencià-Balear (Alcover-Moll)'` | Font lexicogràfica autoritzada |
| `created_at` | `TIMESTAMP` | No | `DEFAULT CURRENT_TIMESTAMP` | Marca temporal del sistema |

### Taula `fauna`
| Camp | Tipus SQL | Obligatori | Restriccions i Valors per Defecte | Descripció |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `INTEGER` | Sí (PK) | `PRIMARY KEY AUTOINCREMENT` | Clau primària numèrica |
| `common_name_ca` | `VARCHAR(150)` | **SÍ** | `NOT NULL UNIQUE`, text no buit | Nom vernacle balear |
| `scientific_name` | `VARCHAR(150)` | No | Nomenclatura binomial en llatí | Nom científic zoològic |
| `group_type` | `VARCHAR(50)` | **SÍ** | `NOT NULL` (`amfibi`, `reptil`, `au`, `mamifer`, `invertebrat`, `peix`, `raça autòctona`) | Classificació de grup |
| `is_endemic` | `BOOLEAN` | No | `DEFAULT 0` (enter 0 o 1 a SQLite; `false`/`true` a JSON) | Si és endemisme balear |
| `is_native_breed` | `BOOLEAN` | No | `DEFAULT 0` (enter 0 o 1 a SQLite; `false`/`true` a JSON) | Raça autòctona IRFAP |
| `conservation_status` | `VARCHAR(50)` | No | Ex: *Preocupació Menor (LC)*, *Vulnerable (VU)*, *En perill (EN)*, *En perill crític (CR)*, *Protecció Oficial (IRFAP)* | Estat de conservació |
| `habitat` | `TEXT` | No | Text descriptiu | Hàbitat natural i distribució insular |
| `description` | `TEXT` | **SÍ** | `NOT NULL`, text no buit | Descripció morfològica i etològica |
| `curiosities` | `TEXT` | No | Dades singulars | Particularitats o anècdotes |
| `image_url` | `TEXT` | No | URL vàlida o buida | Enllaç a imatge amb llicència lliure |
| `source_reference` | `VARCHAR(255)` | No | `DEFAULT 'Biodibal (UIB) / IRFAP'` | Font documental o científica |
| `created_at` | `TIMESTAMP` | No | `DEFAULT CURRENT_TIMESTAMP` | Marca temporal del sistema |

### Taula `flora`
| Camp | Tipus SQL | Obligatori | Restriccions i Valors per Defecte | Descripció |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `INTEGER` | Sí (PK) | `PRIMARY KEY AUTOINCREMENT` | Clau primària numèrica |
| `common_name_ca` | `VARCHAR(150)` | **SÍ** | `NOT NULL UNIQUE`, text no buit | Nom popular català / balear |
| `scientific_name` | `VARCHAR(150)` | **SÍ** | `NOT NULL UNIQUE`, text no buit | Nom científic botànic binomial |
| `family` | `VARCHAR(100)` | No | Família taxonòmica botànica | Família vegetal (ex. *Apiaceae*, *Fabaceae*) |
| `is_endemic` | `BOOLEAN` | No | `DEFAULT 0` (enter 0 o 1 a SQLite; `false`/`true` a JSON) | Si és exclusiva de les Balears |
| `flowering_period` | `VARCHAR(100)` | No | Ex: *Abril - Juliol*, *Setembre - Novembre* | Mesos o època de floració |
| `habitat` | `TEXT` | No | Text descriptiu | Penya-segats, garriga, marjades, etc. |
| `traditional_uses` | `TEXT` | No | Text etnobotànic | Usos medicinals, culinaris, ramaders o artesanals |
| `description` | `TEXT` | **SÍ** | `NOT NULL`, text no buit | Descripció botànica |
| `curiosities` | `TEXT` | No | Dades botàniques insòlites | Trets d'adaptació al medi illenc |
| `image_url` | `TEXT` | No | URL vàlida o buida | Imatge d'Herbari Virtual o repositori obert |
| `source_reference` | `VARCHAR(255)` | No | `DEFAULT 'Herbari Virtual del Mediterrani Occidental (UIB)'` | Font botànica oficial |
| `created_at` | `TIMESTAMP` | No | `DEFAULT CURRENT_TIMESTAMP` | Marca temporal del sistema |

### Taula `emblematic_businesses`
| Camp | Tipus SQL | Obligatori | Restriccions i Valors per Defecte | Descripció |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `INTEGER` | Sí (PK) | `PRIMARY KEY AUTOINCREMENT` | Clau primària numèrica |
| `name` | `VARCHAR(200)` | **SÍ** | `NOT NULL UNIQUE`, text no buit | Nom comercial registrat |
| `category_type` | `VARCHAR(100)` | **SÍ** | `NOT NULL` (*Comerç arrelat*, *Comerç amb història*, *Comerç amb patrimoni*) | Categoria oficial IDI |
| `sector` | `VARCHAR(100)` | **SÍ** | `NOT NULL` (ex. *Forn i Pastisseria*, *Artesania / Teixits*, *Restauració / Celler*) | Sector econòmic |
| `foundation_year` | `INTEGER` | No | `CHECK (foundation_year IS NULL OR foundation_year > 1200)` | Any de fundació històric (> 1200) |
| `municipality` | `VARCHAR(100)` | **SÍ** | `NOT NULL` (p. ex. *Palma*, *Inca*, *Sóller*, *Manacor*) | Municipi de les Illes Balears |
| `address` | `TEXT` | No | Adreça postal física | Carrer, número i codi postal |
| `latitude` | `REAL` | No | `CHECK (latitude BETWEEN 39.0 AND 40.2)` | Latitud geogràfica a l'arxipèlag |
| `longitude` | `REAL` | No | `CHECK (longitude BETWEEN 2.2 AND 3.6)` | Longitud geogràfica a l'arxipèlag |
| `history_summary` | `TEXT` | **SÍ** | `NOT NULL`, text no buit | Resum de la trajectòria històrica |
| `heritage_elements` | `TEXT` | No | Detalls patrimonials | Elements protegits (rètols modernistes, forns de solera) |
| `is_active` | `BOOLEAN` | No | `DEFAULT 1` (enter 0 o 1 a SQLite; `true`/`false` a JSON) | Comerç en funcionament actiu |
| `source_reference` | `VARCHAR(255)` | No | `DEFAULT 'Catàleg Emblemàtics Balears (IDI)'` | Font oficial d'atribució |
| `created_at` | `TIMESTAMP` | No | `DEFAULT CURRENT_TIMESTAMP` | Marca temporal del sistema |

### Taula `historical_events`
| Camp | Tipus SQL | Obligatori | Restriccions i Valors per Defecte | Descripció |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `INTEGER` | Sí (PK) | `PRIMARY KEY AUTOINCREMENT` | Clau primària numèrica |
| `title` | `VARCHAR(200)` | **SÍ** | `NOT NULL UNIQUE`, text no buit | Títol descriptiu del fet |
| `historical_period` | `VARCHAR(100)` | **SÍ** | `NOT NULL` (*Prehistòria i Talaiòtic*, *Època Romana*, *Època Islàmica (Mayûrqa)*, *Reialme de Mallorca (Edat Mitjana)*, *Edat Moderna*, *Edat Contemporània*) | Període històric normatiu |
| `year_start` | `INTEGER` | **SÍ** | `NOT NULL` (pot ser negatiu: ex. `-1000`, `-123`) | Any d'inici de l'esdeveniment |
| `year_end` | `INTEGER` | No | `CHECK (year_end IS NULL OR year_start <= year_end)` | Any de finalització |
| `date_display` | `VARCHAR(100)` | **SÍ** | `NOT NULL` (ex. *31 de desembre de 1229*, *1521 - 1523*, *c. 1000 a. C.*) | Text amigable de la data per a la UI |
| `location_scope` | `VARCHAR(150)` | No | Ex. *Palma i Pol·lèntia*, *Artà*, *Castell de Bellver* | Ubicació geogràfica o àmbit |
| `summary` | `TEXT` | **SÍ** | `NOT NULL`, text no buit | Resum clar del fet històric |
| `detailed_description` | `TEXT` | No | Explicació aprofundida | Causes, desenvolupament i transcendència |
| `key_figures` | `TEXT` | No | Personatges clau separats per comes | Protagonistes històrics |
| `source_reference` | `VARCHAR(255)` | No | `DEFAULT 'Arxiu del Regne de Mallorca (ARM) / GEM'` | Font documental d'arxiu |
| `created_at` | `TIMESTAMP` | No | `DEFAULT CURRENT_TIMESTAMP` | Marca temporal del sistema |

---

## 4. Fonts d'Informació Autoritzades

D'acord amb el document de referència `docs/SOURCES.md` i el catàleg canònic `database/reference_sources.json`, l'agent només ha d'extreure o validar dades provinents de **fonts d'informació autoritzades**:

1. **Llengua i Dialectologia**:
   - **DCVB (Alcover-Moll)** (`dcvb.iec.cat` / `motor-bdlex.iec.cat`): Diccionari Català-Valencià-Balear de mossèn Antoni M. Alcover i Francesc de B. Moll. Font d'autoritat suprema per a pronúncies dialectals per municipi, accepcions mallorquines, etimologia i cites de rondalles.
   - **DIEC2 / BDLex** (`dlc.iec.cat` / `bdlex.iec.cat`): Diccionari de la Llengua Catalana de l'Institut d'Estudis Catalans. Font normativa per a definicions generals i categories gramaticals.
   - **Mallorca Oral / Cançoner Popular** (`mallorcaoral.cat`): Fons de la Fundació Mallorca Literària que recull el Cançoner Popular de Rafel Ginard, milers d'enregistraments orals, cobles, refranys i dites de feina.
   - **ALDC (Atles Lingüístic del Domini Català)** (`aldc.espais.iec.cat`): Cartografia lingüística amb mostres fonètiques reals dels parlars mallorquins.
   - **TERMCAT** (`termcat.cat`): Terminologia d'oficis tradicionals, estris de pedra en sec i ornitologia balear.
   - **Viccionari**: Categoria específica *Mallorquí* i *Balear* contrastada.

2. **Fauna i Conservació**:
   - **Biodibal (BioBal - UIB / Redeia)** (`biodibal.cat`): El repositori més complet de dades obertes sobre biodiversitat de les Balears (+1,5 milions de registres). Font per confirmar endemismes i quadrícules UTM de presència.
   - **IRFAP (Govern de les Illes Balears)** (`irfap.org`): Catàleg oficial de les races autòctones balears. Proporciona estàndards racials, patrons morfològics i història de la domesticació insular.
   - **COFIB (Consorci per a la Recuperació de la Fauna de les Illes Balears)** (`recuperacionfaunabaleares.es`): Informes sanitaris, rescat d'aus marines i control de fauna exòtica.
   - **GOB Mallorca** (`gobmallorca.com`): *Anuari Ornitològic de les Illes Balears* per a dades d'ocells marins i rapinyaires.
   - **SHNB (Societat d'Història Natural de les Balears)** (`shnb.org`): *Bolletí de la SHNB* per a fauna fòssil (*Myotragus balearicus*) i artròpodes endèmics.

3. **Flora i Etnobotànica**:
   - **Herbari Virtual del Mediterrani Occidental (UIB)** (`herbarivirtual.uib.es`): Font botànica oficial que detalla la taxonomia, família, època de floració, noms comuns mallorquins i remeis populars.
   - **MUCBO (Museu Balear de Ciències Naturals i Jardí Botànic de Sóller)** (`mucbo.org`): Conservació d'espècies amenaçades dels penyals de Tramuntana i banc de llavors.
   - **Xarxa Forestal de les Illes Balears** (`xarxaforestal.info`): Catàleg d'arbres monumentals i singulars de Mallorca.

4. **Comerç i Negocis Emblemàtics**:
   - **Emblemàtics Balears (IDI / ADR Balears)** (`emblematicsbalears.es`): Catàleg oficial del Govern de les Illes Balears amb fitxes geolocalitzades d'establiments amb història, tradició i ofici arrelat.
   - **Arxiu Municipal de Palma (Can Balaguer)** (`palma.cat`): Història comercial urbana i documentació gremial.
   - **Museu del Calçat i de la Indústria d'Inca** (`museudelcalcat.inca.es`): Història de la sabateria i la pell a Mallorca.

5. **Història i Patrimoni**:
   - **Arxiu del Regne de Mallorca (ARM)** (`arxiuregnemallorca.com`): Arxiu històric canònic de les Illes Balears des de 1229 (*Llibre del Repartiment*, documentació de la Corona d'Aragó, processos judicials de les Germanies).
   - **Gran Enciclopèdia de Mallorca (GEM)**: Obra enciclopèdica fonamental per a la història, personatges, possessions i esdeveniments locals.
   - **Arxiu Capitular de Mallorca (ACM) i Arxiu Diocesà (Maiorica Sacra)**: Registres des del segle XIII, fàbrica de la Catedral de Palma i demografia històrica.
   - **Portal de Patrimoni Cultural del Consell de Mallorca** (`patrimoni.conselldemallorca.cat`): Registre oficial de Béns d'Interès Cultural (BIC).
   - **Jaciments i Museus de Referència**: Ciutat Romana de Pol·lèntia (`alcudia.net/Pollentia`), Poblat de ses Païsses d'Artà (`artaturisme.com`), Museu de Son Fornés (`sonfornes.mallorca.museum`), Castell de Bellver (`castelldebellver.palma.cat`).

---

## 5. Criteris Lingüístics i de Qualitat

Tota incorporació de dades ha de satisfer els següents **criteris** de qualitat lingüística i formal:

### 1. Varietat Balear del Català
- S'ha de respectar i prioritzar el lèxic autòcton balear (*moix* per a gat, *al·lot* per a noi, *berenar* o *erenar* per a esmorzar o menjar lleuger, *xerec* per a dolent o espatllat, *trempar* per a amanir, *cap-ficat*, *ullprès*).
- En els exemples d'ús oral, refranys, cobles populars i fragments de rondalles s'utilitzarà l'article salat (*es*, *sa*, *ses*, *es / s'*), fidel a la parla viva. En les definicions acadèmiques i resums enciclopèdics s'emprarà el català estàndard normatiu d'àmbit balear (amb article literari *el*, *la*, *els*, *les*).

### 2. Ortografia Normativa Estricta (IEC)
- S'ha d'aplicar amb rigor la normativa de l'Institut d'Estudis Catalans:
  - **Accentuació diacrítica**: Només s'accentuen els mots monosíl·labs establerts a la reforma de 2016 (*bé*, *déu*, *és*, *mà*, *més*, *món*, *pèl*, *què*, *sé*, *sí*, *sòl*, *son*, *te*, *ús*, *vós*).
  - **Ela geminada**: Ús correcte de `l·l` (no guió, ni punt baix, ni punt volat aïllat).
  - **Ce trencada**: Grafia `ç` correcta en tots els contextos necessaris (*plaça*, *dolç*, *caçador*).
  - **Apòstrofs i contraccions**: Aplicació correcta de les regles d'apostrofació de l'article (*l'home*, *l'art*, *la universitat*, *s'home*, *s'aigua*) i de les preposicions (*d'Inca*, *per l'esquerra*).

### 3. Transcripció Fonètica AFI (Alfabet Fonètic Internacional)
- Per als registres de la taula `words`, la pronúncia s'ha de transcriure en format AFI envoltat per claudàtors `[...]`:
  - Representació de la vocal neutra (àtona o tònica mallorquina): `[ə]` (p. ex., *teringa* `[təˈɾiŋ.ɡə]`).
  - Distinció de les consonants palatals: lateral `[ʎ]` (*ull* `[uʎ]`), nasal `[ɲ]` (*senalla* `[səˈna.ʎə]`).
  - Africades i fricatives pròpies: `[ʃ]` (*moix* `[moʃ]`), `[ʒ]` / `[dʒ]`.
  - Signe d'accent prosòdic `ˈ` immediatament davant de la síl·laba tònica (p. ex., *cap-ficat* `[kap.fiˈkat]`).

### 4. Absència d'Anglicismes o Traduccions Inapropiades
- Queda prohibit incorporar termes o traduccions en anglès en títols (`title`), noms comuns (`common_name_ca`), lemes (`term`) o definicions. Tot el corpus ha d'expressar-se en català normatiu i natural.

### 5. Convencions de Majúscules i Tipografia
- **Termes lingüístics**: Primera lletra en majúscula (p. ex., *Teringa*, *Fer un gafet*).
- **Noms comuns de fauna i flora**: Primera lletra en majúscula al llistat mestre (p. ex., *Ferreret*, *Estepa joana*).
- **Noms científics**: Sempre en nomenclatura binomial en llatí, amb la inicial del gènere en majúscula i la de l'espècie en minúscula (p. ex., *Alytes muletensis*, *Hypericum balearicum*).
- **Negocis emblemàtics**: Majúscules segons el nom comercial registrat (p. ex., *Forn del Santo Cristo*, *Teixits Riera*).
- **Fets històrics**: Majúscules als noms propis, segles i títols representatius (p. ex., *La Revolta de les Germanies a Mallorca*).

---

## 6. Procediment Pas a Pas per a l'Agent

Per incorporar amb èxit una nova referència, l'agent ha d'executar aquest **procediment** de sis passos:

### Pas 1: Verificació de la Font i Absència de Duplicats
1. Contrastar les dades amb les fonts autoritzades especificades a la Secció 4.
2. Executar una consulta de comprovació a `curiositats.db` i una cerca a `database/seed_data.json` per assegurar que el registre no existeixi ja:
   ```sql
   -- Taula words
   SELECT id, term FROM words WHERE LOWER(TRIM(term)) = LOWER(TRIM(?));
   -- Taula fauna
   SELECT id, common_name_ca FROM fauna WHERE LOWER(TRIM(common_name_ca)) = LOWER(TRIM(?));
   -- Taula flora
   SELECT id, common_name_ca, scientific_name FROM flora WHERE LOWER(TRIM(common_name_ca)) = LOWER(TRIM(?)) OR LOWER(TRIM(scientific_name)) = LOWER(TRIM(?));
   -- Taula emblematic_businesses
   SELECT id, name FROM emblematic_businesses WHERE LOWER(TRIM(name)) = LOWER(TRIM(?));
   -- Taula historical_events
   SELECT id, title FROM historical_events WHERE LOWER(TRIM(title)) = LOWER(TRIM(?));
   ```
3. Si el terme o títol ja existeix, no s'ha d'afegir com a duplicat. Es valorarà si es requereix una actualització (`UPDATE`) per completar camps pendents (com la pronúncia AFI, usos tradicionals o etimologia).

### Pas 2: Mapeig de Dades segons l'Esquema Relacional
1. Modelar les dades recopilades segons l'esquema relacional de la Secció 3.
2. Assignar a cada camp el seu tipus corresponent (`INTEGER`, `REAL`, `BOOLEAN`, `TEXT`).
3. Especificar de manera explícita la font autoritzada al camp `source_reference`.

### Pas 3: Validació Estricta de Restriccions i Rangs
1. Comprovar que cap camp obligatori (`NOT NULL`) estigui buit ni contingui únicament espais en blanc.
2. **Coordenades geogràfiques** per a `emblematic_businesses`:
   - `latitude` ha d'estar compresa obligatòriament entre `39.0` i `40.2`.
   - `longitude` ha d'estar compresa obligatòriament entre `2.2` i `3.6`.
3. **Anys i Rangs temporals**:
   - `foundation_year` a `emblematic_businesses`: si està present, ha de ser strictly superior a `1200` (`foundation_year > 1200`).
   - `year_start` a `historical_events`: camp enter obligatori (admet nombres negatius com `-123`).
   - `year_end`: si és present, ha de complir que `year_start <= year_end`.

### Pas 4: Inserció o Actualització a `database/seed_data.json` i `curiositats.db`
1. **Actualitzar `database/seed_data.json`**:
   - Obrir el fitxer amb codificació UTF-8.
   - Afegir el nou registre al final de l'array de la taula corresponent (`words`, `fauna`, `flora`, `emblematic_businesses` o `historical_events`).
   - Guardar el fitxer garantint una indentació neta de 2 espais (`indent=2`) i assegurant que `ensure_ascii=False`.
2. **Inserir a la base de dades SQLite `curiositats.db`**:
   - Executar la sentència `INSERT` parametritzada amb un cursor SQLite per evitar injeccions.
   - O bé, executar el sincronitzador mestre del projecte:
     ```bash
     python scripts/importers/init_db.py
     ```

### Pas 5: Sincronització de `web/app.js` (`FALLBACK_DATA`)
Si el nou registre té caràcter representatiu i s'ha d'incorporar a les dades estàtiques de contingència del client web, cal afegir-lo al vector `FALLBACK_DATA` a `web/app.js` utilitzant l'esquema unificat:
```javascript
{
  type: "words", // 'words' | 'fauna' | 'flora' | 'businesses' | 'history'
  title: "Títol o Nom de l'element",
  subtitle: "Subtítol descriptiu (p. ex. pronúncia AFI i categoria)",
  tag: "Etiqueta identificativa",
  definition: "Definició breu o resum principal",
  curiosities: "Detalls curiosos, etimologia o trets rellevants",
  source_reference: "Font autoritzada d'atribució"
}
```

### Pas 6: Execució de Scripts de Verificació d'Integritat
1. Executar la comprovació pre-inserció en mode dry-run per assegurar que totes les dades compleixen les restriccions d'esquema:
   ```bash
   python scripts/importers/init_db.py --check
   ```
2. Executar la suite de tests automatitzats per verificar que no hi ha regressió:
   ```bash
   python -m unittest discover tests/
   ```

---

## 7. Scripts i Ordres CLI d'Exemple

A continuació s'ofereixen les eines i comandaments recomanats per a la gestió i verificació de noves dades:

### 1. Comprovació d'Integritat en Sec (`--check`)
Aquesta comanda comprova totes les regles d'esquema i restriccions a la memòria RAM sense modificar el fitxer `curiositats.db`:
```bash
python scripts/importers/init_db.py --check
```

### 2. Consultes de Control Directe via CLI de SQLite
Verificar el recompte total d'entrades per taula:
```bash
sqlite3 curiositats.db "SELECT 'words', COUNT(*) FROM words UNION ALL SELECT 'fauna', COUNT(*) FROM fauna UNION ALL SELECT 'flora', COUNT(*) FROM flora UNION ALL SELECT 'emblematic_businesses', COUNT(*) FROM emblematic_businesses UNION ALL SELECT 'historical_events', COUNT(*) FROM historical_events;"
```

Comprovar que no hi hagi camps obligatoris buits o corruptes:
```bash
sqlite3 curiositats.db "SELECT id, term FROM words WHERE term IS NULL OR TRIM(term) = '' OR definition IS NULL OR TRIM(definition) = '';"
sqlite3 curiositats.db "SELECT id, name FROM emblematic_businesses WHERE latitude IS NOT NULL AND (latitude < 39.0 OR latitude > 40.2);"
sqlite3 curiositats.db "SELECT id, title FROM historical_events WHERE year_end IS NOT NULL AND year_start > year_end;"
sqlite3 curiositats.db "PRAGMA integrity_check;"
```

### 3. Script Python Reutilitzable per Inserir una Referència
```python
"""Script d'exemple per afegir una nova entrada a 'Una teringa de curiositats'."""

import json
from pathlib import Path
import sqlite3
import sys

BASE_DIR = Path(__file__).resolve().parent.parent if "__file__" in locals() else Path(".")
DB_PATH = BASE_DIR / "curiositats.db"
SEED_PATH = BASE_DIR / "database" / "seed_data.json"

nou_registre = {
    "term": "Burballa",
    "ipa_pronunciation": "[buɾˈba.ʎə]",
    "grammatical_category": "nom femení",
    "definition": "Trosset o borralló petit d'alguna cosa; especialment encenall de fusta que surt en ribotar o floquet de neu fina.",
    "example_sentence": "El fuster va deixar el terra del taller ple de burballes de fusta de pi.",
    "etymology": "D'origen expressiu o relacionat amb borboll / bombolla.",
    "dialectal_notes": "Molt viva a Mallorca i Menorca.",
    "source_reference": "Diccionari Català-Valencià-Balear (Alcover-Moll)"
}

def afegir_terme(w: dict):
    # 1. Comprovació de duplicats
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, term FROM words WHERE LOWER(TRIM(term)) = LOWER(TRIM(?))", (w["term"],))
    row = cur.fetchone()
    if row:
        print(f"⚠️ El terme '{w['term']}' ja existeix a la base de dades (ID {row[0]}).")
        conn.close()
        return

    # 2. Inserció a curiositats.db
    cur.execute("""
        INSERT INTO words (term, ipa_pronunciation, grammatical_category, definition, example_sentence, etymology, dialectal_notes, source_reference)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        w.get("term"),
        w.get("ipa_pronunciation"),
        w.get("grammatical_category"),
        w.get("definition"),
        w.get("example_sentence"),
        w.get("etymology"),
        w.get("dialectal_notes"),
        w.get("source_reference")
    ))
    conn.commit()
    conn.close()
    print(f"✅ Inserit a curiositats.db: {w['term']}")

    # 3. Actualització a database/seed_data.json
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["words"].append(w)

    with open(SEED_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Afegit al catàleg mestre seed_data.json.")

if __name__ == "__main__":
    afegir_terme(nou_registre)
```

### 4. Execució de la Suite de Proves
```bash
python -m unittest tests/test_tier1_features.py
```

# Estratègia d'Absorció Massiva de Lèxic, Frases Fetes i Dites Mallorquines
## Full de Ruta Operatiu, Fonts Documentals, Alineació d'Esquema i Validació Comunitària

**Projecte**: «Una teringa de curiositats»  
**Document**: `docs/mass_absorption_strategy.md`  
**Data**: Novembre de 2026  
**Estat**: Estratègia Aprovada per a Implementació  
**Requisit associat**: R5 (Estratègia d'absorció massiva de lèxic i dites)  

---

## 1. Visió i Objectiu Estratègic

L'illa de Mallorca posseeix un tresor lingüístic, fraseològic i paremiològic d'una riquesa excepcional, forjat a través de segles d'aïllament insular, contacte mariner i una tradició agrícola arrelada a la terra. Moltes d'aquestes paraules genuïnes, dites de calendari, renecs tradicionals i girs expressius corren el risc de caure en desús o romandre reclosos en monografies acadèmiques de difícil accés per a la ciutadania.

La missió del projecte **«Una teringa de curiositats»** és convertir la base de dades `curiositats.db` en el repositori digital viu de referència per a la divulgació del català de Mallorca. L'estratègia d'absorció massiva defineix la metodologia tècnica i editorial per ingerir, normalitzar, classificar i difondre milers de termes i locucions populars, garantint tant la seva autenticitat filològica com la seva traçabilitat històrica.

```
+----------------------------------------------------------------------------------------------------+
|                             EMBUT D'ABSORCIÓ MASSIVA DE LÈXIC I DITES                              |
|                                                                                                    |
|  [P1. Rondaies]   [P2. Cançoner]   [P3. Toponímia]   [P4. Folklore]   [P5. AINA]   [P6. Ciutadania]|
|        \                 \                |                /                /             /        |
|         \                 \               |               /                /             /         |
|   +--------------------------------------------------------------------------------------------+   |
|   |                 PIPELINE D'EXTRACCIÓ, NORMALITZACIÓ I DESDUPLICACIÓ                        |   |
|   |         (Puntuació, ela geminada, articles salats, etiquetatge morfosintàctic)             |   |
|   +--------------------------------------------------------------------------------------------+   |
|                                                |                                                   |
|   +--------------------------------------------------------------------------------------------+   |
|   |                         QUALITY GATES (PORTES DE QUALITAT I REVISIÓ)                       |   |
|   |             [Raw / Ingestat] ---> [Validat Algorisme] ---> [Revisat Expert]                |   |
|   +--------------------------------------------------------------------------------------------+   |
|                                                |                                                   |
|                                                v                                                   |
|                          BASE DE DADES `curiositats.db` (Taula `words`)                            |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Els 6 Pilars Fonamentals de Contingut i Fonts

Per aconseguir un corpus viu, equilibrat i ric, la recollida s'estructura al voltant de 6 pilars documentals i socials complementaris:

### Pilar 1: *Aplec de Rondaies Mallorquines d'en Jordi des Racó* (Antoni M. Alcover)
* **Descripció i Abast**: Recopilació de 24 toms que aplega més de 400 rondalles populars transcrites directament de la viva veu de contadors d'arreu de Mallorca entre 1896 i 1930 per mossèn Antoni M. Alcover sota el pseudònim d'*en Jordi des Racó*.
* **Estat Jurídic**: **Domini Públic complet des de l'1 de gener de 2013** (en aplicació de la regla dels 80 anys *post mortem auctoris* per a autors morts el 1932).
* **Dipòsits Digitals Disponibles**:
  * Transcripcions obertes a Wikisource en català (`ca.wikisource.org/wiki/Aplec_de_Rondalles_Mallorquines_d'en_Jordi_des_Racó`).
  * Exemplars digitalitzats a la Biblioteca Digital de les Illes Balears (IBDigital - UIB).
* **Tipologia Lèxica a Extreure**:
  * Fórmules tradicionals d'obertura i tancament: *"Això era i no era..."*, *"I varen ser feliços i rosegaren un os, i a mi me'n donaren un tros que encara era més gros"*.
  * Lèxic d'oficis extingits i estris rurals (burballa, ribot, arada, tafona).
  * Exclamacions, renoms, comparacions humorístiques i renecs atenuats (*"Vaja per un Déu!"*, *"Cap de fava!"*, *"Pardalot!"*).

### Pilar 2: *Cançoner Popular de Mallorca* (Rafel Ginard) i Portal *Mallorca Oral*
* **Descripció i Abast**: El pare Rafel Ginard i Bauçà (1899–1976) va reunir el recull més extens de poesia popular de tot el domini lingüístic, integrat per 4 volums publicats per Editorial Moll (1966–1975) amb més de 15.000 cobles, quartetes i gloses.
* **Plataforma Digital**: El portal **`mallorcaoral.cat`**, impulsat per la Fundació Mallorca Literària (Consell de Mallorca) des de la Casa Museu Pare Ginard a Sant Joan.
* **Tipologia Lèxica a Extreure**:
  * Glosat d'improvisació i cançons de picat.
  * Cançons de treball i cicles agrícoles (batre, collir olives, segar, fer esment).
  * Paremiologia rimada, dites de sàtira veïnal i metàfores relacionades amb la meteorologia i la mar.

### Pilar 3: Toponímia i Microtoponímia Insular
* **Descripció i Abast**: El territori mallorquí conté desenes de milers de noms de lloc menors que descriuen de manera insubstituïble accidents del terreny, coves, avencs, passos, fonts i alqueries antigues.
* **Fonts Canòniques**:
  * *Nomenclàtor toponímic de les Illes Balears* (Comissió de Toponímia / UIB).
  * *Corpus Toponímic de Mallorca* de Josep Mascaró Pasarius (aprox. 50.000 entrades toponímiques).
  * Repositori geogràfic obert de SITIBSA i l'IDEIB (Infraestructura de Dades Espacials de les Illes Balears, `ideib.caib.es`), amb més de 80.000 topònims cartografiats en serveis WFS i capes vectorials GeoJSON.
* **Tipologia Lèxica a Extreure**:
  * Substantius geogràfics autòctons: *caló, cingle, avenc, coma, clapissa, morro, passet, tossal, ses sitges*.
  * Noms de possessió i termes agraris que conserven l'article salat i l'herència toponímica àrab (*Rafal*, *Alqueria*, *Bini-*).

### Pilar 4: Folklore i Etnografia Insular
* **Descripció i Abast**: Obres monumentals que descriuen la vida material, espiritual i festiva de l'illa abans de la transformació turística.
* **Obres Clau**:
  * *Die Balearen in Wort und Bild geschildert* (*Les Balears descrites per la paraula i la imatge*, 1869–1891) de l'Arxiduc Lluís Salvador d'Àustria.
  * *Costumari català* de Joan Amades (volums dedicats a les Balears: tradicions, balls populars, instruments de música com xeremies i flabiols, calendaris festius i de sants).
* **Tipologia Lèxica a Extreure**:
  * Vocabulari de les festes tradicionals: *dimonis, enceses, colles, cossiers, moretons, correfocs*.
  * Refranyer meteorològic i agrari: *"Pel gener, un pas de conill beu bé"*, *"Si plou per Sant Medir, plou per tot el terme"*, *"Aigua de juliol, cap de fava no la vol"*.

### Pilar 5: Corpora Digitals Lingüístics i Acadèmics
* **Descripció i Abast**: Conjunts de dades lingüístiques informatitzades per a l'anàlisi de freqüència i la verificació de concordances.
* **Fonts Disponibles**:
  * **CTILC** (Corpus Textual Informatitzat de la Llengua Catalana - IEC): més de 52 milions de paraules de literatura catalana des de 1833, amb abundant representació d'autors balears (Costa i Llobera, Joan Alcover, Llorenç Villalonga, Maria Antònia Salvà).
  * **Projecte AINA** (Barcelona Supercomputing Center - BSC): recursos computacionals oberts (`softcatala/catalan-dictionary`), models de detecció d'entitats (NER) i corpus de veu.
  * **Corpus Oral Dialectal (COD)** de la Universitat de Barcelona: enregistraments de parla espontània transcrita a Mallorca (Palma, Sóller, Felanitx, Pollença).
* **Funció**: Validar que els lemes extrets tenen atestació real, discernir arcaismes d'errors tipogràfics i extreure exemples d'ús en frases completes.

### Pilar 6: Participació Ciutadana i Recollida Col·laborativa (*Crowdsourcing*)
* **Descripció i Abast**: Canalització de la llengua viva que encara no ha estat recollida als diccionaris acadèmics o que perviu en la memòria de les generacions més grans de Mallorca.
* **Canals Operatius**:
  * Mòdul web *"Apadrina una dita / Envia una paraula viva"*: formulari senzill integrat a la interfície d'«Una teringa de curiositats».
  * Col·laboració amb l'**Obra Cultural Balear (OCB)** i les seves delegacions locals de poble.
  * Aliança amb les **Associacions de Glosadors de Mallorca** per al buidatge de glosades contemporànies.
  * Tallers escolars intergeneracionals als Instituts d'Educació Secundària (IES) de les comarques del Pla, Raiguer, Tramuntana, Migjorn i Llevant.

---

## 3. Full de Ruta Operatiu en 5 Fases

La ingesta massiva es planifica de manera incremental per assegurar la qualitat de les dades i no desbordar la capacitat de revisió editorial:

```
+-------------------------------------------------------------------------------------------------------+
|                                    CRONOGRAMA DE LES 5 FASES D'INGESTA                                |
|                                                                                                       |
| Fase 1: Ingesta Acadèmica Base (DCVB + Viccionari + DIEC2)          [2.000 - 5.000 lemes]  ==> Mes 1  |
| Fase 2: Mineria de Narrativa Oral (Rondaies Mallorquines)           [1.500 expressions]    ==> Mes 2  |
| Fase 3: Extracció de Poesia Oral i Cançó (Cançoner de Ginard)       [2.000 gloses i dites] ==> Mes 3  |
| Fase 4: Integració de Microtoponímia Insular (SITIBSA / UIB)        [1.000 microtopònims]  ==> Mes 4  |
| Fase 5: Canal de Recollida Viva i Ciència Ciutadana                 [Flux continu de dades]==> Mes 5+ |
+-------------------------------------------------------------------------------------------------------+
```

### Fase 1: Ingesta Acadèmica Base (Mes 1)
* **Objectiu**: Dotar `curiositats.db` d'un nucli filològic sòlid, precís i normativament contrastat.
* **Accions**:
  1. Extracció de les **91 entrades balears del DIEC2** (ja preparades a `database/diec_balear_entries.json`).
  2. Buidatge via MediaWiki API dels **952 articles del Viccionari** pertanyents a les categories `Mallorquí` i `Balear`.
  3. Execució del crawler controlat del DCVB mitjançant el motor XML `motor-bdlex.iec.cat` per incorporar un primer paquet representatiu d'entrades genuïnes amb marca `Mall.` o `Bal.`.
* **Volum objectiu**: 2.000 – 5.000 lemes i dites fundacionals.

### Fase 2: Mineria de la Narrativa Oral de les Rondaies Mallorquines (Mes 2)
* **Objectiu**: Extreure el vocabulari expressiu, frases fetes narratives i arcaismes dels 24 volums de l'Aplec d'en Jordi des Racó.
* **Mètode Tècnic**:
  1. Descàrrega automatitzada dels textos complets en domini públic des de l'API de Wikisource (`action=parse`).
  2. Desenvolupament d'un script en Python (`scripts/scrapers/wikisource_rondaies_parser.py`) basat en expressions regulars i processament del llenguatge:
     * Detecció de fragments entre cometes o guions llargs (estil directe i diàleg popular).
     * Detecció de patrons de comparació popular (*"Més vell que l'arada"*, *"Més trist que un dijous sant"*).
     * Buidatge de fórmules d'encapçalament i de cloenda de contalles.
  3. Filtratge de termes que ja figurin al DCVB per afegir-hi la citació exacta del tom de la rondalla com a `example_sentence`.
* **Volum objectiu**: ~1.500 expressions, refranys i girs narratius.

### Fase 3: Extracció de Poesia Oral i Cançó (Cançoner de Ginard) (Mes 3)
* **Objectiu**: Buidar la saviesa paremiològica i la riquesa mètrica del cançoner tradicional de Mallorca.
* **Mètode Tècnic**:
  1. Processament de les cobles populars publicades al portal *Mallorca Oral* i col·leccions digitalitzades del Pare Ginard.
  2. Normalització tipogràfica dels textos sense alterar les rimes fonètiques originals (mantenint vocalismes i reduccions pròpies del cant popular).
  3. Classificació automàtica per eixos temàtics: Feines del camp, Calendari i Sants, Amor i festeig, Sàtira social.
* **Volum objectiu**: ~2.000 dites rimades i cobles autòctones.

### Fase 4: Integració de Microtoponímia Insular (Mes 4)
* **Objectiu**: Relacionar el paisatge físic de Mallorca amb la toponímia lèxica autòctona.
* **Mètode Tècnic**:
  1. Connexió amb el servei WFS/GeoJSON del visualitzador oficial de l'IDEIB (`ideib.caib.es/geoservices`).
  2. Filtre intel·ligent per seleccionar topònims amb càrrega lèxica descriptiva (accidents orogràfics, fites de pedra en sec, barraques de vinya, avencs i fonts).
  3. Transformació de cada topònim seleccionat en una fitxa enriquida amb etimologia, transcripció aproximada i coordenades del terme municipal.
* **Volum objectiu**: ~1.000 microtopònims d'alt valor patrimonial.

### Fase 5: Canal de Recollida Viva i Crowdsourcing (Mes 5 en endavant)
* **Objectiu**: Mantenir la base de dades en creixement continu gràcies a les aportacions dels parlants d'avui.
* **Mètode Tècnic**:
  1. Habilitació a la interfície web d'un formulari de participació amb camps senzills: *Paraula o dita*, *Poble o comarca on es diu*, *Significat explicat*, *Exemple d'ús en una frase*, *Correu de contacte opcional*.
  2. Ingesta a una taula temporal de revisió `crowdsourced_submissions` a `curiositats.db`.
  3. Revisió comunitària mensual coordinada amb assessors de l'OCB i associacions culturals abans del traspàs definitiu a la taula pública `words`.

---

## 4. Alineació amb l'Esquema de Dades de `curiositats.db`

Totes les dades extretes dels diferents pilars s'han d'adaptar de manera coherent a l'esquema relacional de la taula `words` definit a `database/schema.sql`:

```sql
CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term VARCHAR(150) NOT NULL UNIQUE,
    ipa_pronunciation VARCHAR(100),
    grammatical_category VARCHAR(50),
    definition TEXT NOT NULL,
    example_sentence TEXT,
    etymology TEXT,
    dialectal_notes VARCHAR(150),
    source_reference VARCHAR(255) DEFAULT 'Diccionari Català-Valencià-Balear (Alcover-Moll)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.1. Mapatge de Camps segons la Font d'Origen

| Camp de la BBDD | Pilar 1: Rondaies | Pilar 2: Cançoner / Gloses | Pilar 3: Microtoponímia | Pilar 6: Crowdsourcing |
| :--- | :--- | :--- | :--- | :--- |
| `term` | Lema o frase feta de la rondalla (ex: *fer sa quarentena*) | Primera línia de la quarteta o refrany rimat | Nom del topònim (ex: *Es Pas Vermell*) | Mot o dita introduïda per l'usuari |
| `ipa_pronunciation` | Pronunciació local aproximada | Rima i accentuació mètrica | Fonètica del municipi | Opcional / Revisada per comitè |
| `grammatical_category` | `expressió`, `frase feta`, `fórmula narrativa` | `dita`, `refrany`, `glosa` | `microtopònim`, `nom propi de lloc` | Determinada durant la moderació |
| `definition` | Significat narratiu i context dins el conte | Explicació del sentit satíric o moral de la cobla | Descripció física de l'indret i accident geogràfic | Definició redactada pel parlant |
| `example_sentence` | Cita literal del personatge a la rondalla | Quarteta sencera de la glosa | *"Indret situat a la falda del Puig de..."* | Frase quotidiana proposada pel ciutadà |
| `etymology` | Etimologia històrica (llatí, àrab, romànic) | Refranys paral·lels o arrels tradicionals | Arrel toponímica (mossàrab, catalana, llatina) | Investigada durant la validació |
| `dialectal_notes` | Municipi d'origen del narrador de la rondalla | Comarca de recollida (Pla, Tramuntana, etc.) | Terme municipal i coordenades | Poble informat per l'usuari |
| `source_reference` | `Aplec de Rondaies Mallorquines (Alcover), Tom IV` | `Cançoner Popular de Mallorca (Ginard), Vol. II, núm. 412` | `Nomenclàtor IDEIB / Mascaró Pasarius` | `Recollida oral ciutadana (validat OCB)` |

---

## 5. Mecanismes de Normalització, Desduplicació i Control de Qualitat (*Quality Gates*)

Per mantenir l'excel·lència filològica de la base de dades, cap dada externa no s'insereix directament a la taula de producció sense superar tres filtres estrictes:

### 5.1. Normalització Tipogràfica i Dialectal
1. **Ela geminada**: Conversió automàtica de variants com `l-l`, `l.l` o `ll` no geminada a la forma canònica amb punt volat `l·l` (*al·lot*, *col·legi*).
2. **Apòstrofs i Article Salat**: Garantir l'ús de l'apòstrof tipogràfic recte (`'`) sense espais inconsistents (*s'alqueria*, *es camp*, *sa coma*).
3. **Manteniment de les formes verbals salades i dialectals**: Conservació dels clítics i formes verbals pròpies en els exemples d'ús (*feim*, *veim*, *dèiem*, *mos*, *vos*), tot oferint el lema infinitiu normatiu per a la cerca principal.

### 5.2. Algoritme de Desduplicació
Atès que el camp `term` disposa d'una restricció d'unicitat (`UNIQUE`), el motor d'ingesta utilitza la següent lògica:
* Si el terme ja existeix a `curiositats.db`:
  1. Si l'entrada existent no tenia `example_sentence` i la nova font en conté un de literari (com les rondalles o el cançoner), s'enriqueix l'entrada existent conservant l'anterior.
  2. Si l'entrada ja té una definició acadèmica (DCVB/DIEC2), s'afegeix la dita com a subaccepció o exemple, preservant la font primària.
  3. Si es tracta d'una frase feta homònima amb un significat diferent, es desambigua afegint la marca de context entre parèntesis.

### 5.3. Circuit de Moderació en 4 Estats (*Quality Gates*)

```
[ 1. Ingestat Brut (Raw) ]
           |
           v  (Comprovació d'esquema, caràcters, UTF-8 i absència de nuls)
[ 2. Validat per Algorisme ]
           |
           v  (Revisió filològica: ortografia, definició clara, absència de faltes greus)
[ 3. Validat per Comitè Lingüístic ]
           |
           v  (Inserció definitiva a `words` i indexació al cercador web)
[ 4. Publicat a Producció ]
```

---

## 6. Arquitectura Tècnica dels Scripts d'Ingesta

Tota la infraestructura d'extracció s'articula mitjançant scripts autònoms, modulars i idempotents en Python situats a la carpeta `scripts/`:

```
c:\Users\gabri\Documents\curiositats\scripts\
├── scrapers\
│   ├── dcvb_crawler.py              # Crawler autoritatiu XML de motor-bdlex.iec.cat (Fase 1)
│   ├── viccionari_extractor.py      # Extractor de categories Mallorquí i Balear (Fase 1)
│   ├── wikisource_rondaies_parser.py# Parser de contalles i fórmules alcoverianes (Fase 2)
│   └── canconer_gloses_parser.py    # Processador de quartetes i poesia oral (Fase 3)
├── importers\
│   ├── import_diec.py               # Ingestor del JSON balear del DIEC2 a SQLite (Fase 1)
│   ├── import_sitibsa_toponims.py   # Ingestor GeoJSON de toponímia insular (Fase 4)
│   └── crowdsourcing_processor.py   # Gestor de la cua de moderació comunitària (Fase 5)
└── utils\
    ├── dialect_normalizer.py        # Mòdul de neteja, ela geminada i accents
    └── deduplicator.py              # Comprovador de lemes i unicitat
```

Tots els scripts comparteixen una política de:
* **Execució idempotent**: Es poden tornar a executar tantes vegades com calgui sense produir errors d'integritat de clau primària ni duplicació de dades.
* **Memòria cau local**: Emmagatzematge dels continguts descarregats a `database/cache/` per no sobrecarregar els servidors de les universitats ni de la Viquipèdia.
* **Generació de fitxers JSON intermedis**: Abans d'escriure a la base de dades SQLite, els conjunts de dades es guarden en fitxers estructurats a `database/` per facilitar auditories independents.

---

## 7. Indicadors d'Èxit (KPIs) i Impacte Cultural

Per avaluar l'eficàcia de l'estratègia d'absorció massiva, s'estableixen els següents indicadors de seguiment trimestral:

| Indicador (KPI) | Valor Inicial (Actual) | Objectiu 6 Mesos | Objectiu 12 Mesos |
| :--- | :---: | :---: | :---: |
| **Nombre total de lemes i dites a `words`** | ~140 entrades | 5.000 entrades | 12.000 entrades |
| **Percentatge de termes amb exemples reals d'ús** | < 40% | > 85% | > 95% |
| **Percentatge de termes amb pronunciació IPA** | < 25% | > 60% | > 80% |
| **Cobertura territorial per municipis de Mallorca** | 12 municipis | 35 municipis | 53 municipis (100% de Mallorca) |
| **Volum de col·laboracions ciutadanes rebudes** | 0 | 250 aportacions | 1.000 aportacions |

Amb aquest pla integral, «Una teringa de curiositats» no només assegura un creixement exponencial de continguts de gran qualitat, sinó que es posiciona com una plataforma capdavantera en la preservació digital i la difusió activa del patrimoni dialectal de les Illes Balears.

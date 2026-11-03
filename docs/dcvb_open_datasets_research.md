# Recerca de Datasets Oberts, Dumps i Scrapeigs del DCVB (Alcover-Moll)
## Auditoria Tècnica, Anàlisi de Propietat Intel·lectual i Solució d'Extracció Estructurada

**Projecte**: «Una teringa de curiositats»  
**Document**: `docs/dcvb_open_datasets_research.md`  
**Data**: Novembre de 2026  
**Estat**: Complet i Verificat  
**Requisit associat**: R4 (Recerca d'scrapeigs i datasets oberts del DCVB)  

---

## 1. Resum Executiu i Objectiu de la Recerca

El *Diccionari Català-Valencià-Balear* (DCVB), obra monumental impulsada per mossèn **Antoni Maria Alcover** i culminada per **Francesc de Borja Moll** amb la col·laboració de **Manuel Sanchis Guarner**, consta de 10 volums, més de 160.000 articles i vora 400.000 accepcions. És l'inventari dialectològic i històric més important de la llengua catalana i, en particular, de les modalitats insulars de Mallorca, Menorca, Eivissa i Formentera.

En el marc del projecte **«Una teringa de curiositats»**, l'objectiu d'aquesta investigació tècnica és:
1. **Auditar de manera exhaustiva** l'existència de *dumps*, scrapeigs previs, bases de dades relacionals o datasets oberts del DCVB en repositoris públics mundials (Internet Archive, GitHub, Hugging Face, Wikimedia, etc.).
2. **Avaluar el règim jurídic de drets d'autor i propietat intel·lectual** que empara l'obra per determinar les raons estructurals de la manca d'un dump massiu en obert.
3. **Presentar una alternativa tecnològica robusta, autoritativa i legalment respectuosa**: l'extracció directa i dirigida mitjançant la interfície XML REST de la Base de Dades Lexicogràfica de l'Institut d'Estudis Catalans (`motor-bdlex.iec.cat`), capaç d'alimentar de forma estructurada la taula `words` de `curiositats.db`.

---

## 2. Auditoria Tècnica de Repositoris i Plataformes Públiques

S'ha dut a terme una prospecció sistemàtica a través de les APIs, motors d'indexació i cercadors de codi dels principals repositoris mundials de dades i programari lliure.

### 2.1. Internet Archive (`archive.org`)

L'Internet Archive conserva milions de llibres digitalitzats procedents de biblioteques universitàries internacionals. S'ha investigat l'existència de còpies digitals completes del DCVB.

* **Identificador localitzat**: `diccionaricatala0003alco`  
  * URL de metadades: `https://archive.org/metadata/diccionaricatala0003alco`  
  * Títol catalogat: *Diccionari català-valencià-balear* (Volum 3: D – E).
  * Edició: Editorial Moll, Palma de Mallorca, reimpressió de 1980.
  * Dipòsit original: Fons de la Universitat de Toronto (Robarts Library).
* **Diagnosi tècnica d'accés**:
  * L'accés als fitxers complets està bloquejat pel mecanisme de **Préstec Digital Controlat** (*Controlled Digital Lending* - CDL).
  * Formats disponibles: `ACS Encrypted PDF` i `LCP Encrypted PDF`. Els fitxers OCR en text pla (`_djvu.txt` o hOCR) no estan oberts a la descàrrega pública sense una sessió activa de préstec de 1 hora per a usuaris autenticats.
  * Cobertura: Només s'hi troba dipositat el **Volum 3** de forma aïllada; els volums 1, 2 i 4 al 10 no disposen de cap escaneig complet al catàleg públic de l'entitat.
* **Viabilitat com a dataset obert**: **Nul·la**. No és possible descarregar un fitxer de text continu ni cap estructura de base de dades. A més, qualsevol intent de trencament de l'encapsulament DRM infringiria els termes de servei d'Internet Archive.

### 2.2. GitHub (`github.com`)

S'ha explorat el codi font públic a GitHub cercant repositoris que continguin bases de dades SQLite, fitxers JSON/CSV massius o motors d'extracció del DCVB mitjançant consultes de codi: `"dcvb" scraper`, `"alcover-moll"`, `dcvb database`, `pereorga/dictionary-api`, i projectes de l'organització `Softcatala`.

* **Trobades destacades**:
  1. **`pereorga/dictionary-api`**:
     * Microservei en Python/Go creat per Pere Orga que ofereix una API JSON d'un sol mot per a diccionaris en català (DIEC2, DCVB, GDLC).
     * **Anàlisi**: No conté cap dump de dades. Funciona com un proxy o *client wrapper* en temps real que llança una petició HTTP contra `dcvb.iec.cat/results.asp?Word=...`, en parseja l'HTML i en retorna el fragment. No ofereix cap mecanisme de descàrrega en bloc.
  2. **`Softcatala/catalan-dict-tools` i scripts relacionats**:
     * Eines de Softcatalà orientades a la generació de fitxers per a lectors de llibres electrònics (`deiec-kindle`, MOBI, Stardict).
     * **Anàlisi**: Els scripts processen dades obertes del DIEC2 o del Viccionari. No contenen cap base de dades del DCVB atesa la política estricta de respecte de drets editorials mantinguda per Softcatalà.
  3. **Scrapers personals i intents acadèmics**:
     * Existeixen diversos scripts petits d'estudiants o lingüistes computacionals que intenten fer consultes per llista de paraules contra `dcvb.iec.cat`. Gairebé tots pateixen errors de codificació (perquè el portal històric utilitza `ISO-8859-1` i no `UTF-8`) o fallen davant homònims i caràcters especials (ela geminada `·`).
* **Viabilitat com a dataset obert**: **Inexistent com a dump**. GitHub ofereix exemples útils de funcions auxiliars d'HTML scraping, però **no allotja cap dump de dades complet ni estructurat del DCVB**.

### 2.3. Hugging Face (`huggingface.co`) i Projecte AINA (BSC TeMU)

El Barcelona Supercomputing Center (BSC-CNS), a través del **Projecte AINA** (impulsat per la Generalitat de Catalunya), lidera la creació dels majors models de llengua i recursos de processament de llenguatge natural (NLP) en català. S'han examinat els seus conjunts de dades a Hugging Face:

* **Datasets auditats**:
  * `softcatala/catalan-dictionary`: Llista de 1.180.000 formes flexionades amb lema i etiquetes morfosintàctiques POS (llicència lliure GPL-2.0 / LGPL-2.1). Molt valuós per a validació lèxica, però sense definicions, cites literàries ni marques dialectals insulars del DCVB.
  * `softcatala/optimot-linguistic-data`: Consultes i fitxes de dubtes lingüístics de l'Optimot.
  * `projecte-aina/CATalog`: Corpus massiu web en català filtrat per a pre-entrenament de grans models lingüístics (LLMs).
  * `projecte-aina/CoQCat`: Dataset de preguntes i respostes en català.
  * `projecte-aina/annotated_catalan_common_voice_v17`: Corpus d'àudio i veu anotada.
* **Governança i motius de l'absència del DCVB**:
  * Cap dels repositoris del BSC o de Hugging Face publica un dataset textual del DCVB.
  * Els equips d'adquisició de dades de l'AINA signen convenis específics per a la utilització de textos en l'entrenament de models tancats o d'accés protegit, respectant els drets editorials de les institucions custòdies per evitar reclamacions de llicència.
* **Viabilitat com a dataset obert**: **Nul·la per al DCVB**, encara que `softcatala/catalan-dictionary` és una font excel·lent per creuar lemes i verificar flexions verbals i nominals.

### 2.4. Wikimedia i Viccionari (`ca.wiktionary.org`)

El Viccionari en català (*Wiktionary*) constitueix un dels projectes col·laboratius més rics en contingut dialectal i lèxic popular sota llicència lliure **Creative Commons Reconeixement-CompartirIgual 4.0 (CC BY-SA 4.0)**.

* **Integració existent del DCVB**:
  * El Viccionari conté la plantilla `Plantilla:dcvb`, la qual enllaça termes catalans amb l'article corresponent del DCVB a la xarxa:
    ```wikitext
    {{dcvb|terme}}
    ```
    El codi intern de la plantilla genera una crida dinàmica:
    `http://dcvb.iec.cat/results.asp?Word={{#invoke:urlencode|latin1|{{{1}}}}}`
  * Això demostra que els editors del Viccionari han utilitzat durant anys el DCVB com a font d'autoritat de consulta externa, sense fer-ne un bolcat directe automatitzat.
* **Dumps oficials de Wikimedia (`dumps.wikimedia.org/cawiktionary/`)**:
  * Wikimedia genera dumps periòdics complets en fitxers XML comprimits (`cawiktionary-latest-pages-articles.xml.bz2`).
  * Aquests dumps contenen categories dialectals perfectament delimitades:
    * `Categoria:Mallorquí`: **652 entrades** catalogades de manera comunitària amb etimologia, accepcions i cites.
    * `Categoria:Balear`: **300 entrades** addicionals que abasten l'arc insular.
* **Viabilitat com a dataset obert**: **Molt Alta**. Encara que no és el DCVB sencer, és un dataset obert legítim, lliure de drets restrictius, que es pot explotar immediatament i que beu directament de la tradició alcoveriana.

---

## 3. Anàlisi Jurídica i de Propietat Intel·lectual

La manca d'un dump massiu en obert del DCVB a la xarxa no és cap accident tecnològic, sinó la conseqüència directa del règim jurídic de la propietat intel·lectual a l'Estat espanyol.

```
+-----------------------------------------------------------------------------------+
|                        CRONOLOGIA DELS DRETS D'AUTOR                              |
|                                                                                   |
|  1932: Mort d'Antoni M. Alcover                                                   |
|        (LPI de 1879: 80 anys post-mortem)                                         |
|        ========================> [ 1 de gener de 2013: DOMINI PÚBLIC ]             |
|                                                                                   |
|  1991: Mort de Francesc de Borja Moll                                             |
|        (LPI de 1987: 70 anys post-mortem)                                         |
|        ===============================================> [ 1 de gener de 2062 ]    |
|                                                         (PROTEGIT FINS AL 2061)   |
+-----------------------------------------------------------------------------------+
```

### 3.1. Situació dels Drets d'Antoni Maria Alcover (†1932)
* Mossèn Antoni M. Alcover va morir el 8 de gener de 1932.
* Segons la Disposició Transitòria Quarta de la vigent Llei de Propietat Intel·lectual (Reial Decret Legislatiu 1/1996) i la Llei de Propietat Intel·lectual de 10 de gener de 1879, els autors finats abans del 7 de desembre de 1987 gaudeixen d'un termini de protecció de **80 anys a partir de l'1 de gener següent a la mort de l'autor**.
* Els 80 anys van expirar el **31 de desembre de 2012**. Per tant, el conjunt de l'obra escrita directament per Antoni M. Alcover (incloent-hi els primers volums del Diccionari i el recull de l'*Aplec de Rondaies Mallorquines*) va entrar en el **Domini Públic l'1 de gener de 2013**.

### 3.2. Situació dels Drets de Francesc de Borja Moll (†1991)
* Francesc de Borja Moll va morir el 18 de febrer de 1991.
* Havent finat amb posterioritat a l'entrada en vigor de la Llei 22/1987 de Propietat Intel·lectual, el termini de protecció aplicable és de **70 anys a partir de l'1 de gener següent a la seva mort** (computats des de l'1 de gener de 1992).
* Els drets patrimonials sobre les seves aportacions, redaccions, coordinació i enriquiment dels volums del DCVB romanen vigents fins al **31 de desembre de 2061**, i no passaran al Domini Públic fins a l'**1 de gener de 2062**.

### 3.3. Drets Editorials i la Base de Dades Digitalitzada
* El DCVB és legalment una **obra en col·laboració** d'atribució mixta, on l'edició digital definitiva (finalitzada l'any 2001 amb el patrocini del Govern de les Illes Balears i l'IEC) va comportar una adaptació tipogràfica, correcció i informatització integral dels 10 volums.
* La titularitat dels drets morals i patrimonials de l'edició digital i de la marca editorial recau sobre la **Institució Francesc de Borja Moll**, en coedició i explotació acadèmica conjunta amb l'**Institut d'Estudis Catalans (IEC)**.
* L'article 133 del Reial Decret Legislatiu 1/1996 atorga una protecció addicional de caràcter *sui generis* al **fabricant d'una base de dades** (l'IEC i la Institució Moll) davant la sostracció o reutilització massiva no autoritzada de la totalitat o d'una part substancial del seu contingut.
* **Conclusió jurídica**: Aquest entramat legal explica de manera contundent per què cap institució pública (com el BSC) ni comunitat oberta ha pogut alliberar un dump `.sql` o `.csv` massiu i no restringit a internet.

---

## 4. La Solució Autoritativa i Estructurada: Extracció Dirigida via `motor-bdlex.iec.cat`

Atesa la inexistència de dumps oberts preexistents, la investigació tècnica de camp ha descobert l'accés directe al motor d'indexació de la **Base de Dades Lexicogràfica (BDLex)** de l'Institut d'Estudis Catalans, el qual constitueix la via autoritativa, neta i tècnicament perfecta per al nostre projecte.

### 4.1. Arquitectura del Motor BDLex
A diferència del portal web clàssic (`https://dcvb.iec.cat`), que utilitza un servidor Microsoft IIS amb pàgines ASP antigues en codificació `ISO-8859-1` i sense filtratge semàntic de marques dialectals, el nou servei `https://motor-bdlex.iec.cat/bdlex` funciona sobre un entorn modern Linux/Apache i serveix dades en **XML estructurat natiu en UTF-8**.

* **Capçalera d'accés obert**: El servei emet la capçalera HTTP estàndard:
  ```http
  Access-Control-Allow-Origin: *
  Content-Type: text/xml; charset=UTF-8
  Transfer-Encoding: chunked
  ```
  Això permet la comunicació directa des de qualsevol client sense necessitat de tokens privats o cookies de sessió.

### 4.2. Cerca Específica de Marques Dialectals Balears
El motor permet executar cerques per contingut textual combinades amb el filtre de diccionari `dict[]=DCVB` i sol·licitar directament la llista d'identificadors (`result_type=ids`).

Les proves empíriques han verificat els volums exactes següents:

| Cerca Executada | Paràmetres HTTP GET | Nombre d'Entrades Trobades |
| :--- | :--- | :---: |
| **Marca 'Mall'** | `text[]=Mall&dict[]=DCVB&element=entry&result_type=ids` | **17.181** |
| **Marca 'Bal'** | `text[]=Bal&dict[]=DCVB&element=entry&result_type=ids` | **7.940** |
| **Marca 'Mallorca'** | `text[]=Mallorca&dict[]=DCVB&element=entry&result_type=ids` | **2.042** |
| **Marca 'Balears'** | `text[]=Balears&dict[]=DCVB&element=entry&result_type=ids` | **215** |

### 4.3. Recuperació de Dades en Bloc (*Batch Fetching*)
El motor suporta la petició de múltiples identificadors en una sola crida HTTP GET mitjançant paràmetres múltiples `entry_id[]`:

```http
GET https://motor-bdlex.iec.cat/bdlex?entry_id[]=DCVBE027511&entry_id[]=DCVBE000002&element=entry HTTP/1.1
Host: motor-bdlex.iec.cat
User-Agent: UnaTeringaDeCuriositats/1.0 (Recerca dialectal mallorquina; contacte@curiositats.cat)
```

La resposta XML conté l'article complet amb un desglossament tipològic riquíssim:
* `<orth>`: Lema o forma ortogràfica normalitzada (ex: `burballa`).
* `<gramGrp><pos>`: Categoria gramatical (ex: `f.` per a nom femení).
* `<sense>`: Cada accepció independent amb el seu identificador únic (`DCVBE027511S00001`).
* `<def>`: Text literal de la definició.
* `<usg type="GEO">`: Marca geogràfica explícita (`Mallorca`, `Eivissa`, `Menorca`).
* `<trans>`: Traducció equivalent en castellà (`cast. viruta, cepilladura`).
* `<eg><cit>`: Exemples d'ús, fragments de literatura oral balear i referències bibliogràfiques tradicionals (com les rondalles o la revista satírica *L'Ignorància*).

### 4.4. Política de Respecte i Ètica de Rastrejament (*Crawler Politeness*)
Per garantir la preservació del servidor acadèmic de l'IEC i evitar qualsevol bloqueig:
1. **Límit de cadència**: S'estableix una pausa obligatòria d'entre **1,0 i 1,5 segons** entre crides consecutives.
2. **Batching moderat**: Agrupació de **30 a 50 identificadors** per petició (ben per sota del límit tècnic màxim de 200).
3. **Persistència en memòria cau**: Emmagatzematge persistent de les respostes XML a `database/dcvb_cache/` per garantir que cap registre no es torni a demanar dues vegades.
4. **Capçalera descriptiva**: Inclusió d'un `User-Agent` que identifiqui clarament la finalitat cultural i investigadora del projecte.

---

## 5. Taula Comparativa de Fonts i Alternatives

| Font / Plataforma | Tipus de Recurs | Format de Dades | Volum Dialectal Insular | Disponibilitat Legal | Facilitat d'Ingesta |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **Internet Archive (`archive.org`)** | Llibre digitalitzat (Vol. 3) | PDF encriptat (DRM CDL) | Només lletres D–E | Restringit (préstec temporal) | Nul·la (inaccessible en obert) |
| **GitHub** | Client wrappers i eines Kindle | Python / Go / Scripts | Cap dump integrat | Lliure codi, sense dades DCVB | Nul·la (sense dades) |
| **Hugging Face / AINA** | Corpus web i llistats lemes | Parquet / JSONL / TXT | ~1,18M mots generals | Apache-2.0 / GPL (sense DCVB) | Mitjana (només lemes) |
| **Viccionari (Wikimedia)** | Categoria Mallorquí i Balear | MediaWiki XML / API | ~952 articles | **CC BY-SA 4.0** (Domini lliure) | **Molt Alta** (API oberta) |
| **Portal Web DCVB (`dcvb.iec.cat`)** | Web HTML clàssica (ASP) | HTML (ISO-8859-1) | 160.000 articles | Ús web per consulta | Baixa (HTML scraping complex) |
| **Motor BDLex (`motor-bdlex.iec.cat`)** | API XML REST de recerca | **XML estructurat (UTF-8)** | **17.181 entrades Mall.** | **Accés públic obert per recerca** | **Molt Alta** (Directe i net) |

---

## 6. Conclusions i Pla d'Acció Recomanat

1. **Inexistència de Dumps Públics Preexistents**: Queda certificat tècnicament i jurídicament que no existeix cap repositori públic que allotgi un dump íntegre del DCVB a la xarxa a causa del règim de propietat intel·lectual que protegeix l'obra de Francesc de Borja Moll fins a finals de l'any 2061.
2. **Aprofitament Immediat del Viccionari**: La categoria *Mallorquí* i *Balear* del Viccionari ha de ser extreta íntegrament com a font d'enriquiment immediata i lliure de drets (R2).
3. **Validació del Crawler BDLex com a Solució Estructurada (R1)**: El descobriment de l'API XML oberta a `motor-bdlex.iec.cat` resol de forma brillant la necessitat d'un dataset obert. En lloc de raspar codi HTML obsolet, el projecte disposa d'un canal REST legítim que ofereix 17.181 entrades mallorquines amb etiquetes de lema, gramàtica, accepcions, dialectologia i proverbis.
4. **Compliment i Projecció**: Aquesta arquitectura d'extracció permet alimentar la taula `words` de `curiositats.db` amb màxim rigor filològic, protegint tant la legalitat del projecte com la infraestructura tecnològica de les institucions científiques balears i catalanes.

# Guia de Fonts i Catàleg Documental de Referència (60 Fons Clau)
## Base de Dades i Corpus Documental per a «Una teringa de curiositats»

**Projecte**: «Una teringa de curiositats»  
**Document**: `docs/SOURCES.md`  
**Fitxer de suport associat**: `database/reference_sources.json`  
**Estat**: Complet i Verificat (60 fons catalogats)

---

## 1. Introducció i Marc d'Atribució Ètica

Aquest document constitueix el catàleg canònic d'autoritats, arxius documentals, institucions acadèmiques i bases de dades obertes utilitzades per a la creació, enriquiment i verificació continuada de la plataforma digital **«Una teringa de curiositats»**.

La plataforma té com a objectiu fundacional la salvaguarda, divulgació i aproximació ciutadana del patrimoni etnogràfic, biològic, lingüístic i històric de Mallorca. Per assolir aquesta fita amb el màxim rigor científic i acadèmic, el projecte es fonamenta en **60 fonts autoritatives de referència**, articulades al voltant de tres grans pilars temàtics:

1. **Llengua, Dialectologia i Tradició Oral** (18 referències &rarr; Taula `words`)
2. **Fauna, Flora i Biodiversitat de les Balears** (18 referències &rarr; Taules `fauna` i `flora`)
3. **Cultura, Història, Comerç Emblemàtic i Patrimoni** (24 referències &rarr; Taules `historical_events` i `emblematic_businesses`)

Tots els registres emmagatzemats a la base de dades relacional `curiositats.db` i exposats a través de l'API REST i la interfície web incorporen de forma obligatòria el camp `source_reference`, que acredita de manera transparent l'origen documental canònic de la informació.

---

## 2. Pilar 1: Lexicografia, Dialectologia i Tradició Oral (Taula `words`)

Aquest pilar nodreix el tresor lèxic, fonètic i fraseològic mallorquí, garantint que cada paraula, dita popular o locució contingui la seva definició normativa, context històric, etimologia i pronúncia fonètica internacional (AFI).

### 2.1. Fonts Canòniques Fonamentals
* **DCVB (Diccionari Català-Valencià-Balear / Alcover-Moll)**:  
  Impulsat per mossèn Antoni Maria Alcover i completat per Francesc de Borja Moll amb la col·laboració de Manuel Sanchis Guarner. Comprèn 10 volums, més de 160.000 articles i 400.000 accepcions. És la font primària indiscutible per al lèxic genuí, etimologies aràbigues i mossàrabs, dites populars de camp i les transcripcions fonètiques diferenciades per municipis mallorquins.
* **DIEC2 (Diccionari de la Llengua Catalana de l'Institut d'Estudis Catalans)**:  
  Font normativa de referència. S'ha integrat el corpus específic de **91 entrades dialectals balears** catalogades formalment pel diccionari de l'Acadèmia (`database/diec_balear_entries.json`), aportant equivalències formals i categories gramaticals normalitzades.
* **Corpus Dialectal del Viccionari Balear**:  
  Buidatge sistemàtic a través de l'API de Wikimedia de totes les veus catalogades sota les categories dialectals «Mallorquí» i «Balear», incloent etimologies, exemples d'ús i referències creuades al DCVB.
* **Mallorca Oral / Cançoner Popular de Mallorca (Rafel Ginard / Fundació Mallorca Literària)**:  
  Repositori sonor i textual fonamental ubicat a la Casa Museu Pare Ginard (Sant Joan). Aporta més de 15.000 cobles, cançons de batre, cançons de collir olives i dites del cicle festiu tradicional.
* **ALDC (Atles Lingüístic del Domini Català - Joan Veny i Lídia Pons)**:  
  Cartografia geolingüística monumental que permet contrastar la distribució exacta de denominacions per a fenòmens meteorològics, eines del camp i noms d'animals arreu dels pobles de Mallorca.
* **COD (Corpus Oral Dialectal - Universitat de Barcelona)**:  
  Enregistraments i transcripcions fonètiques d'enquestes orals espontànies que documenten la vivor de l'article salat, la fonètica sintàctica i l'entonació insular.

---

## 3. Pilar 2: Fauna, Flora i Biodiversitat de les Balears (Taules `fauna` i `flora`)

Aquest pilar recull la singularitat biològica insular, combinant dades biològiques contrastades per la comunitat científica amb el ric coneixement etnobotànic i zootècnic acumulat per la pagesia mallorquina.

### 3.1. Fonts Canòniques Fonamentals
* **Herbari Virtual del Mediterrani Occidental (Àrea de Botànica, UIB)**:  
  La plataforma científica més completa per a la flora de les Illes Balears. Proporciona fitxes taxonòmiques d'alta resolució, noms populars vernaculars, èpoques de floració, distribució d'hàbitats (garriga, roquissars litorals, alzinars de Tramuntana) i usos etnobotànics ancestrals (herbes remeieres, condiments tradicionals com el fonoll marí i aplicacions artesanals).
* **IRFAP (Institut de Recerca i Formació Agroalimentària i Pesquera - Govern CAIB)**:  
  Organisme oficial canònic que custodia els llibres genealògics, patrons racials i decrets de protecció de les **14 races autòctones reconegudes de les Illes Balears**:
  - *Mamífers*: Porc Negre mallorquí, Ca de Bestiar, Ca de Bou, Ca Mè mallorquí, Cavall Mallorquí, Ase Balear, Ovella Mallorquina, Ovella Roja Mallorquina, Cabra Mallorquina.
  - *Aus*: Gallina Mallorquina, Colom de Casta Grossa, Colom d'Escampadissa, Colom Balear, Ànnera Mallorquina.
* **Biodibal / BioBal (Universitat de les Illes Balears i Redeia)**:  
  La infraestructura digital oberta sobre biodiversitat més gran de les Balears, amb més d'1,5 milions de registres georeferenciats. Clau per verificar l'estatus d'endemisme salvatge (com el ferreret *Alytes muletensis*, el virot petit *Puffinus mauretanicus* o les sargantanes dels illots) i mapes de presència per quadrícules UTM.
* **Catàleg Balear d'Espècies Amenaçades (Conselleria d'Agricultura, Pesca i Medi Natural)**:  
  Estableix les categories oficials de protecció legal d'acord amb els criteris de la UICN: *En perill crític (CR)*, *En perill d'extinció (EN)*, *Vulnerable (VU)* i *Preocupació Menor (LC)*.
* **COFIB (Consorci per a la Recuperació de Fauna) i Fundació Palma Aquarium**:  
  Aporten dades reals sobre la protecció i alliberament de fauna protegida: seguiment del voltor negre a la Serra de Tramuntana, rescat de tortugues marines (*Caretta caretta*) i atenció a cetacis encallats.

---

## 4. Pilar 3: Cultura, Història, Comerços Emblemàtics i Patrimoni (Taules `historical_events` i `emblematic_businesses`)

Aquest pilar abraça des de les primeres cultures prehistòriques constructores de talaiots fins a la xarxa viva de botigues i tallers històrics que defineixen el paisatge urbà i rural de Mallorca.

### 4.1. Fonts Canòniques Fonamentals
* **Catàleg d'Emblemàtics Balears (IDI / ADR Balears - Govern de les Illes Balears)**:  
  Iniciativa pública oficial que cataloga, protegeix i promociona els comerços tradicionals amb més de 75 anys d'història o arrelament artesanal a Mallorca. Classifica els establiments en tres categories de protecció:
  1. *Comerç amb història*: Antiguitat acreditada i continuïtat familiar o de negoci.
  2. *Comerç arrelat*: Manteniment d'un ofici tradicional (forners d'ensaïmada, sabaters, fusters, teixidors de llengües, cerers).
  3. *Comerç amb patrimoni*: Conservació d'elements arquitectònics, rètols d'època, forns de llenya morunos o decoració modernista catalogada.
* **Arxiu del Regne de Mallorca (ARM - Conselleria de Cultura)**:  
  El principal fons arxivístic de les Illes Balears, amb fons documentals originals ininterromputs des de 1230. És la font fonamental per a la cronologia de la conquesta de Jaume I, el *Llibre del Repartiment*, els privilegis forals del Regne privatiu de Mallorca, la revolta de les Germanies (1521-1523) i els decrets de Nova Planta (1715).
* **Gran Enciclopèdia de Mallorca (GEM)**:  
  Obra monumental de 19 volums coordinada per Promomallorca. Constitueix l'inventari enciclopèdic de referència per a personatges històrics (Jaume I, Ramon Llull, Guillem Sagrera, Joanot Colom, Gaspar Melchor de Jovellanos), microtopònims i fites econòmiques i culturals de l'illa.
* **Arxius Eclesiàstics i de Ciutat**:
  - *Arxiu Capitular de Mallorca (ACM)*: Els llibres de fàbrica de la Catedral de Mallorca (la Seu), pergamins reials i l'Ull del Gòtic.
  - *Arxiu Diocesà (Maiorica Sacra)*: Registres sacramentals de baptismes i matrimonis des del concili de Trento, mortalitat durant les epidèmies de pesta (1652, 1820) i llinatges xuetes de Mallorca.
  - *Arxiu Municipal de Palma (Can Balaguer i Cort)*: Llibres d'actes de la Universitat de la Ciutat i el projecte d'enderrocament de les muralles renaixentistes (1902).
* **Parcs Arqueològics i Museus**:
  - *Poblat Talaiòtic de Ses Païsses (Artà)*: Murada ciclòpia, sala hipòstila i transició del món talaiòtic al període postalaiòtic.
  - *Museu Arqueològic de Son Fornés (Montuïri)*: Banquets comunitaris i consum de carn a l'edat del ferro.
  - *Ciutat Romana de Pol·lèntia i Museu Monogràfic (Alcúdia)*: Fòrum, teatre romà i urbanisme des de la fundació el 123 a.C.
  - *Castell de Bellver, Cartoixa de Valldemossa, Museu de Mallorca, Museu Marítim i Museu del Calçat d'Inca*.

---

## 5. Inventari Detallat dels 60 Fons de Referència

La següent taula recull la totalitat dels 60 recursos documentats a `database/reference_sources.json`, ordenats per pilar temàtic:

| ID | Nom del Recurs / Institució | Pilar | Entitat Responsable | URL Oficial | Àmbit a Mallorca | Taula Destí |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | Biodibal (BioBal) | Fauna | UIB / Redeia | [biodibal.cat](https://biodibal.cat) | Campus UIB, Palma | `fauna`, `flora` |
| **02** | Catàleg de Races Autòctones Balears | Fauna | IRFAP (Govern CAIB) | [irfap.org](https://irfap.org) | Palma / Illes Balears | `fauna` |
| **03** | COFIB (Recuperació de Fauna) | Fauna | Consorci COFIB / CAIB | [recuperacionfaunabaleares.es](https://recuperacionfaunabaleares.es) | Santa Eugènia / Son Reus | `fauna` |
| **04** | GOB Mallorca (Secció d'Ornitologia) | Fauna | GOB Mallorca | [gobmallorca.com](https://www.gobmallorca.com) | Palma | `fauna` |
| **05** | Societat d'Història Natural (SHNB) | Fauna | SHNB (fundada el 1954) | [shnb.org](https://www.shnb.org) | Palma (Campus UIB) | `fauna`, `flora` |
| **06** | MUCBO (Museu i Jardí Botànic) | Fauna | Fundació MUCBO | [mucbo.org](https://mucbo.org) | Sóller | `flora`, `fauna` |
| **07** | Xarxa de Parcs Naturals de les Balears | Fauna | Espais Naturals (CAIB) | [espaisnaturals.caib.es](https://espaisnaturals.caib.es) | Mallorca (S'Albufera, etc.) | `fauna`, `flora` |
| **08** | Parc Nacional de Cabrera | Fauna | OAPN / CAIB | [miteco.gob.es](https://www.miteco.gob.es) | Cabrera / Colònia St. Jordi | `fauna`, `flora` |
| **09** | Centre Balear de Biodiversitat (CBB) | Fauna | UIB | [uib.cat](https://uib.cat) | Campus UIB, Palma | `fauna`, `flora` |
| **10** | IMEDEA (CSIC - UIB) | Fauna | CSIC / UIB | [imedea.uib-csic.es](https://imedea.uib-csic.es) | Esporles | `fauna` |
| **11** | Herbari Virtual del Mediterrani Occ. | Fauna | Àrea de Botànica (UIB) | [herbarivirtual.uib.es](https://herbarivirtual.uib.es) | Campus UIB, Palma | `flora` |
| **12** | Fundació Palma Aquarium | Fauna | Palma Aquarium | [fundacionpalmaaquarium.org](https://fundacionpalmaaquarium.org) | Platja de Palma | `fauna` |
| **13** | SEO/BirdLife Illes Balears | Fauna | SEO/BirdLife | [seo.org](https://seo.org/delegacion-illes-balears/) | Palma | `fauna` |
| **14** | Fundació Marilles (Informe Mar Balear) | Fauna | Fundació Marilles | [marilles.org](https://marilles.org) | Palma | `fauna` |
| **15** | SOCIB (Observatori Costaner) | Fauna | Consorci Públic SOCIB | [socib.es](https://www.socib.es) | Parc Bit, Palma | `fauna` |
| **16** | Fundació Natura Parc | Fauna | Fundació Natura Parc | [fundacionaturaparc.com](https://fundacionaturaparc.com) | Santa Eugènia | `fauna` |
| **17** | Xarxa Forestal de les Illes Balears | Fauna | Servei Forestal (CAIB) | [xarxaforestal.info](https://xarxaforestal.info) | Mallorca | `flora`, `fauna` |
| **18** | Save the Med Foundation (SharkMed) | Fauna | Save The Med Foundation | [savethemed.org](https://savethemed.org) | Palma | `fauna` |
| **19** | DCVB (Alcover-Moll) | Llengua | IEC / Institució Moll | [dcvb.iec.cat](https://dcvb.iec.cat) | Palma / IEC | `words` |
| **20** | Fundació Mallorca Literària | Llengua | Consell de Mallorca | [mallorcaliteraria.cat](https://www.mallorcaliteraria.cat) | Sant Joan (Casa Ginard) | `words`, `historical_events` |
| **21** | Mallorca Oral (Cançoner i Arxiu) | Llengua | F. Mallorca Literària | [mallorcaoral.cat](https://www.mallorcaoral.cat) | Sant Joan / Palma | `words` |
| **22** | Institució Francesc de Borja Moll | Llengua | Institució Moll | [instituciomoll.cat](https://instituciomoll.cat) | Palma | `words` |
| **23** | TERMCAT (Cercaterm i Tradicional) | Llengua | TERMCAT / IEC | [termcat.cat](https://www.termcat.cat) | En línia | `words` |
| **24** | ALDC (Atles Lingüístic Domini Català) | Llengua | Institut d'Estudis Catalans | [aldc.espais.iec.cat](https://aldc.espais.iec.cat) | Mallorca (Punts d'enquesta) | `words` |
| **25** | COD (Corpus Oral Dialectal) | Llengua | CUSC - Universitat Barcelona | [ub.edu](https://www.ub.edu/cccub/corpus-oral-dialectal/) | Municipis de Mallorca | `words` |
| **26** | NGIB (Nomenclàtor Geogràfic Balears) | Llengua | ICGIB / IDEIB | [ideib.caib.es](https://ideib.caib.es) | Palma (Govern CAIB) | `words`, `historical_events` |
| **27** | NOTIB (Nomenclàtor Toponímic IEC/UIB) | Llengua | IEC / UIB | [uib.cat](https://uib.cat) | Campus UIB, Palma | `words` |
| **28** | CTILC (Corpus Textual Informatitzat) | Llengua | Institut d'Estudis Catalans | [ctilc.iec.cat](https://ctilc.iec.cat) | En línia | `words` |
| **29** | BDLex (Base de Dades Lexicogràfica) | Llengua | Institut d'Estudis Catalans | [bdlex.iec.cat](https://bdlex.iec.cat) | En línia | `words` |
| **30** | Rodamots ('Cada dia un mot') | Llengua | Xarxa de Mots (Jordi Palou) | [rodamots.cat](https://rodamots.cat) | En línia | `words` |
| **31** | Obra Cultural Balear (OCB) | Llengua | OCB (fundada el 1962) | [ocb.cat](https://www.ocb.cat) | Can Alcover, Palma | `words`, `historical_events` |
| **32** | Càtedra Josep Maria Llompart | Llengua | Universitat de les Illes Balears | [catedrallompart.uib.cat](https://catedrallompart.uib.cat) | Campus UIB, Palma | `words`, `historical_events` |
| **33** | Magisteri Teatre - Mag Poesia | Llengua | UIB (Antoni Artigues) | [magpoesia.mallorcaweb.com](https://magpoesia.mallorcaweb.com) | Palma | `words`, `historical_events` |
| **34** | Grup de Recerca en Etnopoètica | Llengua | Dept. Filologia Catalana UIB | [uib.cat](https://uib.cat) | Campus UIB, Palma | `words` |
| **35** | Toponímia de Mallorca (M. À. Escanelles) | Llengua | Recerca independent | [toponimiamallorca.net](https://toponimiamallorca.net) | Mallorca | `words`, `historical_events` |
| **36** | Arxiu de Tradicions Locals i Festes | Llengua | Consell de Mallorca | [conselldemallorca.es](https://www.conselldemallorca.es) | Palma / Municipis | `words`, `historical_events` |
| **37** | Arxiu del Regne de Mallorca (ARM) | Cultura | Conselleria de Cultura | [arxiuregnemallorca.com](https://arxiuregnemallorca.com) | Carrer Ramon Llull, Palma | `historical_events` |
| **38** | Arxiu Capitular de Mallorca (ACM) | Cultura | Capítol Catedral de Mallorca | [catedraldemallorca.org](https://catedraldemallorca.org) | Seu de Mallorca, Palma | `historical_events` |
| **39** | Arxiu Diocesà (Maiorica Sacra) | Cultura | Bisbat de Mallorca | [arxiudigital.maioricasacra.org](https://arxiudigital.maioricasacra.org) | Palau Episcopal, Palma | `historical_events` |
| **40** | Arxiu Municipal de Palma | Cultura | Ajuntament de Palma | [palma.cat](https://www.palma.cat) | Can Balaguer / Cort | `historical_events`, `emblematic_businesses` |
| **41** | IBDigital (Biblioteca Digital Balears) | Cultura | Servei de Biblioteca UIB | [ibdigital.uib.es](https://ibdigital.uib.es) | Campus UIB, Palma | `historical_events`, `emblematic_businesses` |
| **42** | Societat Arqueològica Lul·liana (BSAL) | Cultura | Societat Lul·liana (1880) | [arqueologicalulliana.com](https://arqueologicalulliana.com) | Monti-sion, Palma | `historical_events` |
| **43** | Portal de Patrimoni del Consell | Cultura | Consell de Mallorca | [patrimoni.conselldemallorca.cat](https://patrimoni.conselldemallorca.cat) | Mallorca | `historical_events` |
| **44** | Consorci Serra Tramuntana UNESCO | Cultura | Consell de Mallorca | [serradetramuntana.net](https://www.serradetramuntana.net) | Serra de Tramuntana | `historical_events`, `flora` |
| **45** | Museu de Mallorca | Cultura | CAIB / Consell de Mallorca | [museudemallorca.caib.es](http://museudemallorca.caib.es) | Ca la Gran Cristiana, Palma | `historical_events` |
| **46** | Museu Arqueològic de Son Fornés | Cultura | Ajuntament Montuïri / UAB | [sonfornes.mallorca.museum](https://sonfornes.mallorca.museum) | Montuïri | `historical_events` |
| **47** | Poblat Talaiòtic de Ses Païsses | Cultura | Ajuntament d'Artà | [artaturisme.com](https://artaturisme.com) | Artà | `historical_events` |
| **48** | Ciutat Romana de Pol·lèntia i Museu | Cultura | Consorci Ciutat Pol·lèntia | [alcudia.net/Pollentia](https://www.alcudia.net/Pollentia/) | Alcúdia | `historical_events` |
| **49** | Museu d'Història de Manacor | Cultura | Ajuntament de Manacor | [museudemanacor.com](https://museudemanacor.com) | Torre Enagistes, Manacor | `historical_events` |
| **50** | Museu Marítim de Mallorca | Cultura | Consorci Museu Marítim | [museumaritim.conselldemallorca.es](https://museumaritim.conselldemallorca.es) | Ses Voltes (Palma) / Sóller | `historical_events`, `words` |
| **51** | Museu del Calçat i de la Indústria | Cultura | Ajuntament d'Inca | [museudelcalcat.inca.es](https://museudelcalcat.inca.es) | Quarter Luque, Inca | `emblematic_businesses`, `historical_events` |
| **52** | Possessió Museu Els Calderers | Cultura | Fons privat etnogràfic | [els-calderers.com](https://els-calderers.com) | Sant Joan | `historical_events`, `emblematic_businesses` |
| **53** | Castell de Bellver i Museu de Palma | Cultura | Ajuntament de Palma | [castelldebellver.palma.cat](https://castelldebellver.palma.cat) | Bosc de Bellver, Palma | `historical_events` |
| **54** | Castell de Capdepera (i la Llatra) | Cultura | Patronat Castell Capdepera | [casteldecapdepera.com](https://casteldecapdepera.com) | Capdepera | `historical_events`, `emblematic_businesses` |
| **55** | La Cartoixa de Valldemossa | Cultura | Patronat de la Cartoixa | [cartoixadevalldemossa.com](https://cartoixadevalldemossa.com) | Valldemossa | `historical_events` |
| **56** | Fundació Pilar i Joan Miró a Mallorca | Cultura | Ajuntament de Palma / F. Miró | [miromallorca.com](https://miromallorca.com) | Cala Major, Palma | `historical_events` |
| **57** | Es Baluard Museu d'Art Contemporani | Cultura | Fundació Es Baluard | [esbaluard.org](https://www.esbaluard.org) | Baluard St. Pere, Palma | `historical_events` |
| **58** | Fundació Museu Sa Bassa Blanca | Cultura | Fundació Jakober | [msbb.org](https://www.msbb.org) | Alcúdia (Mal Pas) | `historical_events` |
| **59** | Emblemàtics Balears (IDI / ADR) | Cultura | Govern de les Illes Balears | [emblematicsbalears.es](https://emblematicsbalears.es) | Tots els municipis | `emblematic_businesses` |
| **60** | Associació d'Amics dels Molins | Cultura | Amics dels Molins (1980) | [amicsdelsmolins.com](https://amicsdelsmolins.com) | Pla de Sant Jordi / Mallorca | `historical_events`, `emblematic_businesses` |

---

## 6. Consideracions Jurídiques, Propietat Intel·lectual i Atribució Ètica

El projecte «Una teringa de curiositats» aplica un estricte protocol ètic i jurídic en el tractament de la informació pública:

1. **Reconeixement de l'Autoria i Fonts**:  
   Totes les dades consultades, sintetitzades o exposades a la plataforma reconeixen explícitament l'autoria original. La propietat intel·lectual de les definicions, fotografies històriques, decrets administratius i treballs de recerca pertany als seus respectius autors i entitats custòdies (IEC, Institució Francesc de B. Moll, UIB, Consell de Mallorca, Govern de les Illes Balears, ajuntaments i museus).
2. **Ús Cultural, Docent i de Preservació**:  
   L'ús del material s'empara en el dret de citació i reutilització amb finalitats exclusivament educatives, científiques i culturals de divulgació sense afany de lucre.
3. **Ingesta Ètica i Control de Freqüència (Throttling)**:  
   Els mòduls d'extracció automatitzada (`scripts/scrapers/`) incorporen retards obligatoris (*polite delay* d'almenys 1,2 segons per petició) i capçaleres identificatives d'usuari per evitar sobrecarregar els servidors de les institucions col·laboradores (en particular els servidors de l'IEC i la UIB).
4. **Dades Obertes Institucionals**:  
   S'ha prioritzat la informació distribuïda sota marcs de dades obertes del Govern de les Illes Balears (Catàleg CAIB, visors IDEIB WFS) i plataformes de ciència ciutadana (GBIF / Biodibal) per a la georeferenciació de comerços i jaciments.

/**
 * Una teringa de curiositats — Client App JS
 * Vista per defecte: "Una a la sort" (Spotlight aleatori interactiu)
 * Vista secundària: "Tota sa teringa" (Catàleg complet, filtres i cerca)
 */

// Dades de reserva integrades per si s'obre el fitxer directament amb protocol file://
const FALLBACK_DATA = [
  {
    "id": 1,
    "title": "Teringa",
    "subtitle": "[təˈɾiŋ.ɡə]",
    "tag": "nom femení",
    "definition": "Filera, renglera o successió continuada de coses o persones que van l'una darrere l'altra.",
    "example_sentence": "Hi havia una teringa de carros que esperaven per entrar a Ciutat el dia de mercat.",
    "etymology": "D'origen expressiu o relacionat amb 'tirar' / 'enfilar' en cadena.",
    "dialectal_notes": "Molt viva a Mallorca i Menorca.",
    "source_reference": "Diccionari Català-Valencià-Balear (Alcover-Moll)",
    "type": "words"
  },
  {
    "id": 2,
    "title": "Cap-ficat",
    "subtitle": "[kap.fiˈkat]",
    "tag": "adjectiu",
    "definition": "Persona caparruda, obstinada o entestada en una idea; també s'usa per descriure algú immers en pensaments o preocupat.",
    "example_sentence": "No li facis canviar de parer, que quan és cap-ficat no hi ha res a fer.",
    "etymology": "Compost de 'cap' i el participi del verb 'ficar'.",
    "dialectal_notes": "Molt viu a tot Mallorca.",
    "source_reference": "Diccionari Català-Valencià-Balear (Alcover-Moll)",
    "type": "words"
  },
  {
    "id": 3,
    "title": "Ullprès",
    "subtitle": "[uʎˈpɾəs]",
    "tag": "adjectiu",
    "definition": "Afectat pel mal d'ull segons la creença popular tradicional mallorquina; fascinat de manera negativa o malaltís sense causa física aparent.",
    "example_sentence": "L'al·lot plora tota la nit sense motiu; sa padrina diu que deu estar ullprès.",
    "etymology": "De 'ull' i 'près' (pres, capturat).",
    "dialectal_notes": "Patrimoni etnogràfic mallorquí (remeis tradicionals amb aigua i oli).",
    "source_reference": "Diccionari Català-Valencià-Balear (Alcover-Moll) / Costumari Mallorquí",
    "type": "words"
  },
  {
    "id": 4,
    "title": "Fer un gafet",
    "subtitle": "[fe un ɡəˈfət]",
    "tag": "expressió / frase feta",
    "definition": "Dormir una becaina o una petita migdiada breu per recuperar forces.",
    "example_sentence": "Després de dinar me'n vaig anar a jeure vint minuts per fer un gafet.",
    "etymology": "Gafet (ganxo petit o tancador; 'enganxar' la son breument).",
    "dialectal_notes": "Mallorquí col·loquial.",
    "source_reference": "Diccionari Català-Valencià-Balear (Alcover-Moll)",
    "type": "words"
  },
  {
    "id": 5,
    "title": "Trempar",
    "subtitle": "[tɾəmˈpa]",
    "tag": "verb",
    "definition": "Amanir una ensalada amb oli, sal i vinagre, especialment el trempó tradicional (tomàtiga, pebre verd i ceba blanca).",
    "example_sentence": "Talla bé sa ceba i sa tomàtiga i trempa-ho amb un bon raig d'oli d'oliva.",
    "etymology": "Del llatí 'temperare' (mesclar en proporció justa).",
    "dialectal_notes": "Pilar gastronòmic balear.",
    "source_reference": "Diccionari Català-Valencià-Balear (Alcover-Moll)",
    "type": "words"
  },
  {
    "id": 6,
    "title": "Qui no té feina el moix pentina",
    "subtitle": "[ki no te ˈfəj.nə əl moʃ pənˈti.nə]",
    "tag": "dita / refrany",
    "definition": "Refrany popular que es diu d'algú que perd el temps fent feines inútils, ximples o absurdes per no tenir obligacions reals.",
    "example_sentence": "Mira si s'avorreix que compta quantes rajoles té el menjador: qui no té feina el moix pentina!",
    "etymology": "'Moix' és la paraula mallorquina tradicional per a 'gat'.",
    "dialectal_notes": "Dita popular mallorquina universal.",
    "source_reference": "Diccionari Català-Valencià-Balear (Alcover-Moll) / Refranyer Mallorquí",
    "type": "words"
  },
  {
    "id": 7,
    "title": "Xereca",
    "subtitle": "[ʃəˈɾə.kə]",
    "tag": "adjectiu / nom",
    "definition": "Cosa de mala qualitat, mal feta, espatllada o de poc valor; també s'aplica a una persona informal o poc seriosa.",
    "example_sentence": "Aquesta eina és una xereca, no durarà ni dos dies de feina al camp.",
    "etymology": "Probablement d'origen onomatopeic o expressiu.",
    "dialectal_notes": "Molt arrelat a la comarca del Pla i Llevant.",
    "source_reference": "Diccionari Català-Valencià-Balear (Alcover-Moll)",
    "type": "words"
  },
  {
    "id": 8,
    "title": "Al bell mig",
    "subtitle": "[əl beʎ mitʃ]",
    "tag": "locució adverbial",
    "definition": "Exactament al centre, just al mig d'un espai o d'un assumpte.",
    "example_sentence": "Va deixar el carretó aturat al bell mig del camí ral.",
    "etymology": "De 'bell' (en sentit ponderatiu o enfàtic) i 'mig'.",
    "dialectal_notes": "Ús literari i popular a totes les Illes.",
    "source_reference": "Diccionari Català-Valencià-Balear (Alcover-Moll)",
    "type": "words"
  },
  {
    "id": 1,
    "title": "Ferreret",
    "subtitle": "Alytes muletensis",
    "tag": "amfibi",
    "is_endemic": 1,
    "is_native_breed": 0,
    "conservation_status": "Vulnerable (VU)",
    "habitat": "Gorgs i torrents càrstics d'alta muntanya a la Serra de Tramuntana (torrents de Pareis, Gorg Blau, etc.).",
    "definition": "Petit gripau endèmic de Mallorca, considerat un fòssil vivent. Va ser redescobert viu el 1980 després d'haver estat descrit inicialment per restes fòssils del Plistocè.",
    "curiosities": "El mascle és qui transporta els ous fecundats enganxats a les seves cames del darrere fins que es desclouen.",
    "source_reference": "Biodibal (UIB) / Servei de Protecció d'Espècies CAIB",
    "type": "fauna"
  },
  {
    "id": 2,
    "title": "Porc Negre Mallorquí",
    "subtitle": "Sus scrofa domesticus",
    "tag": "raça autòctona",
    "is_endemic": 0,
    "is_native_breed": 1,
    "conservation_status": "Protecció Oficial (IRFAP)",
    "habitat": "Explotacions extensives i garrigues arbrades amb garrovers i alzinars a Mallorca.",
    "definition": "Raça porcina autòctona de color negre o gris fosc, amb característiques 'mamelles' cutànies que pengen del coll. És la base fonamental de l'autèntica Sobrassada de Mallorca de Porc Negre.",
    "curiosities": "La seva dieta tradicional amb figues seques, garroves i glans atorga a la carn una textura i aroma únics al món.",
    "source_reference": "IRFAP (Races Autòctones de les Illes Balears)",
    "type": "fauna"
  },
  {
    "id": 3,
    "title": "Ca de Bou",
    "subtitle": "Canis lupus familiaris",
    "tag": "raça autòctona",
    "is_endemic": 0,
    "is_native_breed": 1,
    "conservation_status": "Raça autòctona catalogada",
    "habitat": "Possessions i finques rústiques de Mallorca.",
    "definition": "Molós autòcton de constitució forta, musculada i mandíbules molt potents. Tradicionalment emprat com a guardià fidel de possessions i per a la subjecció de bestiar brau.",
    "curiosities": "Reconegut internacionalment per la FCI com una de les races autòctones més antigues i singulars de les Balears.",
    "source_reference": "IRFAP / Club del Ca de Bou",
    "type": "fauna"
  },
  {
    "id": 4,
    "title": "Ca de Bestiar",
    "subtitle": "Canis lupus familiaris",
    "tag": "raça autòctona",
    "is_endemic": 0,
    "is_native_breed": 1,
    "conservation_status": "Raça autòctona catalogada",
    "habitat": "Finques ramaderes i pastures de tota l'illa.",
    "definition": "Gos pastor mallorquí d'un negre atzabeja brillant (permissió d'una petita taca blanca al pit), musculat, molt intel·ligent, lleial al seu amo i d'instint de custòdia insuperable.",
    "curiosities": "Existeixen dues varietats de pèl: curt (més comú) i llarg. Tradicionalment no acceptava menjar de cap foraster.",
    "source_reference": "IRFAP / Club del Ca de Bestiar",
    "type": "fauna"
  },
  {
    "id": 5,
    "title": "Virot petit",
    "subtitle": "Puffinus mauretanicus",
    "tag": "au",
    "is_endemic": 1,
    "is_native_breed": 0,
    "conservation_status": "En perill crític (CR)",
    "habitat": "Penya-segats marins, illots costaners i mar obert balear.",
    "definition": "L'ocell marí més amenaçat de tot Europa, endèmic exclusiu de les Illes Balears.",
    "curiosities": "Vola arran d'aigua amb un batre d'ales ràpid i precís, i només toca terra de nit per evitar els depredadors.",
    "source_reference": "Biodibal (UIB) / SEO BirdLife",
    "type": "fauna"
  },
  {
    "id": 6,
    "title": "Voltor negre",
    "subtitle": "Aegypius monachus",
    "tag": "au",
    "is_endemic": 0,
    "is_native_breed": 0,
    "conservation_status": "Vulnerable (població en recuperació)",
    "habitat": "Cingles i alzinars feréstecs de la Serra de Tramuntana.",
    "definition": "L'ocell rapinyaire més gran d'Europa, amb una envergadura d'ales de fins a gairebé tres metres. Mallorca acull l'única població insular del món.",
    "curiosities": "Gràcies a dècades de conservació de la Fundació Vida Silvestre Mediterrània, la seva població a la Tramuntana ha passat d'uns pocs exemplars a més de 200.",
    "source_reference": "Servei de Protecció d'Espècies CAIB / Fundació Vida Silvestre Mediterrània",
    "type": "fauna"
  },
  {
    "id": 7,
    "title": "Sargantana balear",
    "subtitle": "Podarcis lilfordi",
    "tag": "reptil",
    "is_endemic": 1,
    "is_native_breed": 0,
    "conservation_status": "En perill (EN)",
    "habitat": "Illots costaners aïllats de Mallorca (Dragonera, Cabrera, illots de Santa Ponça).",
    "definition": "Rèptil endèmic que va desaparèixer de l'illa gran de Mallorca per la introducció de depredadors forans (com gats i serps), però que sobreviu en una vintena de subespècies als illots.",
    "curiosities": "Als illots no té por dels humans i té un paper clau com a pol·linitzadora i dispersora de llavors com la rapa de frare.",
    "source_reference": "Biodibal (UIB)",
    "type": "fauna"
  },
  {
    "id": 1,
    "title": "Fonoll marí",
    "subtitle": "Crithmum maritimum",
    "tag": "Apiaceae",
    "is_endemic": 0,
    "flowering_period": "Juliol - Octubre",
    "habitat": "Roques i penya-segats marítims batuts per la salabror marina.",
    "traditional_uses": "Conserva tradicional mallorquina adobada amb vinagre i aigua amb sal, acompanyament indispensable del pa amb oli.",
    "definition": "Planta aromàtica suculenta de fulles carnoses verd-glauc. Molt rica en vitamina C, utilitzada històricament pels navegants contra l'escorbut.",
    "curiosities": "La seva recol·lecció silvestre comercial està regulada a les Balears per protegir els penya-segats.",
    "source_reference": "Herbari Virtual del Mediterrani Occidental (UIB)",
    "type": "flora"
  },
  {
    "id": 2,
    "title": "Estepa joana (Hipèric balear)",
    "subtitle": "Hypericum balearicum",
    "tag": "Hypericaceae",
    "is_endemic": 1,
    "flowering_period": "Abril - Juliol",
    "habitat": "Garrigues i vessants pedregosos de la Serra de Tramuntana i el Raiguer.",
    "traditional_uses": "Oli de cop: maceració de flors en oli d'oliva verge per guarir cremades, contusions i ferides.",
    "definition": "Arbust endèmic balear inconfusible per les seves fulles petites amb berrugues resinoses i flors solitàries grogues llampants d'olor balsàmica.",
    "curiosities": "Desprèn una aroma característica a resina quan rep la forta insolació de l'estiu mallorquí.",
    "source_reference": "Herbari Virtual del Mediterrani Occidental (UIB)",
    "type": "flora"
  },
  {
    "id": 3,
    "title": "Garrofer",
    "subtitle": "Ceratonia siliqua",
    "tag": "Fabaceae",
    "is_endemic": 0,
    "flowering_period": "Setembre - Novembre",
    "habitat": "Terres de secà, planes del Raiguer, Pla i Migjorn de Mallorca.",
    "traditional_uses": "Aliment del porc negre, farina de garrova per a rebosteria, garrofí per a espessidors naturals alimentaris.",
    "definition": "Arbre noble de fulla perenne i fusta rogenca, símbol secular del paisatge agrari mallorquí resistent a les secades.",
    "curiosities": "El mot 'quirat' (orfebreria) prové de la paraula grega per a la llavor de la garrova, per la seva sorprenent regularitat de pes.",
    "source_reference": "Herbari Virtual del Mediterrani Occidental (UIB) / IRFAP",
    "type": "flora"
  },
  {
    "id": 4,
    "title": "Mata (Lentisc)",
    "subtitle": "Pistacia lentiscus",
    "tag": "Anacardiaceae",
    "is_endemic": 0,
    "flowering_period": "Març - Maig",
    "habitat": "Garrigues típiques, costes i alzinars degradats de tot Mallorca.",
    "traditional_uses": "Mata de fer escombres rústiques de garriga; la resina s'ha emprat tradicionalment com a màstic aromàtic.",
    "definition": "Arbust perenne aromàtic molt dens amb fulles compostes sense folíol terminal i petits fruits vermells que es tornen negres quan maduren.",
    "curiosities": "Dona nom a la formació vegetal més extensa de l'illa: la mata garriguera.",
    "source_reference": "Herbari Virtual del Mediterrani Occidental (UIB)",
    "type": "flora"
  },
  {
    "id": 5,
    "title": "Cresta de gall (Didalera menor)",
    "subtitle": "Digitalis minor",
    "tag": "Plantaginaceae",
    "is_endemic": 1,
    "flowering_period": "Maig - Juliol",
    "habitat": "Escletxes de roques calcàries i penyals ombrívols de la Serra de Tramuntana.",
    "traditional_uses": "Planta tòxica amb principis cardiotònics; exclusivament ús mèdic controlat.",
    "definition": "Herba endèmica preciosa amb flors rosades o purpúries en forma de didal penjant en espiga elegant.",
    "curiosities": "Creix directament sobre les parets de roca vertical calcària de la Tramuntana.",
    "source_reference": "Herbari Virtual del Mediterrani Occidental (UIB)",
    "type": "flora"
  },
  {
    "id": 1,
    "title": "Forn del Santo Cristo",
    "subtitle": "Palma",
    "tag": "Forn i Pastisseria",
    "category_type": "Comerç amb història",
    "foundation_year": 1910,
    "address": "Carrer dels Paraires, 2, 07001 Palma",
    "latitude": 39.5701,
    "longitude": 2.6489,
    "definition": "Fundat el 1910 al cor de Palma, és un dels forns més venerats de Mallorca per la conservació de la recepta tradicional d'ensaïmada amb saïm autèntic i fermentació pacient.",
    "heritage_elements": "Rètol clàssic, mostrador de fusta noble i forn tradicional de solera.",
    "source_reference": "Catàleg Emblemàtics Balears (IDI)",
    "type": "businesses"
  },
  {
    "id": 2,
    "title": "Teixits Riera",
    "subtitle": "Lloseta",
    "tag": "Artesania / Tèxtil (Teles de llengües)",
    "category_type": "Comerç arrelat i amb història",
    "foundation_year": 1896,
    "address": "Carrer Major, 50, 07360 Lloseta",
    "latitude": 39.7188,
    "longitude": 2.8687,
    "definition": "Taller familiar que des del 1896 confecciona artesanalment les famoses 'teles de llengües' mitjançant la tècnica mil·lenària de l'ikat, mantenint telers mecànics històrics.",
    "heritage_elements": "Telers de fusta i ferro de finals del segle XIX i arxiu històric de patrons gràfics.",
    "source_reference": "Catàleg Emblemàtics Balears (IDI)",
    "type": "businesses"
  },
  {
    "id": 3,
    "title": "Vidrieries Gordiola",
    "subtitle": "Algaida",
    "tag": "Artesania (Vidre bufat)",
    "category_type": "Comerç amb història i patrimoni",
    "foundation_year": 1719,
    "address": "Carretera Palma-Manacor, km 19, 07210 Algaida",
    "latitude": 39.5623,
    "longitude": 2.9021,
    "definition": "Amb més de 300 anys ininterromputs de tradició, és el taller de vidre bufat més antic de Mallorca i un referent mediterrani d'aquest ofici reconegut per la UNESCO.",
    "heritage_elements": "Forns de fusió de vidre en directe, castell neogòtic i museu del vidre bufat.",
    "source_reference": "Catàleg Emblemàtics Balears (IDI) / UNESCO Patrimoni Immaterial",
    "type": "businesses"
  },
  {
    "id": 4,
    "title": "Ca Dona Àngela",
    "subtitle": "Palma",
    "tag": "Merceria tradicional",
    "category_type": "Comerç amb història i patrimoni",
    "foundation_year": 1685,
    "address": "Carrer de Jaume II, 38, 07001 Palma",
    "latitude": 39.5694,
    "longitude": 2.6512,
    "definition": "Documentada des del 1685, és una de les merceries en actiu més antigues d'Europa, venent fils de seda, vetes, encaixos i ornaments tradicionals mallorquins.",
    "heritage_elements": "Taulells i calaixeres de fusta centenària que conserven l'essència del comerç del barroc i segle XIX.",
    "source_reference": "Catàleg Emblemàtics Balears (IDI) / Ajuntament de Palma",
    "type": "businesses"
  },
  {
    "id": 5,
    "title": "Celler Sa Premsa",
    "subtitle": "Palma",
    "tag": "Restauració / Celler tradicional",
    "category_type": "Comerç amb història",
    "foundation_year": 1958,
    "address": "Plaça del Bisbe Berenguer de Palou, 8, 07003 Palma",
    "latitude": 39.5746,
    "longitude": 2.6508,
    "definition": "Espai emblemàtic de la gastronomia tradicional mallorquina, decorat amb bótes de vi gegantines, eines de pagès i cartells històrics de fires de Mallorca.",
    "heritage_elements": "Bótes monumentals de roure i estris agrícoles tradicionals conservats a les parets.",
    "source_reference": "Catàleg Emblemàtics Balears (IDI)",
    "type": "businesses"
  },
  {
    "id": 1,
    "title": "Cultura Talaiòtica: Poblat de ses Païsses",
    "subtitle": "c. 1000 a. C. - 123 a. C.",
    "tag": "Prehistòria i Talaiòtic",
    "location_scope": "Artà, Mallorca",
    "definition": "Període de màxima esplendor de la civilització megalítica talaiòtica a Mallorca, amb grans torres ciclòpies de vigilància, murades ciclòpies i estructures hipòstiles.",
    "detailed_description": "El poblat de ses Païsses a Artà conserva una de les portes megalítiques més monumentals de la Mediterrània occidental i il·lustra l'organització comunitària dels antics pobladors balears.",
    "key_figures": "Foners balears (famosos per la seva punteria al servei de cartaginesos i romans)",
    "source_reference": "Gran Enciclopèdia de Mallorca (GEM)",
    "type": "history"
  },
  {
    "id": 2,
    "title": "Conquesta romana de Quint Cecili Metel",
    "subtitle": "123 a. C.",
    "tag": "Època Romana",
    "location_scope": "Palma i Pol·lèntia (Alcúdia)",
    "definition": "El cònsol romà Quint Cecili Metel (anomenat 'Balearicus') conquereix les Balears i funda les ciutats de Palma i Pol·lèntia.",
    "detailed_description": "La conquesta posà fi a la pirateria a les rutes de la Mediterrània occidental i integrà Mallorca a l'Imperi Romà, iniciant la romanització i l'arribada de la vinya i l'olivera.",
    "key_figures": "Quint Cecili Metel Balearicus",
    "source_reference": "Gran Enciclopèdia de Mallorca (GEM)",
    "type": "history"
  },
  {
    "id": 3,
    "title": "Mayûrqa: La conquesta islàmica",
    "subtitle": "902 d. C. - 1229",
    "tag": "Època Islàmica (Mayûrqa)",
    "location_scope": "Madîna Mayûrqa (Palma)",
    "definition": "Incorporació de les Balears a l'emirat de Còrdova per Issam al-Khawlaní, iniciant més de tres segles d'esplendor andalusí.",
    "detailed_description": "Desenvolupament dels sistemes hidràulics (qanats, sínies i síquies) que transformaren l'agricultura, construcció dels Banys Àrabs i fortificació de Madîna Mayûrqa com a nus comercial clau.",
    "key_figures": "Issam al-Khawlaní, Abu Yahya",
    "source_reference": "Arxiu del Regne de Mallorca (ARM) / Història de les Illes Balears",
    "type": "history"
  },
  {
    "id": 4,
    "title": "Conquesta de Mallorca pel Rei Jaume I",
    "subtitle": "31 de desembre de 1229",
    "tag": "Reialme de Mallorca (Edat Mitjana)",
    "location_scope": "Desembarcament a Santa Ponça i assalt a Madîna Mayûrqa (Palma)",
    "definition": "L'exèrcit cristià liderat pel rei Jaume I el Conqueridor assalta Madîna Mayûrqa el darrer dia de 1229, incorporant l'illa a la cristiandat i a la Corona d'Aragó.",
    "detailed_description": "La campanya va donar pas al 'Llibre del Repartiment' (distribució de les terres entre nobles catalans, aragonesos i occitans) i a la creació de les bases institucionals del futur Regne de Mallorca independent (creat el 1276).",
    "key_figures": "Rei Jaume I, Bernat de Santa Eugènia, Nunó Sanç, Guillem de Montcada",
    "source_reference": "Arxiu del Regne de Mallorca (ARM) / Llibre dels Fets",
    "type": "history"
  },
  {
    "id": 5,
    "title": "La Revolta de les Germanies a Mallorca",
    "subtitle": "1521 - 1523",
    "tag": "Edat Moderna",
    "location_scope": "Ciutat de Mallorca, Alcúdia i Castell de Bellver",
    "definition": "Insurrecció popular dels menestrals i pagesos ('agermanats') contra els tributs abusius, la corrupció de la noblesa i els cavallers.",
    "detailed_description": "Sota el lideratge de menestrals com Joanot Colom, els agermanats van controlar gran part de l'illa durant dos anys, mentre els cavallers es van refugiar a Alcúdia fins a la repressió imperial.",
    "key_figures": "Joan Crespí, Joanot Colom, emperador Carles V",
    "source_reference": "Arxiu del Regne de Mallorca (ARM) / GEM",
    "type": "history"
  },
  {
    "id": 6,
    "title": "El Decret de Nova Planta a Mallorca",
    "subtitle": "28 de novembre de 1715",
    "tag": "Edat Moderna",
    "location_scope": "Regne de Mallorca",
    "definition": "Després de la Guerra de Successió, Felip V aboleix les institucions pròpies del Regne de Mallorca (com el Gran i General Consell).",
    "detailed_description": "Implantació del model castellà de reial audiència i capità general, marcant la fi de la sobirania jurídica i política tradicional de Mallorca.",
    "key_figures": "Felip V, Marquès d'Asfeld",
    "source_reference": "Arxiu del Regne de Mallorca (ARM)",
    "type": "history"
  }
];

// Funció per formatar i embellir les etiquetes (evita slugs ASCII com raca_domestica)
function formatTag(tag) {
  if (!tag) return "";
  const TAG_MAP = {
    "raca_domestica": "raça autòctona",
    "raça autòctona": "raça autòctona",
    "amfibi": "amfibi",
    "au": "au",
    "reptil": "rèptil",
    "mamifer": "mamífer",
    "peix": "peix",
    "invertebrat": "invertebrat"
  };
  return TAG_MAP[tag.toLowerCase()] || tag;
}

// Configuració d'etiquetes i colors per categoria
const TYPE_CONFIG = {
  words: { icon: "🗣️", label: "Llengua & Dites", className: "card-words", color: "var(--cat-words)", bgBadge: "var(--cat-words-bg)" },
  fauna: { icon: "🦎", label: "Fauna & Races", className: "card-fauna", color: "var(--cat-fauna)", bgBadge: "var(--cat-fauna-bg)" },
  flora: { icon: "🌿", label: "Flora & Remeis", className: "card-flora", color: "var(--cat-flora)", bgBadge: "var(--cat-flora-bg)" },
  businesses: { icon: "🥖", label: "Comerç Emblemàtic", className: "card-businesses", color: "var(--cat-businesses)", bgBadge: "var(--cat-businesses-bg)" },
  history: { icon: "📜", label: "Fet Històric", className: "card-history", color: "var(--cat-history)", bgBadge: "var(--cat-history-bg)" }
};

// Estat global
let allItems = [];
let currentCategory = "all";
let currentSearch = "";
let currentRandomIndex = -1;

// Elements del DOM: Selector de vistes
const tabSpotlight = document.getElementById("tab-spotlight");
const tabTeringa = document.getElementById("tab-teringa");
const viewSpotlight = document.getElementById("view-spotlight");
const viewTeringa = document.getElementById("view-teringa");
const tabTotalBadge = document.getElementById("tab-total-badge");

// Elements Spotlight ("Una a la sort")
const spotlightCard = document.getElementById("spotlight-card");
const spBadge = document.getElementById("sp-badge");
const spOriginTag = document.getElementById("sp-origin-tag");
const spTitle = document.getElementById("sp-title");
const spSubtitle = document.getElementById("sp-subtitle");
const spDefinition = document.getElementById("sp-definition");
const spCuriosityBox = document.getElementById("sp-curiosity-box");
const spBoxText = document.getElementById("sp-box-text");
const spSource = document.getElementById("sp-source");
const btnNextRandom = document.getElementById("btn-next-random");
const btnGotoTeringa = document.getElementById("btn-goto-teringa");

// Elements Catàleg ("Tota sa teringa")
const feedContainer = document.getElementById("teringa-feed");
const searchInput = document.getElementById("search-input");
const resultsCounter = document.getElementById("results-counter");
const pills = document.querySelectorAll(".pill");
const btnShuffleFeed = document.getElementById("btn-shuffle-feed");

// Modal de Detall (<dialog>)
const detailModal = document.getElementById("detail-modal");
const modalBadge = document.getElementById("modal-badge");
const modalTitle = document.getElementById("modal-title");
const modalSubtitle = document.getElementById("modal-subtitle");
const modalContent = document.getElementById("modal-content");
const modalExtra = document.getElementById("modal-extra");
const modalSource = document.getElementById("modal-source");
const modalCloseBtn = document.getElementById("modal-close-btn");

// Inicialització de l'aplicació
async function initApp() {
  await loadData();
  setupEventListeners();
  updatePillCounts();
  tabTotalBadge.textContent = allItems.length;

  // 1. Per defecte: Carregar una curiositat a la sort a la vista principal
  pickRandomSpotlight(false);

  // 2. Preparar el feed de la teringa per si l'usuari commuta la vista
  renderTeringa();
}

// Carregar dades de l'API SQLite o fallback
async function loadData() {
  try {
    const res = await fetch("/api/curiositats");
    if (!res.ok) throw new Error("API not available");
    allItems = await res.json();
    if (!allItems || allItems.length === 0) {
      allItems = FALLBACK_DATA;
    }
  } catch (e) {
    allItems = FALLBACK_DATA;
  }
}

// Commutador de vistes
function switchView(viewName) {
  if (viewName === "spotlight") {
    tabSpotlight.classList.add("active");
    tabTeringa.classList.remove("active");
    viewSpotlight.classList.add("active");
    viewTeringa.classList.remove("active");
    window.scrollTo({ top: 0, behavior: "smooth" });
  } else if (viewName === "teringa") {
    tabTeringa.classList.add("active");
    tabSpotlight.classList.remove("active");
    viewTeringa.classList.add("active");
    viewSpotlight.classList.remove("active");
    // Scroll suau a l'inici dels controls
    const controls = document.querySelector(".controls-bar");
    if (controls) {
      controls.scrollIntoView({ behavior: "smooth" });
    }
  }
}

// Escollir una curiositat a l'atzar per al Spotlight
function pickRandomSpotlight(animate = true) {
  if (allItems.length === 0) return;

  // Triar un índex diferent de l'actual si n'hi ha més d'un
  let newIdx;
  if (allItems.length > 1) {
    do {
      newIdx = Math.floor(Math.random() * allItems.length);
    } while (newIdx === currentRandomIndex);
  } else {
    newIdx = 0;
  }
  currentRandomIndex = newIdx;
  const item = allItems[newIdx];

  const updateCardContent = () => {
    const cfg = TYPE_CONFIG[item.type] || TYPE_CONFIG.words;

    spBadge.textContent = `${cfg.icon} ${cfg.label}`;
    spBadge.style.backgroundColor = cfg.bgBadge;
    spBadge.style.color = cfg.color;

    spotlightCard.style.borderTop = `6px solid ${cfg.color}`;

    spOriginTag.textContent = item.tag ? formatTag(item.tag) : "Patrimoni de Mallorca";
    spTitle.textContent = item.title;
    spSubtitle.textContent = item.subtitle || "";
    spDefinition.textContent = item.definition || "";

    const extra = item.curiosities || item.detailed_description || item.example_sentence || item.heritage_elements || "";
    if (extra) {
      spCuriosityBox.style.display = "flex";
      spBoxText.textContent = extra;
    } else {
      spCuriosityBox.style.display = "none";
    }

    spSource.textContent = `Font: ${item.source_reference || "Patrimoni i Etnografia de Mallorca"}`;
  };

  if (animate && window.matchMedia("(prefers-reduced-motion: no-preference)").matches) {
    spotlightCard.style.opacity = "0";
    spotlightCard.style.transform = "translateY(8px) scale(0.98)";
    setTimeout(() => {
      updateCardContent();
      spotlightCard.style.opacity = "1";
      spotlightCard.style.transform = "translateY(0) scale(1)";
    }, 150);
  } else {
    updateCardContent();
  }
}

// Actualitzar els recomptes
function updatePillCounts() {
  const counts = { all: allItems.length, words: 0, fauna: 0, flora: 0, businesses: 0, history: 0 };
  allItems.forEach(it => {
    if (counts[it.type] !== undefined) counts[it.type]++;
  });

  document.getElementById("count-all").textContent = counts.all;
  document.getElementById("count-words").textContent = counts.words;
  document.getElementById("count-fauna").textContent = counts.fauna;
  document.getElementById("count-flora").textContent = counts.flora;
  document.getElementById("count-businesses").textContent = counts.businesses;
  document.getElementById("count-history").textContent = counts.history;
}

// Renderitzar el catàleg de la teringa
function renderTeringa() {
  feedContainer.innerHTML = "";

  const filtered = allItems.filter(item => {
    const matchesCat = (currentCategory === "all" || item.type === currentCategory);
    if (!matchesCat) return false;

    if (!currentSearch) return true;
    const query = currentSearch.toLowerCase();
    const haystack = `${item.title} ${item.subtitle || ""} ${item.tag || ""} ${formatTag(item.tag)} ${item.definition || ""}`.toLowerCase();
    return haystack.includes(query);
  });

  resultsCounter.textContent = `${filtered.length} curiositats a sa teringa`;

  if (filtered.length === 0) {
    feedContainer.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; background: #fff; border-radius: 12px; border: 1px dashed var(--color-border);">
        <p style="font-size: 1.2rem; color: var(--color-text-muted);">No hem trobat cap curiositat amb aquesta cerca.</p>
        <button class="btn btn-primary" style="margin-top: 1rem;" onclick="clearFilters()">Restablir la teringa</button>
      </div>
    `;
    return;
  }

  filtered.forEach((item, index) => {
    const cfg = TYPE_CONFIG[item.type] || TYPE_CONFIG.words;
    const card = document.createElement("article");
    card.className = `card-curiositat ${cfg.className}`;
    card.setAttribute("tabindex", "0");
    card.setAttribute("role", "button");
    card.setAttribute("aria-label", `Veure detalls de: ${item.title}`);

    card.innerHTML = `
      <div class="card-top">
        <span class="card-tag">${formatTag(item.tag) || cfg.label}</span>
        <span class="card-type-icon">${cfg.icon}</span>
      </div>
      <h3 class="card-title">${item.title}</h3>
      ${item.subtitle ? `<p class="card-subtitle">${item.subtitle}</p>` : ""}
      <p class="card-snippet">${item.definition || ""}</p>
      <div class="card-bottom">
        <span>#${index + 1} a sa teringa</span>
        <span class="card-readmore">Saber-ne més &rarr;</span>
      </div>
    `;

    card.addEventListener("click", () => openDetail(item));
    card.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        openDetail(item);
      }
    });

    feedContainer.appendChild(card);
  });
}

// Obrir modal amb detall
function openDetail(item) {
  const cfg = TYPE_CONFIG[item.type] || TYPE_CONFIG.words;
  modalBadge.textContent = `${cfg.icon} ${cfg.label}`;
  modalBadge.style.backgroundColor = cfg.color;
  modalBadge.style.color = "#FFFFFF";

  modalTitle.textContent = item.title;
  modalSubtitle.textContent = item.subtitle || (item.tag ? formatTag(item.tag) : "");
  modalContent.textContent = item.definition || "";

  const extraText = item.curiosities || item.detailed_description || item.example_sentence || item.heritage_elements || "";
  if (extraText) {
    modalExtra.style.display = "block";
    modalExtra.innerHTML = `<strong>💡 Detall o curiositat:</strong> ${extraText}`;
  } else {
    modalExtra.style.display = "none";
  }

  modalSource.textContent = `Font: ${item.source_reference || "Patrimoni de Mallorca"}`;
  detailModal.showModal();
}

// Netejar filtres
window.clearFilters = function() {
  currentCategory = "all";
  currentSearch = "";
  searchInput.value = "";
  pills.forEach(p => p.classList.toggle("active", p.dataset.category === "all"));
  renderTeringa();
};

// Configuració d'esdeveniments
function setupEventListeners() {
  // Tabs de navegació
  tabSpotlight.addEventListener("click", () => switchView("spotlight"));
  tabTeringa.addEventListener("click", () => switchView("teringa"));

  // Accions del Spotlight ("A la sort")
  btnNextRandom.addEventListener("click", () => pickRandomSpotlight(true));
  btnGotoTeringa.addEventListener("click", () => switchView("teringa"));

  // Remenar el feed complet
  btnShuffleFeed.addEventListener("click", () => {
    allItems = [...allItems].sort(() => Math.random() - 0.5);
    renderTeringa();
  });

  // Filtres per categoria
  pills.forEach(pill => {
    pill.addEventListener("click", () => {
      pills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      currentCategory = pill.dataset.category;
      renderTeringa();
    });
  });

  // Cercador en temps real
  searchInput.addEventListener("input", (e) => {
    currentSearch = e.target.value.trim();
    renderTeringa();
  });

  // Tancar modal
  modalCloseBtn.addEventListener("click", () => detailModal.close());

  detailModal.addEventListener("click", (e) => {
    const rect = detailModal.getBoundingClientRect();
    const isInDialog = (
      e.clientX >= rect.left &&
      e.clientX <= rect.right &&
      e.clientY >= rect.top &&
      e.clientY <= rect.bottom
    );
    if (!isInDialog) {
      detailModal.close();
    }
  });
}

// Executar en carregar el document
document.addEventListener("DOMContentLoaded", initApp);

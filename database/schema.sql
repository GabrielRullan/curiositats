-- =====================================================================
-- BBDD: Una teringa de curiositats (Mallorca)
-- Esquema Relacional (Compatible amb SQLite i PostgreSQL)
-- =====================================================================

DROP TABLE IF EXISTS words;
DROP TABLE IF EXISTS fauna;
DROP TABLE IF EXISTS flora;
DROP TABLE IF EXISTS emblematic_businesses;
DROP TABLE IF EXISTS historical_events;

-- 1. TAULA: PARAULES, EXPRESSIONS I DITES
CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term VARCHAR(150) NOT NULL UNIQUE,
    ipa_pronunciation VARCHAR(100),
    grammatical_category VARCHAR(50), -- p. ex: 'nom masculí', 'adjectiu', 'verb', 'expressió', 'frase feta', 'dita'
    definition TEXT NOT NULL,
    example_sentence TEXT,
    etymology TEXT,
    dialectal_notes VARCHAR(150),     -- p. ex: 'Pla de Mallorca', 'Sóller', 'Mallorquí general', 'Raiguer'
    source_reference VARCHAR(255) DEFAULT 'Diccionari Català-Valencià-Balear (Alcover-Moll)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_words_term ON words(term);
CREATE INDEX IF NOT EXISTS idx_words_category ON words(grammatical_category);

-- 2. TAULA: FAUNA (ANIMALS I RACES AUTÒCTONES)
CREATE TABLE IF NOT EXISTS fauna (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    common_name_ca VARCHAR(150) NOT NULL UNIQUE,
    scientific_name VARCHAR(150),
    group_type VARCHAR(50) NOT NULL,  -- 'amfibi', 'reptil', 'au', 'mamifer', 'invertebrat', 'peix', 'raça autòctona'
    is_endemic BOOLEAN DEFAULT 0,
    is_native_breed BOOLEAN DEFAULT 0, -- Raça autòctona reconeguda per IRFAP
    conservation_status VARCHAR(50),  -- 'Preocupació Menor (LC)', 'Vulnerable (VU)', 'En perill (EN)', 'En perill crític (CR)'
    habitat TEXT,
    description TEXT NOT NULL,
    curiosities TEXT,
    image_url TEXT,
    source_reference VARCHAR(255) DEFAULT 'Biodibal (UIB) / IRFAP',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fauna_name ON fauna(common_name_ca);
CREATE INDEX IF NOT EXISTS idx_fauna_group ON fauna(group_type);

-- 3. TAULA: FLORA (PLANTES I ETNOBOTÀNICA)
CREATE TABLE IF NOT EXISTS flora (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    common_name_ca VARCHAR(150) NOT NULL UNIQUE,
    scientific_name VARCHAR(150) NOT NULL UNIQUE,
    family VARCHAR(100),
    is_endemic BOOLEAN DEFAULT 0,
    flowering_period VARCHAR(100),    -- p. ex: 'Primavera', 'Maig - Setembre'
    habitat TEXT,                     -- p. ex: 'Roquissars costaners', 'Alzinars de Tramuntana', 'Garriga'
    traditional_uses TEXT,            -- Usos medicinals, culinaris, ramaders o artesanals
    description TEXT NOT NULL,
    curiosities TEXT,
    image_url TEXT,
    source_reference VARCHAR(255) DEFAULT 'Herbari Virtual del Mediterrani Occidental (UIB)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_flora_name ON flora(common_name_ca);
CREATE INDEX IF NOT EXISTS idx_flora_scientific ON flora(scientific_name);

-- 4. TAULA: NEGOCIS I OFICIS EMBLEMÀTICS
CREATE TABLE IF NOT EXISTS emblematic_businesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL UNIQUE,
    category_type VARCHAR(100) NOT NULL, -- 'Comerç arrelat', 'Comerç amb història', 'Comerç amb patrimoni'
    sector VARCHAR(100) NOT NULL,        -- 'Forn i Pastisseria', 'Artesania / Teixits', 'Restauració / Celler', 'Alimentació tradicional', 'Moda i Calçat'
    foundation_year INTEGER,
    municipality VARCHAR(100) NOT NULL,  -- p. ex: 'Palma', 'Inca', 'Sóller', 'Manacor', 'Pollença'
    address TEXT,
    latitude REAL,
    longitude REAL,
    history_summary TEXT NOT NULL,
    heritage_elements TEXT,             -- Elements protegits (fusteria modernista, rètols històrics, forns de llenya antics)
    is_active BOOLEAN DEFAULT 1,
    source_reference VARCHAR(255) DEFAULT 'Catàleg Emblemàtics Balears (IDI)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (latitude BETWEEN 39.0 AND 40.2 AND longitude BETWEEN 2.2 AND 3.6),
    CHECK (foundation_year IS NULL OR foundation_year > 1200)
);

CREATE INDEX IF NOT EXISTS idx_businesses_municipality ON emblematic_businesses(municipality);
CREATE INDEX IF NOT EXISTS idx_businesses_sector ON emblematic_businesses(sector);

-- 5. TAULA: FETS HISTÒRICS I CRONOLOGIA
CREATE TABLE IF NOT EXISTS historical_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL UNIQUE,
    historical_period VARCHAR(100) NOT NULL, -- 'Prehistòria i Talaiòtic', 'Època Romana', 'Època Islàmica (Mayûrqa)', 'Reialme de Mallorca (Edat Mitjana)', 'Edat Moderna', 'Edat Contemporània'
    year_start INTEGER NOT NULL,
    year_end INTEGER,
    date_display VARCHAR(100) NOT NULL,      -- p. ex: '31 de desembre de 1229', '1521 - 1523', 'c. 1000 a. C.'
    location_scope VARCHAR(150),             -- p. ex: 'Santa Ponça i Madîna Mayûrqa', 'Alaró', 'Illa de Mallorca'
    summary TEXT NOT NULL,
    detailed_description TEXT,
    key_figures TEXT,                        -- p. ex: 'Jaume I, Ramon Llull, Joanot Colom, Guillem Sagrera'
    source_reference VARCHAR(255) DEFAULT 'Arxiu del Regne de Mallorca (ARM) / GEM',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (year_end IS NULL OR year_start <= year_end)
);

CREATE INDEX IF NOT EXISTS idx_events_year ON historical_events(year_start);
CREATE INDEX IF NOT EXISTS idx_events_period ON historical_events(historical_period);

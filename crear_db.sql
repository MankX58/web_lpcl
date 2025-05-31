PRAGMA foreign_keys = ON;

-- 1) Tabla PALABRA
CREATE TABLE IF NOT EXISTS palabra (
    id_palabra INTEGER PRIMARY KEY AUTOINCREMENT,
    texto       TEXT    NOT NULL
);

-- 2) Tabla JUEGO
CREATE TABLE IF NOT EXISTS juego (
    id_juego     INTEGER PRIMARY KEY AUTOINCREMENT,
    id_palabra   INTEGER NOT NULL,
    fecha_inicio TEXT    NOT NULL,
    fecha_fin    TEXT    NULL,
    intentos_max INTEGER NOT NULL DEFAULT 6,
    estado       TEXT    NOT NULL    DEFAULT 'EN_JUEGO',
    FOREIGN KEY (id_palabra) REFERENCES palabra(id_palabra) ON DELETE CASCADE
);

-- 3) Tabla INTENTO
CREATE TABLE IF NOT EXISTS intento (
    id_intento    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_juego      INTEGER NOT NULL,
    letra         TEXT    NOT NULL,
    acierto       INTEGER NOT NULL,    -- 1 = acierto, 0 = fallo
    fecha_intento TEXT    NOT NULL,
    FOREIGN KEY (id_juego) REFERENCES juego(id_juego) ON DELETE CASCADE
);

-- Si la tabla esta vacia se insertan esas palabras
INSERT OR IGNORE INTO palabra (id_palabra, texto) VALUES
    (1, 'PYTHON'),
    (2, 'FLASK'),
    (3, 'GATO'),
    (4, 'MANZANA'),
    (5, 'COMPUTADORA');
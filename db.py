import sqlite3
from datetime import datetime
import os

DB_PATH = 'ahorcado.db'

def get_conn():
    """
    Abre la conexión a SQLite y habilita foreign keys.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn

def init_db():
    """
    Crea las tablas si no existen y agrega palabras de ejemplo.
    Se invoca desde app.py al arrancar si el archivo de BD no existe.
    """
    conn = get_conn()
    cursor = conn.cursor()

    # 1) Creamos la tabla 'palabra'
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS palabra (
            id_palabra INTEGER PRIMARY KEY AUTOINCREMENT,
            texto       TEXT    NOT NULL
        );
    """)

    # 2) Crear tabla 'juego'
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS juego (
            id_juego     INTEGER PRIMARY KEY AUTOINCREMENT,
            id_palabra   INTEGER NOT NULL,
            fecha_inicio TEXT    NOT NULL,
            fecha_fin    TEXT    NULL,
            intentos_max INTEGER NOT NULL DEFAULT 6,
            estado       TEXT    NOT NULL    DEFAULT 'EN_JUEGO',
            FOREIGN KEY (id_palabra) REFERENCES palabra(id_palabra) ON DELETE CASCADE
        );
    """)

    # 3) Crear tabla 'intento'
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intento (
            id_intento    INTEGER PRIMARY KEY AUTOINCREMENT,
            id_juego      INTEGER NOT NULL,
            letra         TEXT    NOT NULL,
            acierto       INTEGER NOT NULL,    -- 1 = verdad, 0 = falso
            fecha_intento TEXT    NOT NULL,
            FOREIGN KEY (id_juego) REFERENCES juego(id_juego) ON DELETE CASCADE
        );
    """)

    # Insertar palabras por defecto si la tabla de palabras está vacía
    cursor.execute("SELECT COUNT(*) as cnt FROM palabra;")
    if cursor.fetchone()['cnt'] == 0:
        ejemplos = ['PYTHON', 'FLASK', 'GATO', 'MANZANA', 'COMPUTADORA']
        for p in ejemplos:
            cursor.execute("INSERT INTO palabra (texto) VALUES (?);", (p,))

    conn.commit()
    conn.close()

def obtener_palabras():
    """
    Devuelve todas las filas de la tabla 'palabra'.
    """
    conn = get_conn()
    filas = conn.execute("SELECT id_palabra, texto FROM palabra;").fetchall()
    conn.close()
    return filas

def crear_juego(id_palabra, intentos_max=6):
    """
    Inserta un nuevo registro en 'juego' y devuelve el id_juego.
    """
    ahora = datetime.utcnow().isoformat()
    conn = get_conn()
    cursor = conn.execute(
        "INSERT INTO juego (id_palabra, fecha_inicio, intentos_max, estado) VALUES (?, ?, ?, ?);",
        (id_palabra, ahora, intentos_max, 'EN_JUEGO')
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return nuevo_id

def obtener_juego(id_juego):
    """
    Devuelve la fila de 'juego' correspondiente a id_juego, o None si no existe.
    """
    conn = get_conn()
    fila = conn.execute(
        "SELECT * FROM juego WHERE id_juego = ?;",
        (id_juego,)
    ).fetchone()
    conn.close()
    return fila

def registrar_intento(id_juego, letra, acierto):
    """
    Inserta un nuevo intento (letra + acierto) para un juego dado.
    """
    ahora = datetime.utcnow().isoformat()
    conn = get_conn()
    conn.execute(
        "INSERT INTO intento (id_juego, letra, acierto, fecha_intento) VALUES (?, ?, ?, ?);",
        (id_juego, letra, int(acierto), ahora)
    )
    conn.commit()
    conn.close()

def obtener_intentos(id_juego):
    """
    Devuelve todas las filas de 'intento' para un id_juego dado.
    """
    conn = get_conn()
    filas = conn.execute(
        "SELECT letra, acierto FROM intento WHERE id_juego = ?;",
        (id_juego,)
    ).fetchall()
    conn.close()
    return filas

def actualizar_estado(id_juego, nuevo_estado):
    """
    Actualiza el estado de un juego. Si es 'GANADO' o 'PERDIDO', también setea fecha_fin.
    """
    ahora = datetime.utcnow().isoformat()
    conn = get_conn()
    if nuevo_estado in ('GANADO', 'PERDIDO'):
        conn.execute(
            "UPDATE juego SET estado = ?, fecha_fin = ? WHERE id_juego = ?;",
            (nuevo_estado, ahora, id_juego)
        )
    else:
        conn.execute(
            "UPDATE juego SET estado = ? WHERE id_juego = ?;",
            (nuevo_estado, id_juego)
        )
    conn.commit()
    conn.close()
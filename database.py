import sqlite3

def conectar():
    return sqlite3.connect("banco.db")

def criar_banco():

    conn = conectar()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS historias(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        titulo TEXT,
        genero TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS capitulos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        historia_id INTEGER,
        titulo TEXT,
        conteudo TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS personagens(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        historia_id INTEGER,
        nome TEXT,
        descricao TEXT
    )
    """)

    conn.commit()
    conn.close()
import sqlite3

DATABASE_NAME = "database.db"

def get_connection():
    """Ritorna una connessione SQLite al file database.db."""
    return sqlite3.connect(DATABASE_NAME)

def init_db():
    """Crea le tabelle bookings e users se non esistono."""
    with get_connection() as conn:
        c = conn.cursor()
        
        # Tabella per le prenotazioni
        c.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            date TEXT NOT NULL,
            service TEXT NOT NULL
        )
        """)

        # Tabella per gli utenti
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT
        )
        """)

        conn.commit()

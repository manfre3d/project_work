import sqlite3
import bcrypt

DATABASE_NAME = "database.db"

def get_connection():
    """Ritorna una connessione SQLite al file database.db con Row factory."""
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row  
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection

def init_db():
    """Crea le tabelle bookings, users e sessions se non esistono."""
    with get_connection() as conn:
        c = conn.cursor()
        
        # Creazione tabella services
        c.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,         
            description TEXT,
            capacity INTEGER,           
            price REAL,                 
            active INTEGER NOT NULL DEFAULT 1  
        );
        """)
        
        # Creazione tabella bookings
        c.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                service_id INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                capacity_requested INTEGER NOT NULL DEFAULT 1,
                total_price REAL DEFAULT 0.0,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (service_id) REFERENCES services(id)
            );
        """)


        # Creazione tabella users
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                email TEXT UNIQUE,
                role TEXT NOT NULL DEFAULT 'user'  -- 'user' o 'admin'
            );
        """)
        
        # Creazione tabella sessions
        c.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # Crea un amministratore di default se non esiste
        c.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")
        admin_count = c.fetchone()["count"]
        if admin_count == 0:
            # Inserire un admin di default
            default_admin_username = "admin"
            default_admin_password = bcrypt.hashpw("admin".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            default_admin_email = "admin@example.com"
            c.execute("""
                INSERT INTO users (username, password, email, role)
                VALUES (?, ?, ?, 'admin')
            """, (default_admin_username, default_admin_password, default_admin_email))
            print("Amministratore di default creato: username='admin', password='admin'")
        
        conn.commit()

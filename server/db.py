import sqlite3
import bcrypt

DATABASE_NAME = "database.db"

def get_connection():
    """Ritorna una connessione SQLite al file database.
    db con Row factory."""
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row  
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection

def seed_services():
    """Popola la tabella services con dati di default."""
    services = [
        {"name": "Camera Singola", "description": "Camera per una persona", "capacity": 1, "price": 50.0, "active": 1},
        {"name": "Camera Doppia", "description": "Camera per due persone", "capacity": 2, "price": 100.0, "active": 1},
        {"name": "Suite", "description": "Camera di lusso per due persone", "capacity": 2, "price": 200.0, "active": 1},
        {"name": "Sala Riunioni", "description": "Sala riunioni per eventi aziendali", "capacity": 20, "price": 500.0, "active": 1},
    ]

    with get_connection() as conn:
        c = conn.cursor()
        for service in services:
            c.execute("""
                INSERT OR IGNORE INTO services (name, description, capacity, price, active)
                VALUES (?, ?, ?, ?, ?)
            """, (service["name"], service["description"], service["capacity"], service["price"], service["active"]))
        conn.commit()
        print("Servizi di default inseriti.")

def seed_bookings():
    """Popola la tabella bookings con dati di default."""
    bookings = [
        {"user_id": 1, "service_id": 1, "start_date": "2025-10-01", "end_date": "2025-11-05", "status": "confirmed", "capacity_requested": 1, "total_price": 200.0},
        {"user_id": 1, "service_id": 2, "start_date": "2025-10-01", "end_date": "2025-11-03", "status": "pending", "capacity_requested": 2, "total_price": 200.0},
    ]

    with get_connection() as conn:
        c = conn.cursor()
        for booking in bookings:
            c.execute("""
                INSERT INTO bookings (user_id, service_id, start_date, end_date, status, capacity_requested, total_price)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (booking["user_id"], booking["service_id"], booking["start_date"], booking["end_date"], booking["status"], booking["capacity_requested"], booking["total_price"]))
        conn.commit()
        print("Prenotazioni di default inserite.")

def seed_users():
    """Popola la tabella users con utenti di default."""
    import bcrypt

    users = [
        {"username": "mario", "password": bcrypt.hashpw("test".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"), "email": "mario@example.com", "role": "user"},
        {"username": "marco", "password": bcrypt.hashpw("test123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"), "email": "marco@example.com", "role": "user"},
    ]

    with get_connection() as conn:
        c = conn.cursor()
        for user in users:
            c.execute("""
                INSERT OR IGNORE INTO users (username, password, email, role)
                VALUES (?, ?, ?, ?)
            """, (user["username"], user["password"], user["email"], user["role"]))
        conn.commit()
        print("Utenti di default inseriti.")

def seed_all():
    """Esegue tutti i seed di default."""
    seed_services()
    seed_users()
    seed_bookings()
    print("Database inizializzato con dati di default.")

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
            default_admin_username = "admin"
            default_admin_password = bcrypt.hashpw("admin".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            default_admin_email = "admin@example.com"
            c.execute("""
                INSERT INTO users (username, password, email, role)
                VALUES (?, ?, ?, 'admin')
            """, (default_admin_username, default_admin_password, default_admin_email))
            print("Amministratore di default creato: username='admin', password='admin'")
            print("Inizializzazione del resto delle tabelle...")
            conn.commit()
            seed_all()
            print("Tabelle inizializzate")
            
        else:
            print("Tabelle già inizializzate")
            conn.commit()

    
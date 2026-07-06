import sqlite3
import os

class DatabaseManager:
    """Manages the SQLite connection and schema initialization."""

    DB_FILE = "transport_db.db"

    def __init__(self):
        self.conn = None

    def connect(self):
        """Connect to the database file. Raises exception on failure."""
        if not os.path.exists(self.DB_FILE):
            raise FileNotFoundError(f"Database file '{self.DB_FILE}' not found.")
        self.conn = sqlite3.connect(self.DB_FILE)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row
        self._initialize_schema()
        return self.conn

    def _initialize_schema(self):
        """Create tables and seed default data if needed."""
        cursor = self.conn.cursor()
        # Create vehicle_types if not exists (simplified – full schema already in the .sqlite file)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicle_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                is_synced INTEGER DEFAULT 0,
                sync_timestamp TIMESTAMP,
                is_deleted INTEGER DEFAULT 0
            );
        """)
        # Seed default vehicle types if table is empty
        cursor.execute("SELECT COUNT(*) FROM vehicle_types")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO vehicle_types (uuid, name) VALUES (?, ?)",
                [
                    ("550e8400-e29b-41d4-a716-446655440001", "Car"),
                    ("550e8400-e29b-41d4-a716-446655440002", "Bus"),
                    ("550e8400-e29b-41d4-a716-446655440003", "HiAce"),
                    ("550e8400-e29b-41d4-a716-446655440004", "Coaster"),
                    ("550e8400-e29b-41d4-a716-446655440005", "Ambulance"),
                    ("550e8400-e29b-41d4-a716-446655440006", "Pickup"),
                    ("550e8400-e29b-41d4-a716-446655440007", "Tractor"),
                    ("550e8400-e29b-41d4-a716-446655440008", "Motorcycle"),
                    ("550e8400-e29b-41d4-a716-446655440009", "Bicycle"),
                    ("550e8400-e29b-41d4-a716-446655440010", "Other"),
                ]
            )
        # Create remaining tables if needed (they will exist from initial schema, but safe)
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                registration_number TEXT UNIQUE NOT NULL,
                vehicle_type_id INTEGER NOT NULL REFERENCES vehicle_types(id),
                model TEXT NOT NULL,
                engine_number TEXT,
                chassis_number TEXT,
                fuel_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                is_synced INTEGER DEFAULT 0,
                sync_timestamp TIMESTAMP,
                is_deleted INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                designation TEXT NOT NULL,
                contact_number TEXT,
                cnic TEXT UNIQUE NOT NULL,
                assigned_vehicle_id INTEGER UNIQUE REFERENCES vehicles(id),
                assigned_route TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                is_synced INTEGER DEFAULT 0,
                sync_timestamp TIMESTAMP,
                is_deleted INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS daily_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                vehicle_id INTEGER NOT NULL REFERENCES vehicles(id),
                driver_id INTEGER NOT NULL REFERENCES drivers(id),
                log_date TEXT NOT NULL,
                from_time TEXT NOT NULL,
                to_time TEXT NOT NULL,
                purpose_route TEXT,
                meter_out REAL NOT NULL,
                meter_in REAL NOT NULL,
                mileage REAL NOT NULL,
                fuel REAL,
                mobile_oil REAL,
                remarks TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                is_synced INTEGER DEFAULT 0,
                sync_timestamp TIMESTAMP,
                is_deleted INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS repairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                vehicle_id INTEGER NOT NULL REFERENCES vehicles(id),
                repair_date TEXT NOT NULL,
                mileage REAL,
                description TEXT NOT NULL,
                cost REAL NOT NULL,
                performed_by TEXT,
                remarks TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                is_synced INTEGER DEFAULT 0,
                sync_timestamp TIMESTAMP,
                is_deleted INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS fuel_slips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                vehicle_id INTEGER NOT NULL REFERENCES vehicles(id),
                from_date TEXT NOT NULL,
                to_date TEXT NOT NULL,
                fuel_quantity REAL NOT NULL,
                amount REAL NOT NULL,
                receipt_number TEXT,
                average_mileage REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                is_synced INTEGER DEFAULT 0,
                sync_timestamp TIMESTAMP,
                is_deleted INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                is_synced INTEGER DEFAULT 0,
                sync_timestamp TIMESTAMP,
                is_deleted INTEGER DEFAULT 0
            );
        """)
        self.conn.commit()
    
    def close(self):
        """Close the database connection gracefully."""
        if self.conn:
            self.conn.close()
            self.conn = None
import sqlite3
import os
import sys
import shutil
from datetime import datetime
from utils.resource_path import resource_path


class DatabaseManager:
    """
    Manages the SQLite database connection.
    In development: uses the seed database from the project root.
    In a PyInstaller bundle: copies the seed database to the user's AppData folder
    on first run, then uses that working copy.
    """

    # Name of the database file (must match the actual file)
    DB_FILENAME = "transport_db.db"

    def __init__(self):
        self.conn = None

    def connect(self):
        """Open (or create) the working database and return the connection."""
        # Determine writable location for the working database
        working_dir = self._get_working_dir()
        os.makedirs(working_dir, exist_ok=True)
        working_db_path = os.path.join(working_dir, self.DB_FILENAME)

        # If the working copy doesn't exist, copy the seed database from resources
        if not os.path.exists(working_db_path):
            seed_db_path = resource_path(self.DB_FILENAME)
            if os.path.exists(seed_db_path):
                shutil.copy2(seed_db_path, working_db_path)
            else:
                raise FileNotFoundError(
                    f"Seed database '{self.DB_FILENAME}' not found at {seed_db_path}."
                )

        # Connect to the working copy
        self.conn = sqlite3.connect(working_db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row
        self._initialize_schema()
        return self.conn

    def _get_working_dir(self) -> str:
        """
        Return a writable directory for the working database.
        In production (frozen) we use %APPDATA%\BBSTUD-TMS.
        In development we use the current directory so that existing data is not lost.
        """
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller bundle – use AppData
            return os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "BBSTUD-TMS")
        else:
            # Development mode – use the project root
            return os.path.abspath(".")

    def _initialize_schema(self):
        """Create tables and seed default data if they don't exist yet."""
        cursor = self.conn.cursor()

        # --- vehicle_types ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicle_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                is_synced INTEGER DEFAULT 0,
                sync_timestamp TIMESTAMP,
                is_deleted INTEGER DEFAULT 0
            )
        """)

        # Seed default vehicle types if the table is empty
        cursor.execute("SELECT COUNT(*) FROM vehicle_types")
        if cursor.fetchone()[0] == 0:
            default_types = [
                ("550e8400-e29b-41d4-a716-446655440001", "Car", "Standard passenger vehicle"),
                ("550e8400-e29b-41d4-a716-446655440002", "Bus", "Large bus for student transport"),
                ("550e8400-e29b-41d4-a716-446655440003", "HiAce", "Toyota HiAce van"),
                ("550e8400-e29b-41d4-a716-446655440004", "Coaster", "Toyota Coaster"),
                ("550e8400-e29b-41d4-a716-446655440005", "Ambulance", "Medical emergency vehicle"),
                ("550e8400-e29b-41d4-a716-446655440006", "Pickup", "Pickup truck"),
                ("550e8400-e29b-41d4-a716-446655440007", "Tractor", "Agricultural tractor"),
                ("550e8400-e29b-41d4-a716-446655440008", "Motorcycle", "Two-wheeled vehicle"),
                ("550e8400-e29b-41d4-a716-446655440009", "Bicycle", "Pedal cycle"),
                ("550e8400-e29b-41d4-a716-446655440010", "Other", "Any other vehicle type"),
            ]
            cursor.executemany(
                "INSERT INTO vehicle_types (uuid, name, description) VALUES (?, ?, ?)",
                default_types,
            )

        # --- vehicles ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                registration_number TEXT UNIQUE NOT NULL,
                vehicle_type_id INTEGER NOT NULL REFERENCES vehicle_types(id) ON DELETE RESTRICT,
                model TEXT NOT NULL,
                engine_number TEXT,
                chassis_number TEXT,
                fuel_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                is_synced INTEGER DEFAULT 0,
                sync_timestamp TIMESTAMP,
                is_deleted INTEGER DEFAULT 0
            )
        """)

        # --- drivers ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                designation TEXT NOT NULL,
                contact_number TEXT,
                cnic TEXT UNIQUE NOT NULL,
                assigned_vehicle_id INTEGER UNIQUE REFERENCES vehicles(id) ON DELETE SET NULL,
                assigned_route TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                is_synced INTEGER DEFAULT 0,
                sync_timestamp TIMESTAMP,
                is_deleted INTEGER DEFAULT 0
            )
        """)

        # --- daily_logs ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
                driver_id INTEGER NOT NULL REFERENCES drivers(id) ON DELETE RESTRICT,
                log_date TEXT NOT NULL,
                from_time TEXT NOT NULL,
                to_time TEXT NOT NULL,
                purpose_route TEXT,
                meter_out REAL NOT NULL,
                meter_in REAL NOT NULL,
                mileage REAL NOT NULL CHECK(mileage >= 0),
                fuel REAL,
                mobile_oil REAL,
                remarks TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                is_synced INTEGER DEFAULT 0,
                sync_timestamp TIMESTAMP,
                is_deleted INTEGER DEFAULT 0
            )
        """)

        # --- repairs ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
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
            )
        """)

        # --- fuel_slips ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fuel_slips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
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
            )
        """)

        # --- users ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('Transport Head','Transport Clerk')),
                status TEXT NOT NULL DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                is_synced INTEGER DEFAULT 0,
                sync_timestamp TIMESTAMP,
                is_deleted INTEGER DEFAULT 0
            )
        """)

        # Ensure indexes exist
        cursor.executescript("""
            CREATE INDEX IF NOT EXISTS idx_vehicles_sync ON vehicles(is_synced, sync_timestamp);
            CREATE INDEX IF NOT EXISTS idx_drivers_sync ON drivers(is_synced, sync_timestamp);
            CREATE INDEX IF NOT EXISTS idx_daily_logs_sync ON daily_logs(is_synced, sync_timestamp);
            CREATE INDEX IF NOT EXISTS idx_fuel_slips_sync ON fuel_slips(is_synced, sync_timestamp);
            CREATE INDEX IF NOT EXISTS idx_repairs_sync ON repairs(is_synced, sync_timestamp);
            CREATE INDEX IF NOT EXISTS idx_users_sync ON users(is_synced, sync_timestamp);
            CREATE INDEX IF NOT EXISTS idx_vehicle_types_sync ON vehicle_types(is_synced, sync_timestamp);
            CREATE INDEX IF NOT EXISTS idx_daily_logs_vehicle ON daily_logs(vehicle_id);
            CREATE INDEX IF NOT EXISTS idx_daily_logs_driver ON daily_logs(driver_id);
            CREATE INDEX IF NOT EXISTS idx_fuel_slips_vehicle ON fuel_slips(vehicle_id);
            CREATE INDEX IF NOT EXISTS idx_repairs_vehicle ON repairs(vehicle_id);
        """)

        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
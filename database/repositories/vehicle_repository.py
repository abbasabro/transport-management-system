import uuid
import sqlite3
from datetime import datetime
from database.database_manager import DatabaseManager

class VehicleRepository:
    def __init__(self,  db: DatabaseManager):
        self.db = db

    def get_all_active(self):
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT v.id, v.uuid, v.registration_number, vt.name as vehicle_type,
                   v.model, v.engine_number, v.chassis_number, v.fuel_type
            FROM vehicles v
            JOIN vehicle_types vt ON v.vehicle_type_id = vt.id
            WHERE v.is_deleted = 0
            ORDER BY v.registration_number
        """)
        return [dict(row) for row in cursor.fetchall()]

    def get_by_id(self, vehicle_id):
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM vehicles WHERE id = ? AND is_deleted = 0", (vehicle_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_vehicle_types(self) -> list[tuple[int, str]]:
        """Return list of (id, name) for all active vehicle types."""
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT id, name FROM vehicle_types WHERE is_deleted = 0 ORDER BY name"
        )
        return cursor.fetchall()


    def add(self, registration_number, vehicle_type_id, model, engine_number, chassis_number, fuel_type):
        new_uuid = str(uuid.uuid4())
        now = datetime.now().isoformat()
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO vehicles (uuid, registration_number, vehicle_type_id, model, engine_number, chassis_number, fuel_type,created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (new_uuid, registration_number, vehicle_type_id, model, engine_number, chassis_number, fuel_type, now))
            self.db.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            err_msg = str(e)
            if "UNIQUE constraint failed: vehicles.registration_number" in err_msg:
                raise ValueError(
                    f"Registration number '{registration_number}' already exists."
                )
            if "FOREIGN KEY constraint failed" in err_msg:
                raise ValueError("Invalid vehicle type selected.")
            raise e

    def update(self, vehicle_id, registration_number, vehicle_type_id, model, engine_number, chassis_number, fuel_type, status):
        now = datetime.now().isoformat()
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                UPDATE vehicles SET registration_number=?, vehicle_type_id=?, model=?, engine_number=?, chassis_number=?, fuel_type=?,  updated_at=?
                WHERE id=?
            """, (registration_number, vehicle_type_id, model, engine_number, chassis_number, fuel_type, now, vehicle_id))
            if cursor.rowcount == 0:
                raise ValueError(f"Vehicle with REG: {registration_number} not found or already deleted.")
            self.db.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            err_msg = str(e)
            if "UNIQUE constraint failed: vehicles.registration_number" in err_msg:
                raise ValueError(
                    f"Registration number '{registration_number}' already exists."
                )
            if "FOREIGN KEY constraint failed" in err_msg:
                raise ValueError("Invalid vehicle type selected.")
            raise e
        
    def soft_delete(self, vehicle_id):
        cursor = self.db.conn.cursor()
        cursor.execute("UPDATE vehicles SET is_deleted=1, updated_at=? WHERE id=?", (datetime.now().isoformat(), vehicle_id))
        if cursor.rowcount == 0:
            raise ValueError(f"Vehicle with ID {vehicle_id} not found or already deleted.")
        self.db.conn.commit()
        return True

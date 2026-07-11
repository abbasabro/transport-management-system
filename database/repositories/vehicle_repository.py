import uuid
import sqlite3
from datetime import datetime
from database.database_manager import DatabaseManager


class VehicleRepository:
    """
    Repository for vehicles and vehicle types.
    Now supports lifecycle via a 'status' column.
    """

    def __init__(self, db: DatabaseManager):
        self.db = db

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------
    def get_all_active(self) -> list[dict]:
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT v.id, v.uuid, v.registration_number, vt.name AS vehicle_type,
                   v.model, v.engine_number, v.chassis_number, v.fuel_type,
                   v.status, v.is_deleted
            FROM vehicles v
            JOIN vehicle_types vt ON v.vehicle_type_id = vt.id
            WHERE v.is_deleted = 0
            ORDER BY v.status = 'Inactive', v.registration_number
            """
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_active_vehicles(self) -> list[dict]:
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT v.id, v.uuid, v.registration_number, vt.name AS vehicle_type,
                   v.model, v.engine_number, v.chassis_number, v.fuel_type,
                   v.status
            FROM vehicles v
            JOIN vehicle_types vt ON v.vehicle_type_id = vt.id
            WHERE v.is_deleted = 0 AND v.status = 'Active'
            ORDER BY v.registration_number
            """
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_by_id(self, vehicle_id: int) :
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT * FROM vehicles WHERE id = ? AND is_deleted = 0",
            (vehicle_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_vehicle_types(self) -> list[tuple[int, str]]:
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT id, name FROM vehicle_types WHERE is_deleted = 0 ORDER BY name"
        )
        return cursor.fetchall()

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------
    def add(
        self,
        registration_number: str,
        vehicle_type_id: int,
        model: str,
        engine_number: str,
        chassis_number: str,
        fuel_type: str,
        status: str = "Active",   # NEW optional parameter
    ) -> bool:
        """
        Insert a new vehicle. Status defaults to 'Active' if not provided.
        """
        new_uuid = str(uuid.uuid4())
        now = datetime.now().isoformat()
        cursor = self.db.conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO vehicles (
                    uuid, registration_number, vehicle_type_id, model,
                    engine_number, chassis_number, fuel_type, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    new_uuid,
                    registration_number,
                    vehicle_type_id,
                    model,
                    engine_number,
                    chassis_number,
                    fuel_type,
                    status,
                    now,
                ),
            )
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

    def update(
        self,
        vehicle_id: int,
        registration_number: str,
        vehicle_type_id: int,
        model: str,
        engine_number: str,
        chassis_number: str,
        fuel_type: str,
        status: str,
    ) -> bool:
        now = datetime.now().isoformat()
        cursor = self.db.conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE vehicles
                SET registration_number = ?, vehicle_type_id = ?, model = ?,
                    engine_number = ?, chassis_number = ?, fuel_type = ?,
                    status = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    registration_number,
                    vehicle_type_id,
                    model,
                    engine_number,
                    chassis_number,
                    fuel_type,
                    status,
                    now,
                    vehicle_id,
                ),
            )
            if cursor.rowcount == 0:
                raise ValueError(f"Vehicle with ID {vehicle_id} not found or already deleted.")
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

    def soft_delete(self, vehicle_id: int) -> bool:
        cursor = self.db.conn.cursor()
        cursor.execute(
            "UPDATE vehicles SET is_deleted = 1, updated_at = ? WHERE id = ? AND is_deleted = 0",
            (datetime.now().isoformat(), vehicle_id),
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Vehicle with ID {vehicle_id} not found or already deleted.")
        self.db.conn.commit()
        return True

    def add_vehicle_type(self, name: str, description: str = "") -> bool:
        new_uuid = str(uuid.uuid4())
        now = datetime.now().isoformat()
        cursor = self.db.conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO vehicle_types (uuid, name, description, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (new_uuid, name, description, now),
            )
            self.db.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: vehicle_types.name" in str(e):
                raise ValueError(f"Vehicle type '{name}' already exists.")
            raise e
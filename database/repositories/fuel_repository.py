import uuid
import sqlite3
from datetime import datetime
from database.database_manager import DatabaseManager


class FuelRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_all_active(self) -> list[dict]:
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT f.id, f.uuid, f.vehicle_id, f.from_date, f.to_date,
                   f.fuel_quantity, f.amount, f.receipt_number,
                   f.average_mileage, v.registration_number AS vehicle_reg
            FROM fuel_slips f
            JOIN vehicles v ON f.vehicle_id = v.id AND v.is_deleted = 0
            WHERE f.is_deleted = 0
            ORDER BY f.to_date DESC
            """
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_by_id(self, slip_id: int):
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT f.id, f.uuid, f.vehicle_id, f.from_date, f.to_date,
                   f.fuel_quantity, f.amount, f.receipt_number,
                   f.average_mileage, v.registration_number AS vehicle_reg
            FROM fuel_slips f
            JOIN vehicles v ON f.vehicle_id = v.id AND v.is_deleted = 0
            WHERE f.id = ? AND f.is_deleted = 0
            """,
            (slip_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_by_vehicle(self, vehicle_id: int):
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT f.id, f.uuid, f.vehicle_id, f.from_date, f.to_date,
                   f.fuel_quantity, f.amount, f.receipt_number,
                   f.average_mileage, v.registration_number AS vehicle_reg
            FROM fuel_slips f
            JOIN vehicles v ON f.vehicle_id = v.id AND v.is_deleted = 0
            WHERE f.vehicle_id = ? AND f.is_deleted = 0
            ORDER BY f.to_date DESC
            """,
            (vehicle_id,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def search_by_receipt(self, receipt_number: str) :
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT f.id, f.uuid, f.vehicle_id, f.from_date, f.to_date,
                   f.fuel_quantity, f.amount, f.receipt_number,
                   f.average_mileage, v.registration_number AS vehicle_reg
            FROM fuel_slips f
            JOIN vehicles v ON f.vehicle_id = v.id AND v.is_deleted = 0
            WHERE f.receipt_number LIKE ? AND f.is_deleted = 0
            ORDER BY f.to_date DESC
            """,
            (f"%{receipt_number}%",),
        )
        return [dict(row) for row in cursor.fetchall()]

  
    def add(
        self,
        vehicle_id,
        from_date,
        to_date,
        fuel_quantity,
        amount,
        receipt_number ,
        average_mileage,
    ):
        new_uuid = str(uuid.uuid4())
        now = datetime.now().isoformat()
        cursor = self.db.conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO fuel_slips (
                    uuid, vehicle_id, from_date, to_date, fuel_quantity,
                    amount, receipt_number, average_mileage, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    new_uuid,
                    vehicle_id,
                    from_date,
                    to_date,
                    fuel_quantity,
                    amount,
                    receipt_number,
                    average_mileage,
                    now,
                ),
            )
            self.db.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                raise ValueError("Invalid vehicle ID.")
            raise e

    def update(
        self,
        slip_id,
        vehicle_id,
        from_date,
        to_date,
        fuel_quantity,
        amount,
        receipt_number ,
        average_mileage,
       
    ):
        now = datetime.now().isoformat()
        cursor = self.db.conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE fuel_slips
                SET vehicle_id = ?, from_date = ?, to_date = ?, fuel_quantity = ?,
                    amount = ?, receipt_number = ?, average_mileage = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    vehicle_id,
                    from_date,
                    to_date,
                    fuel_quantity,
                    amount,
                    receipt_number,
                    average_mileage,
                    now,
                    slip_id,
                ),
            )
            if cursor.rowcount == 0:
                raise ValueError(f"Fuel slip with ID {slip_id} not found or already deleted.")
            self.db.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                raise ValueError("Invalid vehicle ID.")
            raise e

    def soft_delete(self, slip_id: int) -> bool:
        cursor = self.db.conn.cursor()
        cursor.execute(
            "UPDATE fuel_slips SET is_deleted = 1, updated_at = ? WHERE id = ? AND is_deleted = 0",
            (datetime.now().isoformat(), slip_id),
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Fuel slip with ID {slip_id} not found or already deleted.")
        self.db.conn.commit()
        return True
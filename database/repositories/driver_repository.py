import uuid, sqlite3
from datetime import datetime
from database.database_manager import DatabaseManager

class DriverRepository:
    def __init__(self, db:DatabaseManager):
        self.db = db

    def get_all_active_with_vehicle(self):
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT d.id, d.uuid, d.name, d.designation, d.contact_number, d.cnic,
                   d.assigned_route, d.assigned_vehicle_id,
                   v.registration_number as vehicle_reg
            FROM drivers d
            LEFT JOIN vehicles v ON d.assigned_vehicle_id = v.id AND v.is_deleted=0
            WHERE d.is_deleted = 0
            ORDER BY d.name
        """)
        return [dict(row) for row in cursor.fetchall()]

    def add(self, name, designation, contact_number, cnic, assigned_vehicle_id, assigned_route):
        new_uuid = str(uuid.uuid4())
        now = datetime.now().isoformat()
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO drivers (uuid, name, designation, contact_number, cnic, assigned_vehicle_id, assigned_route, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (new_uuid, name, designation, contact_number, cnic, assigned_vehicle_id, assigned_route, now))
            self.db.conn.commit()
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: drivers.cnic" in str(e):
                raise Exception("CNIC already exists.")
            if "UNIQUE constraint failed: drivers.assigned_vehicle_id" in str(e):
                raise Exception("Vehicle already assigned to another driver.")
            raise e

    def update(self, driver_id, name, designation, contact_number,  assigned_vehicle_id, assigned_route):
        now = datetime.now().isoformat()
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                UPDATE drivers SET name=?, designation=?, contact_number=?,  assigned_vehicle_id=?, assigned_route=?, updated_at=?
                WHERE id=?
            """, (name, designation, contact_number,  assigned_vehicle_id, assigned_route, now, driver_id))
            self.db.conn.commit()
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: drivers.cnic" in str(e):
                raise Exception("CNIC already exists.")
            if "UNIQUE constraint failed: drivers.assigned_vehicle_id" in str(e):
                raise Exception("Vehicle already assigned to another driver.")
            raise e

    def soft_delete(self, driver_id):
        cursor = self.db.conn.cursor()
        cursor.execute("UPDATE drivers SET is_deleted=1, updated_at=? WHERE id=?", (datetime.now().isoformat(), driver_id))
        self.db.conn.commit()

    def get_driver_by_vehicle(self, vehicle_id):
        """Return driver info for a given vehicle (if any)."""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT id, name FROM drivers
            WHERE assigned_vehicle_id = ? AND is_deleted=0
        """, (vehicle_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_by_id(self, driver_id: int) :
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT d.id, d.uuid, d.name, d.designation, d.contact_number,
                   d.cnic, d.assigned_vehicle_id, d.assigned_route,
                   v.registration_number AS vehicle_reg
            FROM drivers d
            LEFT JOIN vehicles v ON d.assigned_vehicle_id = v.id AND v.is_deleted = 0
            WHERE d.id = ? AND d.is_deleted = 0
            """,
            (driver_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
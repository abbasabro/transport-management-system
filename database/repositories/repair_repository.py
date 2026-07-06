import uuid,sqlite3
from datetime import datetime
from database.database_manager import DatabaseManager

class RepairRepository:
    def __init__(self, db:DatabaseManager):
        self.db = db

    def get_all_active(self):
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT r.id, r.uuid, r.vehicle_id, r.repair_date, r.mileage,
                   r.description, r.cost, r.performed_by, r.remarks,
                   v.registration_number as vehicle_reg
            FROM repairs r
            JOIN vehicles v ON r.vehicle_id = v.id AND v.is_deleted=0
            WHERE r.is_deleted = 0
            ORDER BY r.repair_date DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

    def search_by_description(self, search_text):
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT r.id, r.uuid, r.vehicle_id, r.repair_date, r.mileage,
                   r.description, r.cost, r.performed_by, r.remarks,
                   v.registration_number as vehicle_reg
            FROM repairs r
            JOIN vehicles v ON r.vehicle_id = v.id AND v.is_deleted=0
            WHERE r.description LIKE ? AND r.is_deleted = 0
            ORDER BY r.repair_date DESC
        """, ('%' + search_text + '%',))
        return [dict(row) for row in cursor.fetchall()]

    def add(self, vehicle_id, repair_date, mileage, description, cost, performed_by, remarks):
        new_uuid = str(uuid.uuid4())
        now = datetime.now().isoformat()
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO repairs (uuid, vehicle_id, repair_date, mileage, description, cost, performed_by, remarks, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (new_uuid, vehicle_id, repair_date, mileage, description, cost, performed_by, remarks, now))
            self.db.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                raise ValueError("Invalid vehicle ID.")
            raise e

    def update(self, repair_id, vehicle_id, repair_date, mileage, description, cost, performed_by, remarks):
        now = datetime.now().isoformat()
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                UPDATE repairs SET vehicle_id=?, repair_date=?, mileage=?, description=?, cost=?, performed_by=?, remarks=?, updated_at=?
                WHERE id=?
            """, (vehicle_id, repair_date, mileage, description, cost, performed_by, remarks, now, repair_id))
            if cursor.rowcount == 0:
                raise ValueError(f"Repair with ID {repair_id} not found or already deleted.")
            self.db.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                raise ValueError("Invalid vehicle ID.")
            raise e

    def soft_delete(self, repair_id):
        cursor = self.db.conn.cursor()
        cursor.execute("UPDATE repairs SET is_deleted=1, updated_at=? WHERE id=?", (datetime.now().isoformat(), repair_id))
        if cursor.rowcount == 0:
            raise ValueError(f"Repair with ID {repair_id} not found or already deleted.")
        self.db.conn.commit()
        return True

    
    def get_by_id(self, repair_id: int) :
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT r.id, r.uuid, r.vehicle_id, r.repair_date, r.mileage,
                   r.description, r.cost, r.performed_by, r.remarks,
                   v.registration_number AS vehicle_reg
            FROM repairs r
            JOIN vehicles v ON r.vehicle_id = v.id AND v.is_deleted = 0
            WHERE r.id = ? AND r.is_deleted = 0
            """,
            (repair_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
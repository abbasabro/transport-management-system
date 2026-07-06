import uuid,sqlite3
from datetime import datetime
from database.database_manager import DatabaseManager

class DailyLogRepository:
    def __init__(self, db:DatabaseManager):
        self.db = db

    def add_log(self, vehicle_id, driver_id, log_date, from_time, to_time, purpose_route,
                meter_out, meter_in, mileage, fuel, mobile_oil, remarks):
        new_uuid = str(uuid.uuid4())
        now = datetime.now().isoformat()
        cursor = self.db.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO daily_logs (uuid, vehicle_id, driver_id, log_date, from_time, to_time,
                                        purpose_route, meter_out, meter_in, mileage, fuel, mobile_oil, remarks, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (new_uuid, vehicle_id, driver_id, log_date, from_time, to_time, purpose_route,
                meter_out, meter_in, mileage, fuel, mobile_oil, remarks, now))
            self.db.conn.commit()
        except sqlite3.IntegrityError as e:
            # Foreign key error if vehicle_id or driver_id is invalid
            if "FOREIGN KEY constraint failed" in str(e):
                raise ValueError("Invalid vehicle or driver ID.")
            raise e

    def get_logs_for_vehicle(self, vehicle_id):
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT log_date, from_time, to_time, purpose_route, meter_out, meter_in,
                   mileage, fuel, mobile_oil, remarks
            FROM daily_logs
            WHERE vehicle_id = ? AND is_deleted = 0
            ORDER BY log_date DESC, from_time DESC
        """, (vehicle_id,))
        return [dict(row) for row in cursor.fetchall()]
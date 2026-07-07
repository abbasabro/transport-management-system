import uuid
import sqlite3
from datetime import datetime
from database.database_manager import DatabaseManager


class DailyLogRepository:
    """Repository for daily log entries, now with pagination and date filtering."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def add_log(
        self,
        vehicle_id: int,
        driver_id: int,
        log_date: str,
        from_time: str,
        to_time: str,
        purpose_route: str,
        meter_out: float,
        meter_in: float,
        mileage: float,
        fuel,
        mobile_oil,
        remarks,
    ) -> bool:
        """Insert a new daily log."""
        new_uuid = str(uuid.uuid4())
        now = datetime.now().isoformat()
        cursor = self.db.conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO daily_logs (
                    uuid, vehicle_id, driver_id, log_date, from_time, to_time,
                    purpose_route, meter_out, meter_in, mileage, fuel, mobile_oil,
                    remarks, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    new_uuid, vehicle_id, driver_id, log_date, from_time, to_time,
                    purpose_route, meter_out, meter_in, mileage, fuel, mobile_oil,
                    remarks, now,
                ),
            )
            self.db.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                raise ValueError("Invalid vehicle or driver ID.")
            raise e

    def get_logs_for_vehicle(self, vehicle_id: int) -> list[dict]:
        """Return all logs for a vehicle (used by existing reports)."""
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT log_date, from_time, to_time, purpose_route,
                   meter_out, meter_in, mileage, fuel, mobile_oil, remarks
            FROM daily_logs
            WHERE vehicle_id = ? AND is_deleted = 0
            ORDER BY log_date DESC, from_time DESC
            """,
            (vehicle_id,),
        )
        return [dict(row) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Paginated and filtered queries for All Logs dialog
    # ------------------------------------------------------------------
    def get_logs_for_vehicle_filtered(
        self,
        vehicle_id: int,
        from_date,
        to_date,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict]:
        """
        Retrieve a page of logs for a vehicle, optionally filtered by date range.
        Returns the full row (all columns) for display in the dialog.
        """
        query = """
            SELECT id, uuid, vehicle_id, driver_id, log_date, from_time, to_time,
                   purpose_route, meter_out, meter_in, mileage, fuel, mobile_oil, remarks
            FROM daily_logs
            WHERE vehicle_id = ? AND is_deleted = 0
        """
        params = [vehicle_id]
        if from_date:
            query += " AND log_date >= ?"
            params.append(from_date)
        if to_date:
            query += " AND log_date <= ?"
            params.append(to_date)
        query += " ORDER BY log_date ASC, from_time ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = self.db.conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_logs_count_for_vehicle(
        self,
        vehicle_id: int,
        from_date,
        to_date,
    ) -> int:
        """Return the total number of logs for a vehicle (after optional date filter)."""
        query = "SELECT COUNT(*) FROM daily_logs WHERE vehicle_id = ? AND is_deleted = 0"
        params = [vehicle_id]
        if from_date:
            query += " AND log_date >= ?"
            params.append(from_date)
        if to_date:
            query += " AND log_date <= ?"
            params.append(to_date)

        cursor = self.db.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()[0]
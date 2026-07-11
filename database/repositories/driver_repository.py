import uuid
import sqlite3
from datetime import datetime
from database.database_manager import DatabaseManager


class DriverRepository:
    """Repository for drivers with lifecycle management (status)."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------
    def get_all_drivers_with_vehicle(self) -> list[dict]:
        """
        Return ALL non‑deleted drivers (Active + Inactive) with vehicle reg.
        Inactive drivers are sorted to the bottom.
        """
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT d.id, d.uuid, d.name, d.designation, d.contact_number,
                   d.cnic, d.assigned_vehicle_id, d.assigned_route,
                   d.status, d.is_deleted,
                   v.registration_number AS vehicle_reg
            FROM drivers d
            LEFT JOIN vehicles v ON d.assigned_vehicle_id = v.id AND v.is_deleted = 0
            WHERE d.is_deleted = 0
            ORDER BY d.status = 'Inactive', d.name
            """
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_active_drivers_with_vehicle(self) -> list[dict]:
        """
        Return only Active drivers (non‑deleted) with vehicle registration.
        Used for operational dropdowns and dashboard counts.
        """
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT d.id, d.uuid, d.name, d.designation, d.contact_number,
                   d.cnic, d.assigned_vehicle_id, d.assigned_route,
                   d.status,
                   v.registration_number AS vehicle_reg
            FROM drivers d
            LEFT JOIN vehicles v ON d.assigned_vehicle_id = v.id AND v.is_deleted = 0
            WHERE d.is_deleted = 0 AND d.status = 'Active'
            ORDER BY d.name
            """
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_by_id(self, driver_id: int) :
        """Return a single driver (any status) by ID."""
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT d.id, d.uuid, d.name, d.designation, d.contact_number,
                   d.cnic, d.assigned_vehicle_id, d.assigned_route, d.status,
                   v.registration_number AS vehicle_reg
            FROM drivers d
            LEFT JOIN vehicles v ON d.assigned_vehicle_id = v.id AND v.is_deleted = 0
            WHERE d.id = ? AND d.is_deleted = 0
            """,
            (driver_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_driver_by_vehicle(self, vehicle_id: int) :
        """
        Return the Active driver assigned to a specific vehicle.
        Inactive drivers are not returned because they cannot be assigned.
        """
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT id, name FROM drivers
            WHERE assigned_vehicle_id = ? AND is_deleted = 0 AND status = 'Active'
            """,
            (vehicle_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def find_by_cnic(self, cnic: str) :
        """Find a driver by CNIC across all non‑deleted (any status)."""
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT id, name, cnic, status FROM drivers
            WHERE cnic = ? AND is_deleted = 0
            """,
            (cnic,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------
    def add(
        self,
        name: str,
        designation: str,
        contact_number: str,
        cnic: str,
        assigned_vehicle_id,
        assigned_route: str,
    ) -> bool:
        """
        Insert a new driver (status defaults to 'Active').
        Raises ValueError if CNIC already exists (active driver) or if an
        inactive driver with the same CNIC is found (special case for UI).
        """
        # Check for existing CNIC
        existing = self.find_by_cnic(cnic)
        if existing:
            if existing["status"] == "Active":
                raise ValueError(f"CNIC '{cnic}' already exists (active).")
            else:
                # Inactive driver exists – raise a specific error that the UI can catch
                raise ValueError("INACTIVE_DRIVER_EXISTS")
                # The UI will handle this and offer reactivation.

        new_uuid = str(uuid.uuid4())
        now = datetime.now().isoformat()
        cursor = self.db.conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO drivers (
                    uuid, name, designation, contact_number, cnic,
                    assigned_vehicle_id, assigned_route, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    new_uuid,
                    name,
                    designation,
                    contact_number,
                    cnic,
                    assigned_vehicle_id,
                    assigned_route,
                    now,
                ),
            )
            self.db.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            err_msg = str(e)
            if "UNIQUE constraint failed: drivers.cnic" in err_msg:
                raise ValueError(f"CNIC '{cnic}' already exists.")
            if "UNIQUE constraint failed: drivers.assigned_vehicle_id" in err_msg:
                raise ValueError(
                    "The selected vehicle is already assigned to another active driver."
                )
            raise e

    def update(
        self,
        driver_id: int,
        name: str,
        designation: str,
        contact_number: str,
        cnic: str,
        assigned_vehicle_id,
        assigned_route: str,
        status: str,                # NEW parameter
    ) -> bool:
        """
        Update an existing driver, including status.
        """
        now = datetime.now().isoformat()
        cursor = self.db.conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE drivers
                SET name = ?, designation = ?, contact_number = ?, cnic = ?,
                    assigned_vehicle_id = ?, assigned_route = ?, status = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    name,
                    designation,
                    contact_number,
                    cnic,
                    assigned_vehicle_id,
                    assigned_route,
                    status,
                    now,
                    driver_id,
                ),
            )
            if cursor.rowcount == 0:
                raise ValueError(f"Driver with ID {driver_id} not found or already deleted.")
            self.db.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            err_msg = str(e)
            if "UNIQUE constraint failed: drivers.cnic" in err_msg:
                raise ValueError(f"CNIC '{cnic}' already exists.")
            if "UNIQUE constraint failed: drivers.assigned_vehicle_id" in err_msg:
                raise ValueError(
                    "The selected vehicle is already assigned to another active driver."
                )
            raise e

    def reactivate(self, driver_id: int) -> bool:
        """Set an inactive driver back to Active."""
        cursor = self.db.conn.cursor()
        cursor.execute(
            "UPDATE drivers SET status = 'Active', updated_at = ? WHERE id = ? AND is_deleted = 0",
            (datetime.now().isoformat(), driver_id),
        )
        if cursor.rowcount == 0:
            raise ValueError("Driver not found or already deleted.")
        self.db.conn.commit()
        return True

    def soft_delete(self, driver_id: int) -> bool:
        """Soft‑delete a driver (is_deleted = 1). Status is not changed."""
        cursor = self.db.conn.cursor()
        cursor.execute(
            "UPDATE drivers SET is_deleted = 1, updated_at = ? WHERE id = ? AND is_deleted = 0",
            (datetime.now().isoformat(), driver_id),
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Driver with ID {driver_id} not found or already deleted.")
        self.db.conn.commit()
        return True
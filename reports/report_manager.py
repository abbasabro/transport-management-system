from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget
from reports.vehicle_report import VehicleReport
from reports.driver_report import DriverReport
from reports.vehicle_list_report import VehicleListReport
from reports.repair_report import RepairReport
from database.repositories.vehicle_repository import VehicleRepository
from database.repositories.driver_repository import DriverRepository
from database.repositories.daily_log_repository import DailyLogRepository
from database.repositories.repair_repository import RepairRepository


class ReportManager:
    """Orchestrates report generation: validation, file dialog, dispatch, feedback."""

    def __init__(
        self,
        parent: QWidget,
        vehicle_repo: VehicleRepository,
        driver_repo: DriverRepository,
        log_repo: DailyLogRepository,
        repair_repo: RepairRepository,
    ):
        self.parent = parent
        self.vehicle_repo = vehicle_repo
        self.driver_repo = driver_repo
        self.log_repo = log_repo
        self.repair_repo = repair_repo

    def _get_save_path(self, suggested_name: str) :
        """Open a Save File dialog and return the chosen path, or None if cancelled."""
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent,
            "Save Report As",
            suggested_name,
            "PDF Files (*.pdf);;All Files (*)"
        )
        return file_path if file_path else None

    def generate_vehicle_log_report(
        self, vehicle_id: int, from_date: str, to_date: str, fuel_consumed: str
    ):
        """Generate a Vehicle Log Report, pre‑filling the filename with vehicle details."""
        try:
            fuel_val = float(fuel_consumed)
            if fuel_val <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(
                self.parent, "Invalid Input",
                "Fuel consumed must be a positive number."
            )
            return

        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        if vehicle:
            reg = vehicle["registration_number"]
            suggested = f"{reg}_{from_date}_{to_date}.pdf"
        else:
            suggested = "Vehicle_Log_Report.pdf"

        path = self._get_save_path(suggested)
        if not path:
            return

        try:
            generator = VehicleReport(
                self.vehicle_repo, self.driver_repo, self.log_repo
            )
            generator.generate(
                filepath=path,
                vehicle_id=vehicle_id,
                from_date=from_date,
                to_date=to_date,
                fuel_consumed=fuel_val
            )
            QMessageBox.information(
                self.parent, "Success", f"Report saved to:\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self.parent, "Report Error",
                f"Failed to generate the report:\n{str(e)}"
            )

    def generate_driver_report(self):
        """Generate a report listing all active drivers."""
        path = self._get_save_path("Driver_List_Report.pdf")
        if not path:
            return

        try:
            generator = DriverReport(self.driver_repo)
            generator.generate(path)
            QMessageBox.information(
                self.parent, "Success", f"Report saved to:\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self.parent, "Report Error",
                f"Failed to generate the report:\n{str(e)}"
            )

    def generate_vehicle_list_report(self):
        """Generate a report listing all active vehicles."""
        path = self._get_save_path("Vehicle_List_Report.pdf")
        if not path:
            return

        try:
            generator = VehicleListReport(self.vehicle_repo)
            generator.generate(path)
            QMessageBox.information(
                self.parent, "Success", f"Report saved to:\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self.parent, "Report Error",
                f"Failed to generate the report:\n{str(e)}"
            )

    def generate_repair_report(self, from_date: str, to_date: str):
        """Generate a repair report for a date range."""
        path = self._get_save_path("Repair_Report.pdf")
        if not path:
            return

        try:
            # FIX: RepairReport now requires only repair_repo.
            generator = RepairReport(self.repair_repo)
            generator.generate(path, from_date, to_date)
            QMessageBox.information(
                self.parent, "Success", f"Report saved to:\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self.parent, "Report Error",
                f"Failed to generate the report:\n{str(e)}"
            )
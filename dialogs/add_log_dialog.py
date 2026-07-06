from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDateEdit, QTimeEdit,
    QDialogButtonBox, QLabel, QMessageBox
)
from PySide6.QtCore import QDate, QTime
from database.database_manager import DatabaseManager
from database.repositories.driver_repository import DriverRepository
from database.repositories.vehicle_repository import VehicleRepository
from database.repositories.daily_log_repository import DailyLogRepository


class AddLogDialog(QDialog):
    """
    Dialog for adding a daily log entry.
    The driver name is auto‑filled based on the vehicle assignment.
    Mileage is calculated automatically from Meter Out / Meter In.
    """

    def __init__(
        self,
        db: DatabaseManager,
        vehicle_id,
        vehicle_reg: str,
        vehicle_repo: VehicleRepository,
        driver_repo: DriverRepository,
        log_repo: DailyLogRepository,
        parent=None,
    ):
        super().__init__(parent)
        self.db = db
        self.vehicle_id = vehicle_id
        self.vehicle_reg = vehicle_reg
        self.vehicle_repo = vehicle_repo
        self.driver_repo = driver_repo
        self.log_repo = log_repo

        self.setWindowTitle("Add Log Entry")
        self.setMinimumWidth(450)
        self._setup_ui()
        self._auto_fill_driver()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        form.addRow("Date:", self.date_edit)

        # Vehicle Registration Number (read‑only)
        self.reg_number_edit = QLineEdit(self.vehicle_reg)
        self.reg_number_edit.setReadOnly(True)
        form.addRow("Vehicle Registration No:", self.reg_number_edit)

        # Driver Name (read‑only, auto‑filled)
        self.driver_name_edit = QLineEdit()
        self.driver_name_edit.setReadOnly(True)
        form.addRow("Driver Name:", self.driver_name_edit)

        # From Time (QTimeEdit, 24h format)
        self.from_time_edit = QTimeEdit()
        self.from_time_edit.setDisplayFormat("HH:mm")
        self.from_time_edit.setTime(QTime(8, 0))
        form.addRow("From Time:", self.from_time_edit)

        # To Time (QTimeEdit, 24h format)
        self.to_time_edit = QTimeEdit()
        self.to_time_edit.setDisplayFormat("HH:mm")
        self.to_time_edit.setTime(QTime(17, 0))
        form.addRow("To Time:", self.to_time_edit)

        # Purpose / Route
        self.purpose_edit = QLineEdit()
        form.addRow("Purpose / Route:", self.purpose_edit)

        # Meter Out
        self.meter_out_edit = QLineEdit()
        form.addRow("Meter Out:", self.meter_out_edit)

        # Meter In
        self.meter_in_edit = QLineEdit()
        form.addRow("Meter In:", self.meter_in_edit)

        # Calculated Mileage (read‑only label)
        self.mileage_label = QLabel("0")
        self.mileage_label.setStyleSheet("font-weight: bold; padding: 4px;")
        form.addRow("Mileage:", self.mileage_label)

        # Fuel
        self.fuel_edit = QLineEdit()
        form.addRow("Fuel:", self.fuel_edit)

        # Mobile Oil
        self.mobile_oil_edit = QLineEdit()
        form.addRow("Mobile Oil:", self.mobile_oil_edit)

        # Remarks
        self.remarks_edit = QLineEdit()
        form.addRow("Remarks:", self.remarks_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._validate_and_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _auto_fill_driver(self):
        """Find the driver assigned to this vehicle and populate the field."""
        if self.vehicle_id is None:
            self.driver_name_edit.setText("No vehicle selected")
            return
        driver = self.driver_repo.get_driver_by_vehicle(self.vehicle_id)
        if driver:
            self.driver_name_edit.setText(driver["name"])
            self.driver_name_edit.setProperty("driver_id", driver["id"])
        else:
            self.driver_name_edit.setText("Not Assigned")
            self.driver_name_edit.setProperty("driver_id", None)

    def _connect_signals(self):
        self.meter_out_edit.textChanged.connect(self._calculate_mileage)
        self.meter_in_edit.textChanged.connect(self._calculate_mileage)

    def _calculate_mileage(self):
        try:
            out = float(self.meter_out_edit.text()) if self.meter_out_edit.text() else 0.0
            inc = float(self.meter_in_edit.text()) if self.meter_in_edit.text() else 0.0
            mileage = inc - out
            self.mileage_label.setText(str(mileage))
        except ValueError:
            self.mileage_label.setText("Invalid")

    def _validate_and_save(self):
        """Validate inputs, check mileage, and insert into database."""
        # Meter Out/In validation
        try:
            meter_out = float(self.meter_out_edit.text())
            meter_in = float(self.meter_in_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input",
                                "Meter Out and Meter In must be numbers.")
            return

        if meter_in < meter_out:
            QMessageBox.warning(self, "Invalid Mileage",
                                "Meter In cannot be less than Meter Out.")
            return

        mileage = meter_in - meter_out

        # Driver ID
        driver_id = self.driver_name_edit.property("driver_id")
        if driver_id is None:
            QMessageBox.warning(self, "No Driver",
                                "No driver is assigned to this vehicle. Cannot save log.")
            return

        # Fuel and Mobile Oil (optional, convert to float or None)
        fuel = None
        mobile_oil = None
        if self.fuel_edit.text().strip():
            try:
                fuel = float(self.fuel_edit.text())
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Fuel must be a number.")
                return
        if self.mobile_oil_edit.text().strip():
            try:
                mobile_oil = float(self.mobile_oil_edit.text())
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Mobile Oil must be a number.")
                return

        log_date = self.date_edit.date().toString("yyyy-MM-dd")
        from_time = self.from_time_edit.time().toString("HH:mm")
        to_time = self.to_time_edit.time().toString("HH:mm")
        purpose = self.purpose_edit.text().strip()
        remarks = self.remarks_edit.text().strip()

        try:
            self.log_repo.add_log(
                vehicle_id=self.vehicle_id,
                driver_id=driver_id,
                log_date=log_date,
                from_time=from_time,
                to_time=to_time,
                purpose_route=purpose,
                meter_out=meter_out,
                meter_in=meter_in,
                mileage=mileage,
                fuel=fuel,
                mobile_oil=mobile_oil,
                remarks=remarks,
            )
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Database Error", str(e))
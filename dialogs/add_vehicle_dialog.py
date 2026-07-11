from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QMessageBox
)
from core.exception_handler import AppExceptionHandler
from database.repositories.vehicle_repository import VehicleRepository


class AddVehicleDialog(QDialog):
    """Dialog for adding or editing a vehicle, now with a status dropdown."""

    def __init__(self, vehicle_repo: VehicleRepository, parent=None, vehicle_data: dict = None):
        super().__init__(parent)
        self.vehicle_repo = vehicle_repo
        self.vehicle_data = vehicle_data
        self.edit_mode = vehicle_data is not None
        self.setWindowTitle("Edit Vehicle" if self.edit_mode else "Add Vehicle")
        self.setMinimumWidth(400)
        self._setup_ui()
        if self.edit_mode:
            self._populate_fields()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.registration_edit = QLineEdit()
        form.addRow("Registration Number:", self.registration_edit)

        self.vehicle_type_combo = QComboBox()
        try:
            types = self.vehicle_repo.get_vehicle_types()
            for type_id, name in types:
                self.vehicle_type_combo.addItem(name, type_id)
        except Exception:
            pass
        form.addRow("Vehicle Type:", self.vehicle_type_combo)

        self.model_edit = QLineEdit()
        form.addRow("Model:", self.model_edit)

        self.engine_edit = QLineEdit()
        form.addRow("Engine Number:", self.engine_edit)

        self.chassis_edit = QLineEdit()
        form.addRow("Chassis Number:", self.chassis_edit)

        self.fuel_combo = QComboBox()
        self.fuel_combo.addItems([
            "Petrol", "Diesel", "CNG", "Electric",
            "Super-Petrol", "Hybrid", "Other"
        ])
        form.addRow("Fuel Type:", self.fuel_combo)

        # Status dropdown
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive"])
        form.addRow("Status:", self.status_combo)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _populate_fields(self):
        v = self.vehicle_data
        self.registration_edit.setText(str(v.get("registration_number", "")))
        type_id = v.get("vehicle_type_id")
        if type_id is not None:
            idx = self.vehicle_type_combo.findData(type_id)
            if idx >= 0:
                self.vehicle_type_combo.setCurrentIndex(idx)
        self.model_edit.setText(str(v.get("model", "")))
        self.engine_edit.setText(str(v.get("engine_number", "")))
        self.chassis_edit.setText(str(v.get("chassis_number", "")))
        fuel = v.get("fuel_type", "")
        if fuel is not None:
            idx = self.fuel_combo.findText(str(fuel))
            if idx >= 0:
                self.fuel_combo.setCurrentIndex(idx)
        # Set status
        status = v.get("status", "Active")
        idx = self.status_combo.findText(status)
        if idx >= 0:
            self.status_combo.setCurrentIndex(idx)

    def _save(self):
        reg = self.registration_edit.text().strip()
        if not reg:
            QMessageBox.warning(self, "Validation Error", "Registration number is required.")
            return
        if self.vehicle_type_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Validation Error", "Please select a vehicle type.")
            return
        vehicle_type_id = self.vehicle_type_combo.currentData()
        model = self.model_edit.text().strip()
        if not model:
            QMessageBox.warning(self, "Validation Error", "Model is required.")
            return
        engine = self.engine_edit.text().strip()
        chassis = self.chassis_edit.text().strip()
        fuel = self.fuel_combo.currentText()
        status = self.status_combo.currentText()

        try:
            if self.edit_mode:
                self.vehicle_repo.update(
                    vehicle_id=self.vehicle_data["id"],
                    registration_number=reg,
                    vehicle_type_id=vehicle_type_id,
                    model=model,
                    engine_number=engine,
                    chassis_number=chassis,
                    fuel_type=fuel,
                    status=status,
                )
            else:
                self.vehicle_repo.add(
                    registration_number=reg,
                    vehicle_type_id=vehicle_type_id,
                    model=model,
                    engine_number=engine,
                    chassis_number=chassis,
                    fuel_type=fuel,
                    status=status,
                )
            self.accept()
        except ValueError as e:
            AppExceptionHandler.show_error("Database Error", str(e), parent=self)
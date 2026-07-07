from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QMessageBox
)
from database.repositories.vehicle_repository import VehicleRepository


class AddVehicleDialog(QDialog):
    """Dialog for adding a new vehicle. Uses VehicleRepository for vehicle types and persistence."""

    def __init__(self, vehicle_repo: VehicleRepository, parent=None):
        super().__init__(parent)
        self.vehicle_repo = vehicle_repo
        self.setWindowTitle("Add Vehicle")
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Registration Number
        self.registration_edit = QLineEdit()
        form.addRow("Registration Number:", self.registration_edit)

        # Vehicle Type (dropdown from database)
        self.vehicle_type_combo = QComboBox()
        try:
            types = self.vehicle_repo.get_vehicle_types()
            for type_id, name in types:
                self.vehicle_type_combo.addItem(name, type_id)
        except Exception:
            pass  # if loading fails, dropdown is empty
        form.addRow("Vehicle Type:", self.vehicle_type_combo)

        # Model
        self.model_edit = QLineEdit()
        form.addRow("Model:", self.model_edit)

        # Engine Number
        self.engine_edit = QLineEdit()
        form.addRow("Engine Number:", self.engine_edit)

        # Chassis Number
        self.chassis_edit = QLineEdit()
        form.addRow("Chassis Number:", self.chassis_edit)

        # Fuel Type
        self.fuel_combo = QComboBox()
        self.fuel_combo.addItems(["Petrol","Super Petrol", "Diesel", "CNG", "Electric"])
        form.addRow("Fuel Type:", self.fuel_combo)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _save(self):
        reg_number = self.registration_edit.text().strip()
        if not reg_number:
            QMessageBox.warning(self, "Validation Error", "Registration number is required.")
            return

        if self.vehicle_type_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Validation Error", "Please select a vehicle type.")
            return

        vehicle_type_id = self.vehicle_type_combo.currentData()
        model = self.model_edit.text().strip()
        engine = self.engine_edit.text().strip()
        chassis = self.chassis_edit.text().strip()
        fuel = self.fuel_combo.currentText()

        if not model:
            QMessageBox.warning(self, "Validation Error", "Model is required.")
            return

        try:
            self.vehicle_repo.add(
                registration_number=reg_number,
                vehicle_type_id=vehicle_type_id,
                model=model,
                engine_number=engine,
                chassis_number=chassis,
                fuel_type=fuel,
            )
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Database Error", str(e))
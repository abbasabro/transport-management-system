from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QDialogButtonBox, QMessageBox
)
from database.repositories.vehicle_repository import VehicleRepository


class AddVehicleTypeDialog(QDialog):
    """Dialog for adding a new vehicle type. Uses VehicleRepository to persist."""

    def __init__(self, vehicle_repo: VehicleRepository, parent=None):
        super().__init__(parent)
        self.vehicle_repo = vehicle_repo
        self.setWindowTitle("Add Vehicle Type")
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Bus, Car, HiAce")
        form.addRow("Type Name:", self.name_edit)


        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Type name is required.")
            return
        try:
            self.vehicle_repo.add_vehicle_type(name)
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Database Error", str(e))
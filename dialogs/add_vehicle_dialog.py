from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QVBoxLayout
)
from PySide6.QtCore import Qt


class AddVehicleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Vehicle")
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.vehicle_number = QLineEdit()
        form.addRow("Vehicle Number:", self.vehicle_number)

        self.vehicle_type = QLineEdit()
        form.addRow("Vehicle Type:", self.vehicle_type)

        self.model = QLineEdit()
        form.addRow("Model:", self.model)

        self.engine_number = QLineEdit()
        form.addRow("Engine Number:", self.engine_number)

        self.chassis_number = QLineEdit()
        form.addRow("Chassis Number:", self.chassis_number)

        self.fuel_type = QComboBox()
        self.fuel_type.addItems(["Petrol", "Diesel", "CNG", "Electric"])
        form.addRow("Fuel Type:", self.fuel_type)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
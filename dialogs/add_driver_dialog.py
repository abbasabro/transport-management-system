from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit,
    QDialogButtonBox, QVBoxLayout
)


class AddDriverDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Driver")
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.driver_name = QLineEdit()
        form.addRow("Driver Name:", self.driver_name)

        self.designation = QLineEdit()
        form.addRow("Designation:", self.designation)

        self.vehicle_number = QLineEdit()
        form.addRow("Vehicle Number:", self.vehicle_number)

        self.contact_number = QLineEdit()
        form.addRow("Contact Number:", self.contact_number)

        self.cnic = QLineEdit()
        form.addRow("CNIC:", self.cnic)

        self.route = QLineEdit()
        form.addRow("Route:", self.route)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
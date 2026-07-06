from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QTextEdit,
    QDialogButtonBox, QVBoxLayout
)


class AddVehicleTypeDialog(QDialog):
    """Dialog for adding a new vehicle type."""

    def __init__(self, parent=None):
        super().__init__(parent)
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
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
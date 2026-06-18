from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDateEdit,
    QDialogButtonBox, QVBoxLayout
)
from PySide6.QtCore import QDate


class AddRepairDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Repair Record")
        self.setMinimumWidth(450)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.vehicle_number = QLineEdit()
        form.addRow("Vehicle Number:", self.vehicle_number)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        form.addRow("Date:", self.date_edit)

        self.mileage = QLineEdit()
        form.addRow("Mileage:", self.mileage)

        self.description = QLineEdit()
        form.addRow("Repair Description:", self.description)

        self.cost = QLineEdit()
        form.addRow("Cost:", self.cost)

        self.performed_by = QLineEdit()
        form.addRow("Performed By:", self.performed_by)

        self.remarks = QLineEdit()
        form.addRow("Remarks:", self.remarks)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
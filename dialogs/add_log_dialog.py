from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDateEdit,
    QDialogButtonBox, QVBoxLayout
)
from PySide6.QtCore import QDate


class AddLogDialog(QDialog):
    def __init__(self, parent=None, vehicle_reg=""):
        super().__init__(parent)
        self.setWindowTitle("Add Log Entry")
        self.setMinimumWidth(450)
        self.vehicle_reg = vehicle_reg
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        form.addRow("Date:", self.date_edit)

        self.reg_number = QLineEdit()
        self.reg_number.setText(self.vehicle_reg)
        form.addRow("Vehicle Registration Number:", self.reg_number)

        self.driver_name = QLineEdit()
        form.addRow("Driver Name:", self.driver_name)

        self.from_time = QLineEdit()
        form.addRow("From Time:", self.from_time)

        self.to_time = QLineEdit()
        form.addRow("To Time:", self.to_time)

        self.purpose = QLineEdit()
        form.addRow("Purpose / Route:", self.purpose)

        self.meter_out = QLineEdit()
        form.addRow("Meter Out:", self.meter_out)

        self.meter_in = QLineEdit()
        form.addRow("Meter In:", self.meter_in)

        self.mileage = QLineEdit()
        form.addRow("Mileage:", self.mileage)

        self.fuel = QLineEdit()
        form.addRow("Fuel:", self.fuel)

        self.mobile_oil = QLineEdit()
        form.addRow("Mobile Oil:", self.mobile_oil)

        self.remarks = QLineEdit()
        form.addRow("Remarks:", self.remarks)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
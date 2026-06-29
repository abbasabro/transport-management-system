from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialogButtonBox, QLabel
)
from PySide6.QtGui import QFont


class VehicleLogsDialog(QDialog):
    """Popup displaying log history for a given vehicle."""

    DUMMY_LOGS = {
        "LES-1234": [
            ["2025-03-01", "08:00", "14:00", "Route 5", "12500", "12600", "100", "20", "1", "Normal"],
            ["2025-03-02", "07:30", "13:30", "Route 5", "12600", "12710", "110", "22", "1", "Normal"],
        ],
        "LEA-5678": [
            ["2025-03-01", "09:00", "12:00", "Staff route", "5000", "5060", "60", "10", "0.5", "None"],
        ],
        "RIG-9901": [
            ["2025-03-03", "10:00", "16:00", "Cargo delivery", "2000", "2200", "200", "40", "2", "Heavy load"],
        ],
        "ABC-111": [
            ["2025-03-04", "11:00", "15:00", "Admin trip", "3000", "3080", "80", "12", "0.5", "None"],
        ],
    }

    def __init__(self, vehicle_reg: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Log History - {vehicle_reg}")
        self.resize(800, 400)
        self.vehicle_reg = vehicle_reg
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel(f"Log entries for {self.vehicle_reg}")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Date", "From Time", "To Time", "Purpose / Route",
            "Meter Out", "Meter In", "Mileage", "Fuel",
            "Mobile Oil", "Remarks"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Populate dummy data
        logs = self.DUMMY_LOGS.get(self.vehicle_reg, [])
        self.table.setRowCount(len(logs))
        for row_idx, row_data in enumerate(logs):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(value))

        layout.addWidget(self.table)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
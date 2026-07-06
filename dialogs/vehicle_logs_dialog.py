from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialogButtonBox, QLabel, QAbstractItemView
)
from PySide6.QtGui import QFont
from database.repositories.vehicle_repository import VehicleRepository
from database.repositories.daily_log_repository import DailyLogRepository


class VehicleLogsDialog(QDialog):
    """Dialog that shows all daily logs for a selected vehicle."""

    def __init__(
        self,
        vehicle_id: int,
        vehicle_repo: VehicleRepository,
        log_repo: DailyLogRepository,
        parent=None,
    ):
        super().__init__(parent)
        self.vehicle_id = vehicle_id
        self.vehicle_repo = vehicle_repo
        self.log_repo = log_repo

        self.setWindowTitle("Vehicle Log History")
        self.resize(900, 400)
        self._setup_ui()
        self._load_logs()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Title with vehicle registration
        vehicle = self.vehicle_repo.get_by_id(self.vehicle_id)
        reg = vehicle["registration_number"] if vehicle else "Unknown"
        title = QLabel(f"Log entries for {reg}")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(title)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Date", "From Time", "To Time", "Purpose / Route",
            "Meter Out", "Meter In", "Mileage", "Fuel",
            "Mobile Oil", "Remarks"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.table)

        # Close button
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_logs(self):
        """Retrieve logs from repository and populate the table."""
        try:
            logs = self.log_repo.get_logs_for_vehicle(self.vehicle_id)
            self._populate_table(logs)
        except Exception:
            self.table.setRowCount(0)

    def _populate_table(self, logs):
        self.table.setRowCount(len(logs))
        for row, log in enumerate(logs):
            self.table.setItem(row, 0, QTableWidgetItem(log.get("log_date", "")))
            self.table.setItem(row, 1, QTableWidgetItem(log.get("from_time", "")))
            self.table.setItem(row, 2, QTableWidgetItem(log.get("to_time", "")))
            self.table.setItem(row, 3, QTableWidgetItem(log.get("purpose_route", "")))
            self.table.setItem(row, 4, QTableWidgetItem(str(log.get("meter_out", ""))))
            self.table.setItem(row, 5, QTableWidgetItem(str(log.get("meter_in", ""))))
            self.table.setItem(row, 6, QTableWidgetItem(str(log.get("mileage", ""))))
            self.table.setItem(row, 7, QTableWidgetItem(str(log.get("fuel", "")) if log.get("fuel") is not None else ""))
            self.table.setItem(row, 8, QTableWidgetItem(str(log.get("mobile_oil", "")) if log.get("mobile_oil") is not None else ""))
            self.table.setItem(row, 9, QTableWidgetItem(log.get("remarks", "")))
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QFont

from database.repositories.vehicle_repository import VehicleRepository


class LogsPage(QWidget):
    """
    Logs Management page: lists active vehicles. Clicking a row opens the log entry dialog.
    """

    add_log_requested = Signal(int, str)  # vehicle_id, registration_number
    back_requested = Signal()

    def __init__(self, vehicle_repo: VehicleRepository):
        super().__init__()
        self.vehicle_repo = vehicle_repo
        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        # Top: back button + title
        top_layout = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.setIcon(QIcon.fromTheme("go-previous"))
        self.back_btn.setToolTip("Back to Dashboard")
        self.back_btn.setFixedSize(40, 40)
        self.back_btn.clicked.connect(self.back_requested.emit)
        top_layout.addWidget(self.back_btn)

        title = QLabel("Logs Management")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        top_layout.addWidget(title)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        # Middle: search bar only (no Add button)
        toolbar = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search vehicle registration...")
        self.search_edit.textChanged.connect(self._filter_table)
        toolbar.addWidget(self.search_edit)
        layout.addLayout(toolbar)

        # Bottom: table with one column
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Registration Number"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.cellClicked.connect(self._on_row_clicked)
        layout.addWidget(self.table)

    def load_data(self):
        """Load all ACTIVE vehicles and populate the table."""
        try:
            vehicles = self.vehicle_repo.get_active_vehicles()
            self._populate_table(vehicles)
        except Exception:
            self.table.setRowCount(0)

    def _populate_table(self, vehicles):
        self.table.setRowCount(len(vehicles))
        for row, v in enumerate(vehicles):
            item = QTableWidgetItem(v["registration_number"])
            item.setData(Qt.UserRole, v["id"])  # store vehicle id
            self.table.setItem(row, 0, item)

    def _filter_table(self, text):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and text.lower() in item.text().lower():
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def _on_row_clicked(self, row, col):
        """Emit signal with vehicle id and registration number."""
        vehicle_id = self.table.item(row, 0).data(Qt.UserRole)
        reg_num = self.table.item(row, 0).text()
        self.add_log_requested.emit(vehicle_id, reg_num)
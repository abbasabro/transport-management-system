from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QFont

from database.repositories.vehicle_repository import VehicleRepository
from database.repositories.driver_repository import DriverRepository


class AllLogsPage(QWidget):
    """
    Displays all vehicles with basic info and assigned driver.
    Clicking a vehicle opens its log history in a popup dialog.
    """

    vehicle_log_requested = Signal(int)  # vehicle_id
    back_requested = Signal()

    def __init__(self, vehicle_repo: VehicleRepository, driver_repo: DriverRepository):
        super().__init__()
        self.vehicle_repo = vehicle_repo
        self.driver_repo = driver_repo
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

        title = QLabel("All Logs")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        top_layout.addWidget(title)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        # Table with three columns
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            "Registration Number", "Vehicle Type", "Driver Name"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.cellClicked.connect(self._on_vehicle_clicked)
        layout.addWidget(self.table)

    def load_data(self):
        """Load all vehicles with their assigned driver names."""
        try:
            vehicles = self.vehicle_repo.get_all_active()
            self._populate_table(vehicles)
        except Exception:
            self.table.setRowCount(0)

    def _populate_table(self, vehicles):
        self.table.setRowCount(len(vehicles))
        for row, v in enumerate(vehicles):
            # Registration Number
            reg_item = QTableWidgetItem(v["registration_number"])
            reg_item.setData(Qt.UserRole, v["id"])  # store vehicle id
            self.table.setItem(row, 0, reg_item)

            # Vehicle Type
            type_item = QTableWidgetItem(v.get("vehicle_type", ""))
            self.table.setItem(row, 1, type_item)

            # Driver Name – fetch from driver repository
            driver = self.driver_repo.get_driver_by_vehicle(v["id"])
            driver_name = driver["name"] if driver else "Not Assigned"
            driver_item = QTableWidgetItem(driver_name)
            self.table.setItem(row, 2, driver_item)

    def _on_vehicle_clicked(self, row, col):
        """Emit signal with vehicle ID when a row is clicked."""
        vehicle_id = self.table.item(row, 0).data(Qt.UserRole)
        self.vehicle_log_requested.emit(vehicle_id)
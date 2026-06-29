from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QLabel, QPushButton
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon, QFont


class AllLogsPage(QWidget):
    """Displays all vehicles with basic info; clicking reg number opens logs dialog."""
    vehicle_log_requested = Signal(str)   # vehicle registration number
    back_requested = Signal()

    DUMMY_DATA = [
        ["LES-1234", "Bus", "Ahmed Khan"],
        ["LEA-5678", "Van", "Bilal Saeed"],
        ["RIG-9901", "Truck", "Kamran Ali"],
        ["ABC-111", "Car", "Sara Bibi"],
    ]

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._load_data()

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

        # Table (no search needed)
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Registration Number", "Vehicle Type", "Driver Name"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.cellClicked.connect(self._on_cell_clicked)
        layout.addWidget(self.table)

    def _load_data(self):
        self.table.setRowCount(len(self.DUMMY_DATA))
        for row_idx, row_data in enumerate(self.DUMMY_DATA):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(value))

    def _on_cell_clicked(self, row, col):
        # Emit signal regardless of column, but only use registration number
        reg = self.table.item(row, 0).text()
        self.vehicle_log_requested.emit(reg)
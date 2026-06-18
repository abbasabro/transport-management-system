from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QFont


class VehiclesPage(QWidget):
    """Searchable vehicles table with add button."""
    add_vehicle_clicked = Signal()

    DUMMY_DATA = [
        ["LES-1234", "Bus", "Hino RN8J", "ENG-001", "CHS-001", "Diesel"],
        ["LEA-5678", "Van", "Toyota Hiace", "ENG-002", "CHS-002", "Petrol"],
        ["RIG-9901", "Truck", "Isuzu FVZ", "ENG-003", "CHS-003", "Diesel"],
        ["ABC-111", "Car", "Honda Civic", "ENG-004", "CHS-004", "Petrol"],
    ]

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._load_data(self.DUMMY_DATA)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)

        title = QLabel("Vehicle Management")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        layout.addWidget(title)

        # Search and Add bar
        toolbar = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by registration number...")
        self.search_edit.textChanged.connect(self._filter_table)
        toolbar.addWidget(self.search_edit)

        self.add_btn = QPushButton("Add Vehicle")
        self.add_btn.setIcon(QIcon.fromTheme("list-add"))
        self.add_btn.clicked.connect(self.add_vehicle_clicked.emit)
        toolbar.addWidget(self.add_btn)
        layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Vehicle No / Reg No", "Vehicle Type", "Model", "Engine Number",
            "Chassis Number", "Fuel Type"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

    def _load_data(self, data):
        self.table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(value))

    def _filter_table(self, text):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)  # Registration number column
            if item and text.lower() in item.text().lower():
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)
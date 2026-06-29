from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QFont


class DriversPage(QWidget):
    """Searchable drivers table with add button and back navigation."""
    add_driver_clicked = Signal()
    back_requested = Signal()

    DUMMY_DATA = [
        ["Ahmed Khan", "Driver", "LES-1234", "0300-1234567", "42201-1234567-1", "Route 5"],
        ["Bilal Saeed", "Driver", "LEA-5678", "0321-9876543", "42201-9876543-2", "Route 12"],
        ["Kamran Ali", "Driver", "RIG-9901", "0333-1122334", "42201-1122334-3", "Campus Shuttle"],
        ["Sara Bibi", "Driver", "ABC-111", "0345-5566778", "42201-5566778-4", "Staff Route"],
    ]

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._load_data(self.DUMMY_DATA)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        # Top area: back button + title
        top_layout = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.setIcon(QIcon.fromTheme("go-previous"))
        self.back_btn.setToolTip("Back to Dashboard")
        self.back_btn.setFixedSize(40, 40)
        self.back_btn.clicked.connect(self.back_requested.emit)
        top_layout.addWidget(self.back_btn)

        title = QLabel("Driver Management")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        top_layout.addWidget(title)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        # Middle area: search and add button
        toolbar = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by name...")
        self.search_edit.textChanged.connect(self._filter_table)
        toolbar.addWidget(self.search_edit)

        self.add_btn = QPushButton("Add Driver")
        self.add_btn.setIcon(QIcon.fromTheme("list-add"))
        self.add_btn.clicked.connect(self.add_driver_clicked.emit)
        toolbar.addWidget(self.add_btn)
        layout.addLayout(toolbar)

        # Bottom area: table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Driver Name", "Designation", "Vehicle Number", "Contact Number",
            "CNIC", "Route"
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
            item = self.table.item(row, 0)
            if item and text.lower() in item.text().lower():
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)
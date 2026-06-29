from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QFont


class LogsPage(QWidget):
    """Logs management page: table of vehicle registration numbers."""
    add_log_requested = Signal(str)
    back_requested = Signal()

    DUMMY_VEHICLES = ["LES-1234", "LEA-5678", "RIG-9901", "ABC-111"]

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._load_data()

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

        title = QLabel("Logs Management")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        top_layout.addWidget(title)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        # Middle area: only search bar (no Add Log button)
        toolbar = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search vehicle...")
        self.search_edit.textChanged.connect(self._filter_table)
        toolbar.addWidget(self.search_edit)
        layout.addLayout(toolbar)

        # Bottom area: table
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Registration Number"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        # Single click opens dialog (was double click)
        self.table.cellClicked.connect(self._on_row_clicked)
        layout.addWidget(self.table)

    def _load_data(self):
        self.table.setRowCount(len(self.DUMMY_VEHICLES))
        for i, reg in enumerate(self.DUMMY_VEHICLES):
            self.table.setItem(i, 0, QTableWidgetItem(reg))

    def _filter_table(self, text):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and text.lower() in item.text().lower():
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def _on_row_clicked(self, row, col):
        reg = self.table.item(row, 0).text()
        self.add_log_requested.emit(reg)
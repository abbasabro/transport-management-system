from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QAbstractItemView,
    QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QFont

from database.repositories.repair_repository import RepairRepository
from database.repositories.vehicle_repository import VehicleRepository


class RepairsPage(QWidget):
    """Repair management page with table, search, add, edit, delete."""

    add_repair_clicked = Signal()
    edit_repair_requested = Signal(int)  # repair_id
    back_requested = Signal()

    def __init__(self, repair_repo: RepairRepository, vehicle_repo: VehicleRepository):
        super().__init__()
        self.repair_repo = repair_repo
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

        title = QLabel("Repair Management")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        top_layout.addWidget(title)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        # Middle: search bar + action buttons
        toolbar = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by description...")
        self.search_edit.textChanged.connect(self._on_search)
        toolbar.addWidget(self.search_edit)

        self.add_btn = QPushButton("Add Repair")
        self.add_btn.setIcon(QIcon.fromTheme("list-add"))
        self.add_btn.clicked.connect(self.add_repair_clicked.emit)
        toolbar.addWidget(self.add_btn)

        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.setIcon(QIcon.fromTheme("document-edit"))
        self.edit_btn.clicked.connect(self._edit_selected)
        toolbar.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setIcon(QIcon.fromTheme("edit-delete"))
        self.delete_btn.clicked.connect(self._delete_selected)
        toolbar.addWidget(self.delete_btn)

        layout.addLayout(toolbar)

        # Bottom: table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Vehicle Number", "Date", "Repair Description",
            "Cost", "Performed By", "Remarks"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.table)

    def load_data(self):
        """Fetch repairs from database and populate table."""
        try:
            repairs = self.repair_repo.get_all_active()
            self._populate_table(repairs)
        except Exception:
            self.table.setRowCount(0)

    def _populate_table(self, repairs):
        self.table.setRowCount(len(repairs))
        for row, r in enumerate(repairs):
            # Vehicle registration
            veh_item = QTableWidgetItem(r.get("vehicle_reg", ""))
            veh_item.setData(Qt.UserRole, r["id"])  # store repair id in first col
            self.table.setItem(row, 0, veh_item)

            self.table.setItem(row, 1, QTableWidgetItem(r.get("repair_date", "")))
            self.table.setItem(row, 2, QTableWidgetItem(r.get("description", "")))
            self.table.setItem(row, 3, QTableWidgetItem(str(r.get("cost", ""))))
            self.table.setItem(row, 4, QTableWidgetItem(r.get("performed_by", "")))
            self.table.setItem(row, 5, QTableWidgetItem(r.get("remarks", "")))

    def _on_search(self, text):
        """Filter table by description (case‑insensitive)."""
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 2)  # description column
            if item and text.lower() in item.text().lower():
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def _edit_selected(self):
        """Emit signal with repair ID if a row is selected."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select a repair to edit.")
            return
        row = selected[0].row()
        repair_id = self.table.item(row, 0).data(Qt.UserRole)
        self.edit_repair_requested.emit(repair_id)

    def _delete_selected(self):
        """Soft‑delete the selected repair after confirmation."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select a repair to delete.")
            return
        row = selected[0].row()
        repair_id = self.table.item(row, 0).data(Qt.UserRole)
        vehicle_reg = self.table.item(row, 0).text()
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete repair for vehicle '{vehicle_reg}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                self.repair_repo.soft_delete(repair_id)
                self.load_data()
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))
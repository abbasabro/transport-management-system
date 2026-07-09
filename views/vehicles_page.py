from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QAbstractItemView,
    QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QFont

from database.repositories.vehicle_repository import VehicleRepository
from security.permissions import PermissionManager


class VehiclesPage(QWidget):
    """Vehicles management page with role‑based button visibility."""

    add_vehicle_clicked = Signal()
    edit_vehicle_requested = Signal(int)               # vehicle_id
    download_vehicle_list_clicked = Signal()           # only if permitted
    back_requested = Signal()

    def __init__(self, vehicle_repo: VehicleRepository, perm_manager: PermissionManager):
        super().__init__()
        self.vehicle_repo = vehicle_repo
        self.perm = perm_manager
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

        title = QLabel("Vehicle Management")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        top_layout.addWidget(title)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        # Middle: search bar + action buttons (conditionally visible)
        toolbar = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by registration number...")
        self.search_edit.textChanged.connect(self._filter_table)
        toolbar.addWidget(self.search_edit)

        # Buttons appear only if permitted
        if self.perm.has_permission("vehicle.add"):
            self.add_btn = QPushButton("Add Vehicle")
            self.add_btn.setIcon(QIcon.fromTheme("list-add"))
            self.add_btn.clicked.connect(self.add_vehicle_clicked.emit)
            toolbar.addWidget(self.add_btn)

        if self.perm.has_permission("vehicle.update"):
            self.update_btn = QPushButton("Update Selected")
            self.update_btn.setIcon(QIcon.fromTheme("document-edit"))
            self.update_btn.clicked.connect(self._update_selected)
            toolbar.addWidget(self.update_btn)

        if self.perm.has_permission("vehicle.delete"):
            self.delete_btn = QPushButton("Delete Selected")
            self.delete_btn.setIcon(QIcon.fromTheme("edit-delete"))
            self.delete_btn.clicked.connect(self._delete_selected)
            toolbar.addWidget(self.delete_btn)

        if self.perm.has_permission("vehicle.download_report"):
            self.download_btn = QPushButton("Download Vehicle List")
            self.download_btn.setIcon(QIcon.fromTheme("document-print"))
            self.download_btn.clicked.connect(self.download_vehicle_list_clicked.emit)
            toolbar.addWidget(self.download_btn)

        layout.addLayout(toolbar)

        # Bottom: table (always visible, read‑only for everyone except column edits are off anyway)
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Registration No", "Vehicle Type", "Model",
            "Engine Number", "Chassis Number", "Fuel Type", 
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.table)

    def load_data(self):
        """Load vehicles from database and populate the table."""
        try:
            vehicles = self.vehicle_repo.get_all_active()
            self._populate_table(vehicles)
        except Exception as e:
            self.table.setRowCount(0)

    def _populate_table(self, vehicles):
        """Fill table with vehicle data."""
        self.table.setRowCount(len(vehicles))
        for row, v in enumerate(vehicles):
            reg_item = QTableWidgetItem(v["registration_number"])
            reg_item.setData(Qt.UserRole, v["id"])
            self.table.setItem(row, 0, reg_item)

            self.table.setItem(row, 1, QTableWidgetItem(v.get("vehicle_type", "")))
            self.table.setItem(row, 2, QTableWidgetItem(v.get("model", "")))
            self.table.setItem(row, 3, QTableWidgetItem(v.get("engine_number", "")))
            self.table.setItem(row, 4, QTableWidgetItem(v.get("chassis_number", "")))
            self.table.setItem(row, 5, QTableWidgetItem(v.get("fuel_type", "")))

    def _filter_table(self, text):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and text.lower() in item.text().lower():
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def _update_selected(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select a vehicle to update.")
            return
        row = selected[0].row()
        vehicle_id = self.table.item(row, 0).data(Qt.UserRole)
        self.edit_vehicle_requested.emit(vehicle_id)

    def _delete_selected(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select a vehicle to delete.")
            return
        row = selected[0].row()
        vehicle_id = self.table.item(row, 0).data(Qt.UserRole)
        reg_no = self.table.item(row, 0).text()
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete vehicle '{reg_no}'?\nThis action will soft-delete the record.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                self.vehicle_repo.soft_delete(vehicle_id)
                self.load_data()
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))
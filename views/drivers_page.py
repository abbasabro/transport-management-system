from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QAbstractItemView,
    QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QFont

from database.repositories.driver_repository import DriverRepository
from database.repositories.vehicle_repository import VehicleRepository
from security.permissions import PermissionManager


class DriversPage(QWidget):
    """Drivers management page with lifecycle status display."""

    add_driver_clicked = Signal()
    edit_driver_requested = Signal(int)          # driver_id
    download_driver_report_clicked = Signal()
    back_requested = Signal()

    def __init__(
        self,
        driver_repo: DriverRepository,
        vehicle_repo: VehicleRepository,
        perm_manager: PermissionManager,
    ):
        super().__init__()
        self.driver_repo = driver_repo
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

        title = QLabel("Driver Management")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        top_layout.addWidget(title)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        # Middle: search bar + action buttons (conditionally visible)
        toolbar = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by name...")
        self.search_edit.textChanged.connect(self._filter_table)
        toolbar.addWidget(self.search_edit)

        if self.perm.has_permission("driver.add"):
            self.add_btn = QPushButton("Add Driver")
            self.add_btn.setIcon(QIcon.fromTheme("list-add"))
            self.add_btn.clicked.connect(self.add_driver_clicked.emit)
            toolbar.addWidget(self.add_btn)

        if self.perm.has_permission("driver.update"):
            self.edit_btn = QPushButton("Edit Selected")
            self.edit_btn.setIcon(QIcon.fromTheme("document-edit"))
            self.edit_btn.clicked.connect(self._edit_selected)
            toolbar.addWidget(self.edit_btn)

        if self.perm.has_permission("driver.delete"):
            self.delete_btn = QPushButton("Delete Selected")
            self.delete_btn.setIcon(QIcon.fromTheme("edit-delete"))
            self.delete_btn.clicked.connect(self._delete_selected)
            toolbar.addWidget(self.delete_btn)

        if self.perm.has_permission("driver.download_report"):
            self.download_btn = QPushButton("Download Driver List")
            self.download_btn.setIcon(QIcon.fromTheme("document-print"))
            self.download_btn.clicked.connect(self.download_driver_report_clicked.emit)
            toolbar.addWidget(self.download_btn)

        layout.addLayout(toolbar)

        # Bottom: table with 7 columns (no hidden column)
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Driver Name", "Designation", "Vehicle Number",
            "Contact Number", "CNIC", "Route", "Status"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        if self.perm.has_permission("driver.update"):
            self.table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
            self.table.itemChanged.connect(self._on_item_changed)
        else:
            self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.table)

    def load_data(self):
        """Fetch all non‑deleted drivers (Active + Inactive)."""
        try:
            drivers = self.driver_repo.get_all_drivers_with_vehicle()
            self._populate_table(drivers)
        except Exception as e:
            self.table.setRowCount(0)

    def _populate_table(self, drivers):
        self.table.blockSignals(True)
        self.table.setRowCount(len(drivers))
        for row, d in enumerate(drivers):
            # Name column – store driver id in UserRole
            name_item = QTableWidgetItem(d["name"])
            name_item.setData(Qt.UserRole, d["id"])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, name_item)

            desig_item = QTableWidgetItem(d["designation"])
            desig_item.setFlags(desig_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, desig_item)

            # Vehicle column: show registration or "Spare Driver"
            if d.get("assigned_vehicle_id") is None:
                veh_text = "Spare Driver"
            else:
                veh_text = d.get("vehicle_reg", "Not Assigned")
            veh_item = QTableWidgetItem(veh_text)
            veh_item.setFlags(veh_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, veh_item)

            contact_item = QTableWidgetItem(d.get("contact_number", ""))
            contact_item.setFlags(contact_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 3, contact_item)

            cnic_item = QTableWidgetItem(d["cnic"])
            cnic_item.setFlags(cnic_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 4, cnic_item)

            # Route column (editable only if user has update permission)
            route_item = QTableWidgetItem(d.get("assigned_route", ""))
            if self.perm.has_permission("driver.update"):
                route_item.setFlags(route_item.flags() | Qt.ItemIsEditable)
            else:
                route_item.setFlags(route_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 5, route_item)

            # Status column
            status = d.get("status", "Active")
            status_item = QTableWidgetItem(status)
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            if status == "Inactive":
                status_item.setForeground(Qt.gray)
            self.table.setItem(row, 6, status_item)

        self.table.blockSignals(False)

    def _on_item_changed(self, item):
        """Called when the Route column is edited inline."""
        if item.column() != 5:
            return
        # Get driver id from the first column's UserRole
        driver_id = self.table.item(item.row(), 0).data(Qt.UserRole)
        if driver_id is None:
            QMessageBox.warning(self, "Error", "Could not retrieve driver ID.")
            return
        new_route = item.text().strip()
        try:
            driver = self.driver_repo.get_by_id(driver_id)
            if driver is None:
                QMessageBox.warning(self, "Error", "Driver not found.")
                self.load_data()
                return
            self.driver_repo.update(
                driver_id=driver_id,
                name=driver["name"],
                designation=driver["designation"],
                contact_number=driver["contact_number"] or "",
                cnic=driver["cnic"],
                assigned_vehicle_id=driver["assigned_vehicle_id"],
                assigned_route=new_route,
                status=driver["status"],  # keep current status
            )
        except ValueError as e:
            QMessageBox.warning(self, "Update Failed", str(e))
            self.load_data()

    def _edit_selected(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select a driver to edit.")
            return
        row = selected[0].row()
        driver_id = self.table.item(row, 0).data(Qt.UserRole)
        if driver_id is None:
            QMessageBox.warning(self, "Error", "Could not retrieve driver ID.")
            return
        self.edit_driver_requested.emit(driver_id)

    def _delete_selected(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select a driver to delete.")
            return
        row = selected[0].row()
        driver_id = self.table.item(row, 0).data(Qt.UserRole)
        if driver_id is None:
            QMessageBox.warning(self, "Error", "Could not retrieve driver ID.")
            return
        driver_name = self.table.item(row, 0).text()
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete driver '{driver_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                self.driver_repo.soft_delete(driver_id)
                self.load_data()
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))

    def _filter_table(self, text):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and text.lower() in item.text().lower():
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)
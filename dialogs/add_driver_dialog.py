from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QCheckBox, QDialogButtonBox, QMessageBox
)
from core.exception_handler import AppExceptionHandler
from database.repositories.driver_repository import DriverRepository
from database.repositories.vehicle_repository import VehicleRepository


class AddDriverDialog(QDialog):
    """
    Dialog for adding or editing a driver.
    Includes status, spare driver, and reactivation prompt for inactive drivers.
    """

    def __init__(
        self,
        driver_repo: DriverRepository,
        vehicle_repo: VehicleRepository,
        parent=None,
        driver_data= None,
    ):
        super().__init__(parent)
        self.driver_repo = driver_repo
        self.vehicle_repo = vehicle_repo
        self.driver_data = driver_data
        self.edit_mode = driver_data is not None
        self._reactivating = False   # set to True if reactivating an inactive driver

        self.setWindowTitle("Edit Driver" if self.edit_mode else "Add Driver")
        self.setMinimumWidth(450)
        self._setup_ui()
        if self.edit_mode:
            self._populate_fields()
        self._toggle_vehicle_combo()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Name
        self.name_edit = QLineEdit()
        form.addRow("Driver Name:", self.name_edit)

        # Designation
        self.designation_edit = QLineEdit()
        form.addRow("Designation:", self.designation_edit)

        # Contact Number
        self.contact_edit = QLineEdit()
        form.addRow("Contact Number:", self.contact_edit)

        # CNIC
        self.cnic_edit = QLineEdit()
        form.addRow("CNIC:", self.cnic_edit)

        # Spare Driver checkbox
        self.spare_checkbox = QCheckBox("Spare Driver")
        self.spare_checkbox.toggled.connect(self._toggle_vehicle_combo)
        form.addRow("", self.spare_checkbox)

        # Vehicle assignment – only Active vehicles
        self.vehicle_combo = QComboBox()
        self.vehicle_combo.addItem("None", None)
        try:
            # Use get_active_vehicles() to exclude Inactive vehicles
            vehicles = self.vehicle_repo.get_active_vehicles()
            for v in vehicles:
                self.vehicle_combo.addItem(v["registration_number"], v["id"])
        except Exception:
            pass
        form.addRow("Assigned Vehicle:", self.vehicle_combo)

        # Route
        self.route_edit = QLineEdit()
        form.addRow("Assigned Route:", self.route_edit)

        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive"])
        # Default is Active (new drivers) – but we set in _populate_fields for edit
        self.status_combo.setCurrentIndex(0)
        form.addRow("Status:", self.status_combo)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _toggle_vehicle_combo(self):
        is_spare = self.spare_checkbox.isChecked()
        self.vehicle_combo.setEnabled(not is_spare)
        if is_spare:
            self.vehicle_combo.setCurrentIndex(0)

    def _populate_fields(self):
        d = self.driver_data
        self.name_edit.setText(d.get("name", ""))
        self.designation_edit.setText(d.get("designation", ""))
        self.contact_edit.setText(d.get("contact_number", ""))
        self.cnic_edit.setText(d.get("cnic", ""))
        self.route_edit.setText(d.get("assigned_route", ""))

        is_spare = d.get("assigned_vehicle_id") is None
        self.spare_checkbox.setChecked(is_spare)

        assigned_id = d.get("assigned_vehicle_id")
        if assigned_id is not None:
            idx = self.vehicle_combo.findData(assigned_id)
            if idx >= 0:
                self.vehicle_combo.setCurrentIndex(idx)
        else:
            self.vehicle_combo.setCurrentIndex(0)

        # Status
        status = d.get("status", "Active")
        idx = self.status_combo.findText(status)
        if idx >= 0:
            self.status_combo.setCurrentIndex(idx)

    def _save(self):
        name = self.name_edit.text().strip()
        designation = self.designation_edit.text().strip()
        contact = self.contact_edit.text().strip()
        cnic = self.cnic_edit.text().strip()
        route = self.route_edit.text().strip()
        status = self.status_combo.currentText()

        if not name or not designation or not cnic:
            QMessageBox.warning(self, "Validation Error", "Name, Designation and CNIC are required.")
            return

        # Determine vehicle ID
        if self.spare_checkbox.isChecked():
            assigned_vehicle_id = None
        else:
            if self.vehicle_combo.currentData() is None:
                QMessageBox.warning(self, "Validation Error",
                                    "Please select a vehicle or mark as Spare Driver.")
                return
            assigned_vehicle_id = self.vehicle_combo.currentData()

        try:
            if self.edit_mode or self._reactivating:
                # Update existing driver (or reactivate)
                driver_id = self.driver_data["id"]
                self.driver_repo.update(
                    driver_id=driver_id,
                    name=name,
                    designation=designation,
                    contact_number=contact,
                    cnic=cnic,
                    assigned_vehicle_id=assigned_vehicle_id,
                    assigned_route=route,
                    status=status,
                )
            else:
                # New driver – may raise INACTIVE_DRIVER_EXISTS
                self.driver_repo.add(
                    name=name,
                    designation=designation,
                    contact_number=contact,
                    cnic=cnic,
                    assigned_vehicle_id=assigned_vehicle_id,
                    assigned_route=route,
                )
            self.accept()
        except ValueError as e:
            if str(e) == "INACTIVE_DRIVER_EXISTS":
                # Prompt for reactivation
                reply = QMessageBox.question(
                    self,
                    "Inactive Driver",
                    "This driver already exists but is currently inactive.\n"
                    "Would you like to reactivate this driver instead?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply == QMessageBox.Yes:
                    # Load the inactive driver data and switch to edit mode
                    existing = self.driver_repo.find_by_cnic(cnic)
                    if existing:
                        self.driver_data = self.driver_repo.get_by_id(existing["id"])
                        self.edit_mode = True
                        self._reactivating = True
                        self.setWindowTitle("Edit Driver (Reactivating)")
                        self._populate_fields()
                        self.status_combo.setCurrentIndex(0)  # set to Active
                        self._toggle_vehicle_combo()
                        # Do NOT call accept yet; user can modify and save again
                        return
                    else:
                        QMessageBox.warning(self, "Error", "Inactive driver not found.")
                # else: do nothing, user can correct CNIC
            else:
                AppExceptionHandler.show_error("Database Error", str(e), parent=self)
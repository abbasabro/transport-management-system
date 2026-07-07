from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QCheckBox, QDialogButtonBox, QMessageBox
)
from database.repositories.driver_repository import DriverRepository
from database.repositories.vehicle_repository import VehicleRepository


class AddDriverDialog(QDialog):
    """
    Dialog for adding or editing a driver.
    Includes a 'Spare Driver' checkbox that disables vehicle selection.
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

        self.setWindowTitle("Edit Driver" if self.edit_mode else "Add Driver")
        self.setMinimumWidth(450)
        self._setup_ui()
        if self.edit_mode:
            self._populate_fields()
        # Initial state: if spare is checked, disable vehicle combo
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

        # Vehicle assignment
        self.vehicle_combo = QComboBox()
        self.vehicle_combo.addItem("None", None)  # allow unassigned (for spare)
        try:
            vehicles = self.vehicle_repo.get_all_active()
            for v in vehicles:
                self.vehicle_combo.addItem(v["registration_number"], v["id"])
        except Exception:
            pass
        form.addRow("Assigned Vehicle:", self.vehicle_combo)

        # Route
        self.route_edit = QLineEdit()
        form.addRow("Assigned Route:", self.route_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _toggle_vehicle_combo(self):
        """Enable/disable vehicle combo based on spare checkbox."""
        is_spare = self.spare_checkbox.isChecked()
        self.vehicle_combo.setEnabled(not is_spare)
        if is_spare:
            self.vehicle_combo.setCurrentIndex(0)  # reset to None

    def _populate_fields(self):
        """Pre‑fill fields with existing driver data."""
        d = self.driver_data
        self.name_edit.setText(d.get("name", ""))
        self.designation_edit.setText(d.get("designation", ""))
        self.contact_edit.setText(d.get("contact_number", ""))
        self.cnic_edit.setText(d.get("cnic", ""))
        self.route_edit.setText(d.get("assigned_route", ""))

        # Spare checkbox: checked if no vehicle assigned
        is_spare = d.get("assigned_vehicle_id") is None
        self.spare_checkbox.setChecked(is_spare)

        # Vehicle combo
        assigned_id = d.get("assigned_vehicle_id")
        if assigned_id is not None:
            idx = self.vehicle_combo.findData(assigned_id)
            if idx >= 0:
                self.vehicle_combo.setCurrentIndex(idx)
        else:
            self.vehicle_combo.setCurrentIndex(0)  # None

    def _save(self):
        """Validate input and call repository."""
        name = self.name_edit.text().strip()
        designation = self.designation_edit.text().strip()
        contact = self.contact_edit.text().strip()
        cnic = self.cnic_edit.text().strip()
        route = self.route_edit.text().strip()

        # Basic validation
        if not name or not designation or not cnic:
            QMessageBox.warning(self, "Validation Error", "Name, Designation and CNIC are required.")
            return

        if self.spare_checkbox.isChecked():
            assigned_vehicle_id = None
        else:
            if self.vehicle_combo.currentData() is None:
                QMessageBox.warning(self, "Validation Error",
                                    "Please select a vehicle or mark as Spare Driver.")
                return
            assigned_vehicle_id = self.vehicle_combo.currentData()

        try:
            if self.edit_mode:
                self.driver_repo.update(
                    driver_id=self.driver_data["id"],
                    name=name,
                    designation=designation,
                    contact_number=contact,
                    cnic=cnic,
                    assigned_vehicle_id=assigned_vehicle_id,
                    assigned_route=route,
                )
            else:
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
            QMessageBox.warning(self, "Database Error", str(e))
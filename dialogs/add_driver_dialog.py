from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import Qt
from database.repositories.driver_repository import DriverRepository
from database.repositories.vehicle_repository import VehicleRepository


class AddDriverDialog(QDialog):
    """
    Dialog for adding or editing a driver.
    If driver_data is provided, the dialog operates in edit mode and pre‑fills the fields.
    """

    def __init__(
        self,
        driver_repo: DriverRepository,
        vehicle_repo: VehicleRepository,
        parent=None,
        driver_data: dict or None = None,
    ):
        super().__init__(parent)
        self.driver_repo = driver_repo
        self.vehicle_repo = vehicle_repo
        self.driver_data = driver_data  # None for add, dict for edit
        self.edit_mode = driver_data is not None

        self.setWindowTitle("Edit Driver" if self.edit_mode else "Add Driver")
        self.setMinimumWidth(450)
        self._setup_ui()
        if self.edit_mode:
            self._populate_fields()

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

        # Vehicle assignment
        self.vehicle_combo = QComboBox()
        self.vehicle_combo.addItem("None", None)  # allow unassigned
        # Load active vehicles
        try:
            vehicles = self.vehicle_repo.get_all_active()
            for v in vehicles:
                self.vehicle_combo.addItem(v["registration_number"], v["id"])
        except Exception:
            pass  # keep only "None" if loading fails
        form.addRow("Assigned Vehicle:", self.vehicle_combo)

        # Route
        self.route_edit = QLineEdit()
        form.addRow("Assigned Route:", self.route_edit)

        layout.addLayout(form)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _populate_fields(self):
        """Fill fields with existing driver data."""
        d = self.driver_data
        self.name_edit.setText(d.get("name", ""))
        self.designation_edit.setText(d.get("designation", ""))
        self.contact_edit.setText(d.get("contact_number", ""))
        self.cnic_edit.setText(d.get("cnic", ""))
        self.route_edit.setText(d.get("assigned_route", ""))

        # Set vehicle combo to the current assignment
        assigned_id = d.get("assigned_vehicle_id")
        if assigned_id is not None:
            idx = self.vehicle_combo.findData(assigned_id)
            if idx >= 0:
                self.vehicle_combo.setCurrentIndex(idx)

    def _save(self):
        """Validate input and call the repository to add or update."""
        name = self.name_edit.text().strip()
        designation = self.designation_edit.text().strip()
        contact = self.contact_edit.text().strip()
        cnic = self.cnic_edit.text().strip()
        assigned_vehicle_id = self.vehicle_combo.currentData()
        route = self.route_edit.text().strip()

        # Basic validation
        if not name:
            QMessageBox.warning(self, "Validation Error", "Driver name is required.")
            self.name_edit.setFocus()
            return
        if not designation:
            QMessageBox.warning(self, "Validation Error", "Designation is required.")
            self.designation_edit.setFocus()
            return
        if not cnic:
            QMessageBox.warning(self, "Validation Error", "CNIC is required.")
            self.cnic_edit.setFocus()
            return

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
            QMessageBox.warning(self, "Error", str(e))
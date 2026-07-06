from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDateEdit,
    QComboBox, QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import QDate
from database.repositories.repair_repository import RepairRepository
from database.repositories.vehicle_repository import VehicleRepository


class AddRepairDialog(QDialog):
    """
    Dialog for adding or editing a repair record.
    If repair_data is provided, the dialog operates in edit mode and pre‑fills fields.
    """

    def __init__(
        self,
        repair_repo: RepairRepository,
        vehicle_repo: VehicleRepository,
        parent=None,
        repair_data = None,
    ):
        super().__init__(parent)
        self.repair_repo = repair_repo
        self.vehicle_repo = vehicle_repo
        self.repair_data = repair_data
        self.edit_mode = repair_data is not None

        self.setWindowTitle("Edit Repair" if self.edit_mode else "Add Repair")
        self.setMinimumWidth(450)
        self._setup_ui()
        if self.edit_mode:
            self._populate_fields()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Vehicle dropdown
        self.vehicle_combo = QComboBox()
        try:
            vehicles = self.vehicle_repo.get_all_active()
            for v in vehicles:
                self.vehicle_combo.addItem(v["registration_number"], v["id"])
        except Exception:
            pass  # no vehicles
        form.addRow("Vehicle:", self.vehicle_combo)

        # Repair Date
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        form.addRow("Repair Date:", self.date_edit)

        # Mileage (optional)
        self.mileage_edit = QLineEdit()
        form.addRow("Mileage:", self.mileage_edit)

        # Description
        self.desc_edit = QLineEdit()
        form.addRow("Repair Description:", self.desc_edit)

        # Cost
        self.cost_edit = QLineEdit()
        form.addRow("Cost:", self.cost_edit)

        # Performed By
        self.performed_by_edit = QLineEdit()
        form.addRow("Performed By:", self.performed_by_edit)

        # Remarks
        self.remarks_edit = QLineEdit()
        form.addRow("Remarks:", self.remarks_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _populate_fields(self):
        """Pre‑fill fields with existing repair data."""
        d = self.repair_data
        # Set vehicle combo
        vehicle_id = d.get("vehicle_id")
        if vehicle_id is not None:
            idx = self.vehicle_combo.findData(vehicle_id)
            if idx >= 0:
                self.vehicle_combo.setCurrentIndex(idx)

        # Set date
        if d.get("repair_date"):
            self.date_edit.setDate(QDate.fromString(d["repair_date"], "yyyy-MM-dd"))

        self.mileage_edit.setText(str(d.get("mileage", "")) if d.get("mileage") is not None else "")
        self.desc_edit.setText(d.get("description", ""))
        self.cost_edit.setText(str(d.get("cost", "")))
        self.performed_by_edit.setText(d.get("performed_by", ""))
        self.remarks_edit.setText(d.get("remarks", ""))

    def _save(self):
        """Validate input and call repository to add or update."""
        if self.vehicle_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Validation Error", "Please select a vehicle.")
            return

        vehicle_id = self.vehicle_combo.currentData()
        repair_date = self.date_edit.date().toString("yyyy-MM-dd")
        description = self.desc_edit.text().strip()
        cost_text = self.cost_edit.text().strip()
        performed_by = self.performed_by_edit.text().strip()
        remarks = self.remarks_edit.text().strip()
        mileage_text = self.mileage_edit.text().strip()

        if not description:
            QMessageBox.warning(self, "Validation Error", "Repair description is required.")
            self.desc_edit.setFocus()
            return
        if not cost_text:
            QMessageBox.warning(self, "Validation Error", "Cost is required.")
            self.cost_edit.setFocus()
            return

        try:
            cost = float(cost_text)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Cost must be a number.")
            return

        mileage = None
        if mileage_text:
            try:
                mileage = float(mileage_text)
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Mileage must be a number.")
                return

        try:
            if self.edit_mode:
                self.repair_repo.update(
                    repair_id=self.repair_data["id"],
                    vehicle_id=vehicle_id,
                    repair_date=repair_date,
                    mileage=mileage,
                    description=description,
                    cost=cost,
                    performed_by=performed_by,
                    remarks=remarks,
                )
            else:
                self.repair_repo.add(
                    vehicle_id=vehicle_id,
                    repair_date=repair_date,
                    mileage=mileage,
                    description=description,
                    cost=cost,
                    performed_by=performed_by,
                    remarks=remarks,
                )
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Database Error", str(e))
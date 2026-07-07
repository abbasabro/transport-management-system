from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDateEdit, QLineEdit, QComboBox, QGroupBox, QMessageBox
)
from PySide6.QtCore import QDate, Signal
from PySide6.QtGui import QFont, QIcon
from reports.report_manager import ReportManager
from database.repositories.vehicle_repository import VehicleRepository


class ReportsPage(QWidget):
    """Reports generation page with input controls for various report types."""

    back_requested = Signal()

    def __init__(self, vehicle_repo: VehicleRepository, report_manager: ReportManager):
        super().__init__()
        self.vehicle_repo = vehicle_repo
        self.report_manager = report_manager
        self._setup_ui()
        self._populate_vehicles()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)

        # Top area: back button + title
        top_layout = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.setIcon(QIcon.fromTheme("go-previous"))
        self.back_btn.setToolTip("Back to Dashboard")
        self.back_btn.setFixedSize(40, 40)
        self.back_btn.clicked.connect(self.back_requested.emit)
        top_layout.addWidget(self.back_btn)

        title = QLabel("Report Generation")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        top_layout.addWidget(title)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)

        # --- Vehicle Log Report Section ---
        vehicle_group = QGroupBox("Vehicle Log Report")
        vg_layout = QVBoxLayout(vehicle_group)

        # Vehicle selection
        veh_row = QHBoxLayout()
        veh_row.addWidget(QLabel("Select Vehicle:"))
        self.vehicle_combo = QComboBox()
        self.vehicle_combo.setMinimumWidth(200)
        veh_row.addWidget(self.vehicle_combo)
        veh_row.addStretch()
        vg_layout.addLayout(veh_row)

        # Date range
        date_row = QHBoxLayout()
        date_row.addWidget(QLabel("From Date:"))
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        date_row.addWidget(self.from_date)

        date_row.addWidget(QLabel("To Date:"))
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        date_row.addWidget(self.to_date)
        date_row.addStretch()
        vg_layout.addLayout(date_row)

        # Fuel input
        fuel_row = QHBoxLayout()
        fuel_row.addWidget(QLabel("Total Fuel Consumed (Litre):"))
        self.fuel_input = QLineEdit()
        self.fuel_input.setPlaceholderText("e.g., 50.5")
        self.fuel_input.setMaximumWidth(100)
        fuel_row.addWidget(self.fuel_input)
        fuel_row.addStretch()
        vg_layout.addLayout(fuel_row)

        # Generate button
        self.gen_vehicle_btn = QPushButton("Generate Vehicle Report")
        self.gen_vehicle_btn.setIcon(QIcon.fromTheme("document-print"))
        self.gen_vehicle_btn.clicked.connect(self._generate_vehicle_report)
        vg_layout.addWidget(self.gen_vehicle_btn)

        main_layout.addWidget(vehicle_group)

        # --- Driver List Report Section ---
        driver_group = QGroupBox("Driver List Report")
        dg_layout = QVBoxLayout(driver_group)
        self.gen_driver_btn = QPushButton("Generate Driver List Report")
        self.gen_driver_btn.setIcon(QIcon.fromTheme("document-print"))
        self.gen_driver_btn.clicked.connect(self._generate_driver_report)
        dg_layout.addWidget(self.gen_driver_btn)
        main_layout.addWidget(driver_group)

        # --- Vehicle List Report Section ---
        vlist_group = QGroupBox("Vehicle List Report")
        vlg_layout = QVBoxLayout(vlist_group)
        self.gen_vehicle_list_btn = QPushButton("Generate Vehicle List Report")
        self.gen_vehicle_list_btn.setIcon(QIcon.fromTheme("document-print"))
        self.gen_vehicle_list_btn.clicked.connect(self._generate_vehicle_list_report)
        vlg_layout.addWidget(self.gen_vehicle_list_btn)
        main_layout.addWidget(vlist_group)

        # --- Repair Report Section ---
        repair_group = QGroupBox("Repair Report")
        rg_layout = QVBoxLayout(repair_group)

        # Date range
        rdate_row = QHBoxLayout()
        rdate_row.addWidget(QLabel("From Date:"))
        self.repair_from_date = QDateEdit()
        self.repair_from_date.setCalendarPopup(True)
        self.repair_from_date.setDate(QDate.currentDate().addMonths(-1))
        rdate_row.addWidget(self.repair_from_date)

        rdate_row.addWidget(QLabel("To Date:"))
        self.repair_to_date = QDateEdit()
        self.repair_to_date.setCalendarPopup(True)
        self.repair_to_date.setDate(QDate.currentDate())
        rdate_row.addWidget(self.repair_to_date)
        rdate_row.addStretch()
        rg_layout.addLayout(rdate_row)

        self.gen_repair_btn = QPushButton("Generate Repair Report")
        self.gen_repair_btn.setIcon(QIcon.fromTheme("document-print"))
        self.gen_repair_btn.clicked.connect(self._generate_repair_report)
        rg_layout.addWidget(self.gen_repair_btn)
        main_layout.addWidget(repair_group)

        main_layout.addStretch()

    def _populate_vehicles(self):
        """Fill the vehicle combo box with active vehicles."""
        self.vehicle_combo.clear()
        try:
            vehicles = self.vehicle_repo.get_all_active()
            for v in vehicles:
                self.vehicle_combo.addItem(
                    f"{v['registration_number']} - {v.get('vehicle_type', '')}",
                    v["id"]
                )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load vehicles:\n{str(e)}")

    def _generate_vehicle_report(self):
        if self.vehicle_combo.currentIndex() < 0:
            QMessageBox.warning(self, "No Vehicle", "Please select a vehicle.")
            return
        vehicle_id = self.vehicle_combo.currentData()
        from_date = self.from_date.date().toString("yyyy-MM-dd")
        to_date = self.to_date.date().toString("yyyy-MM-dd")
        fuel = self.fuel_input.text().strip()
        if not fuel:
            QMessageBox.warning(self, "Missing Input", "Please enter the total fuel consumed.")
            return
        self.report_manager.generate_vehicle_log_report(vehicle_id, from_date, to_date, fuel)

    def _generate_driver_report(self):
        self.report_manager.generate_driver_report()

    def _generate_vehicle_list_report(self):
        self.report_manager.generate_vehicle_list_report()

    def _generate_repair_report(self):
        from_date = self.repair_from_date.date().toString("yyyy-MM-dd")
        to_date = self.repair_to_date.date().toString("yyyy-MM-dd")
        self.report_manager.generate_repair_report(from_date, to_date)
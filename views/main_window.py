from PySide6.QtWidgets import (
    QMainWindow, QMenuBar, QStatusBar, QStackedWidget, QMessageBox
)
from PySide6.QtGui import QAction, QIcon

from views.dashboard_page import DashboardPage
from views.vehicles_page import VehiclesPage
from views.drivers_page import DriversPage
from views.logs_page import LogsPage
from views.repairs_page import RepairsPage
from views.reports_page import ReportsPage
from views.all_logs_page import AllLogsPage
from views.settings_page import SettingsPage  # new

from dialogs.add_vehicle_dialog import AddVehicleDialog
from dialogs.add_driver_dialog import AddDriverDialog
from dialogs.add_log_dialog import AddLogDialog
from dialogs.add_repair_dialog import AddRepairDialog
from dialogs.vehicle_logs_dialog import VehicleLogsDialog
from dialogs.add_vehicle_type_dialog import AddVehicleTypeDialog

from reports.report_manager import ReportManager

from database.repositories.vehicle_repository import VehicleRepository
from database.repositories.driver_repository import DriverRepository
from database.repositories.daily_log_repository import DailyLogRepository
from database.repositories.repair_repository import RepairRepository
from database.repositories.user_repository import UserRepository  # for settings


class MainWindow(QMainWindow):
    """Main application window with all modules integrated, including Settings."""

    def __init__(self, db, user):
        super().__init__()
        self.db = db
        self.user = user

        # ------------------ Repositories ------------------
        self.vehicle_repo = VehicleRepository(db)
        self.driver_repo = DriverRepository(db)
        self.log_repo = DailyLogRepository(db)
        self.repair_repo = RepairRepository(db)
        self.user_repo = UserRepository(db)          # for settings page

        # ------------------ Report Manager ------------------
        self.report_manager = ReportManager(
            self, self.vehicle_repo, self.driver_repo,
            self.log_repo, self.repair_repo
        )

        # ------------------ Window setup ------------------
        self.setWindowTitle("BBSTUD Transport Management System")
        self.resize(1100, 700)

        # Central stacked widget
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # ------------------ Pages ------------------
        self.dashboard_page = DashboardPage(self.vehicle_repo, self.driver_repo)
        self.vehicles_page = VehiclesPage(self.vehicle_repo)
        self.drivers_page = DriversPage(self.driver_repo, self.vehicle_repo)
        self.logs_page = LogsPage(self.vehicle_repo)
        self.all_logs_page = AllLogsPage(self.vehicle_repo, self.driver_repo)
        self.repairs_page = RepairsPage(self.repair_repo, self.vehicle_repo)
        self.reports_page = ReportsPage(self.vehicle_repo, self.report_manager)
        self.settings_page = SettingsPage(self.user_repo, self.user)  # new

        # Add pages to stack (order follows navigation)
        self.stack.addWidget(self.dashboard_page)   # 0
        self.stack.addWidget(self.vehicles_page)    # 1
        self.stack.addWidget(self.drivers_page)     # 2
        self.stack.addWidget(self.logs_page)        # 3
        self.stack.addWidget(self.all_logs_page)    # 4
        self.stack.addWidget(self.repairs_page)     # 5
        self.stack.addWidget(self.reports_page)     # 6
        self.stack.addWidget(self.settings_page)    # 7 (new)

        self._setup_menu_bar()
        self._setup_status_bar()
        self._connect_dashboard_signals()
        self._connect_page_signals()

        self.stack.setCurrentWidget(self.dashboard_page)

    # ------------------------------------------------------------------
    # Menu bar
    # ------------------------------------------------------------------
    def _setup_menu_bar(self):
        menubar = self.menuBar()

        # Master Data
        master_menu = menubar.addMenu("Master Data")

        add_driver_action = QAction(QIcon.fromTheme("contact-new"), "Add Driver", self)
        add_driver_action.triggered.connect(self.open_add_driver_dialog)
        master_menu.addAction(add_driver_action)

        add_vehicle_action = QAction(QIcon.fromTheme("document-new"), "Add Vehicle", self)
        add_vehicle_action.triggered.connect(self.open_add_vehicle_dialog)
        master_menu.addAction(add_vehicle_action)

        add_vehicle_type_action = QAction(QIcon.fromTheme("list-add"), "Add Vehicle Type", self)
        add_vehicle_type_action.triggered.connect(self.open_add_vehicle_type_dialog)
        master_menu.addAction(add_vehicle_type_action)

        master_menu.addSeparator()

        drivers_list_action = QAction(QIcon.fromTheme("view-list-details"), "Drivers List", self)
        drivers_list_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.drivers_page))
        master_menu.addAction(drivers_list_action)

        vehicles_list_action = QAction(QIcon.fromTheme("view-list-tree"), "Vehicles List", self)
        vehicles_list_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.vehicles_page))
        master_menu.addAction(vehicles_list_action)

        # Operations
        ops_menu = menubar.addMenu("Operations")
        logs_action = QAction(QIcon.fromTheme("x-office-spreadsheet"), "Logs Management", self)
        logs_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.logs_page))
        ops_menu.addAction(logs_action)

        all_logs_action = QAction(QIcon.fromTheme("view-list-tree"), "All Logs", self)
        all_logs_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.all_logs_page))
        ops_menu.addAction(all_logs_action)

        repair_action = QAction(QIcon.fromTheme("applications-engineering"), "Repair Management", self)
        repair_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.repairs_page))
        ops_menu.addAction(repair_action)

        # Reports
        reports_menu = menubar.addMenu("Reports")
        reports_action = QAction(QIcon.fromTheme("document-print-preview"), "Report Generation", self)
        reports_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.reports_page))
        reports_menu.addAction(reports_action)

        # Settings (new)
        settings_menu = menubar.addMenu("Settings")
        settings_action = QAction(QIcon.fromTheme("configure"), "Settings", self)
        settings_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.settings_page))
        settings_menu.addAction(settings_action)

        # Exit
        exit_menu = menubar.addMenu("Exit")
        exit_action = QAction(QIcon.fromTheme("application-exit"), "Exit Application", self)
        exit_action.triggered.connect(self.close)
        exit_menu.addAction(exit_action)

    # ------------------------------------------------------------------
    # Status bar
    # ------------------------------------------------------------------
    def _setup_status_bar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage(
            f"Logged in as: {self.user['full_name']} ({self.user['role']})   |   Ready"
        )

    # ------------------------------------------------------------------
    # Dashboard signal connections (added settings)
    # ------------------------------------------------------------------
    def _connect_dashboard_signals(self):
        dash = self.dashboard_page
        dash.add_vehicle_clicked.connect(self.open_add_vehicle_dialog)
        dash.add_driver_clicked.connect(self.open_add_driver_dialog)
        dash.logs_clicked.connect(lambda: self.stack.setCurrentWidget(self.logs_page))
        dash.vehicles_list_clicked.connect(lambda: self.stack.setCurrentWidget(self.vehicles_page))
        dash.drivers_list_clicked.connect(lambda: self.stack.setCurrentWidget(self.drivers_page))
        dash.repairs_clicked.connect(lambda: self.stack.setCurrentWidget(self.repairs_page))
        dash.reports_clicked.connect(lambda: self.stack.setCurrentWidget(self.reports_page))
        dash.all_logs_clicked.connect(lambda: self.stack.setCurrentWidget(self.all_logs_page))
        dash.settings_clicked.connect(lambda: self.stack.setCurrentWidget(self.settings_page))  # new

    # ------------------------------------------------------------------
    # Page signal connections (back buttons, downloads, edits)
    # ------------------------------------------------------------------
    def _connect_page_signals(self):
        # Back buttons
        self.vehicles_page.back_requested.connect(self._go_to_dashboard)
        self.drivers_page.back_requested.connect(self._go_to_dashboard)
        self.logs_page.back_requested.connect(self._go_to_dashboard)
        self.all_logs_page.back_requested.connect(self._go_to_dashboard)
        self.repairs_page.back_requested.connect(self._go_to_dashboard)
        self.reports_page.back_requested.connect(self._go_to_dashboard)
        self.settings_page.back_requested.connect(self._go_to_dashboard)  # new

        # Add dialogs from pages
        self.vehicles_page.add_vehicle_clicked.connect(self.open_add_vehicle_dialog)
        self.drivers_page.add_driver_clicked.connect(self.open_add_driver_dialog)
        self.drivers_page.edit_driver_requested.connect(self.open_edit_driver_dialog)
        self.logs_page.add_log_requested.connect(self.open_add_log_dialog)
        self.repairs_page.add_repair_clicked.connect(self.open_add_repair_dialog)
        self.repairs_page.edit_repair_requested.connect(self.open_edit_repair_dialog)
        self.all_logs_page.vehicle_log_requested.connect(self.open_vehicle_logs_dialog)

        # New connections for vehicle editing and downloads
        self.vehicles_page.edit_vehicle_requested.connect(self.open_edit_vehicle_dialog)
        self.vehicles_page.download_vehicle_list_clicked.connect(
            self.report_manager.generate_vehicle_list_report
        )
        self.drivers_page.download_driver_report_clicked.connect(
            self.report_manager.generate_driver_report
        )

    def _go_to_dashboard(self):
        self.dashboard_page.refresh()
        self.stack.setCurrentWidget(self.dashboard_page)

    # ------------------------------------------------------------------
    # Dialog openers (existing + new edit vehicle)
    # ------------------------------------------------------------------
    def open_add_vehicle_dialog(self):
        dialog = AddVehicleDialog(self.vehicle_repo, self)
        if dialog.exec():
            self.vehicles_page.load_data()
            self.dashboard_page.refresh()
            QMessageBox.information(self, "Success", "Vehicle added successfully.")

    def open_add_driver_dialog(self):
        dialog = AddDriverDialog(self.driver_repo, self.vehicle_repo, self)
        if dialog.exec():
            self.drivers_page.load_data()
            self.dashboard_page.refresh()
            QMessageBox.information(self, "Success", "Driver added successfully.")

    def open_edit_driver_dialog(self, driver_id):
        driver = self.driver_repo.get_by_id(driver_id)
        if not driver:
            QMessageBox.warning(self, "Error", "Driver not found.")
            return
        dialog = AddDriverDialog(
            self.driver_repo, self.vehicle_repo, self, driver_data=driver
        )
        if dialog.exec():
            self.drivers_page.load_data()
            self.dashboard_page.refresh()
            QMessageBox.information(self, "Success", "Driver updated successfully.")

    def open_add_log_dialog(self, vehicle_id, vehicle_reg=""):
        dialog = AddLogDialog(
            self.db,
            vehicle_id,
            vehicle_reg,
            self.vehicle_repo,
            self.driver_repo,
            self.log_repo,
            self,
        )
        if dialog.exec():
            QMessageBox.information(self, "Success", "Log entry saved.")

    def open_add_repair_dialog(self):
        dialog = AddRepairDialog(self.repair_repo, self.vehicle_repo, self)
        if dialog.exec():
            self.repairs_page.load_data()
            QMessageBox.information(self, "Success", "Repair record saved.")

    def open_edit_repair_dialog(self, repair_id):
        repair = self.repair_repo.get_by_id(repair_id)
        if not repair:
            QMessageBox.warning(self, "Error", "Repair not found.")
            return
        dialog = AddRepairDialog(
            self.repair_repo, self.vehicle_repo, self, repair_data=repair
        )
        if dialog.exec():
            self.repairs_page.load_data()
            QMessageBox.information(self, "Success", "Repair updated successfully.")

    def open_vehicle_logs_dialog(self, vehicle_id):
        dialog = VehicleLogsDialog(vehicle_id, self.vehicle_repo, self.log_repo, self)
        dialog.exec()

    def open_add_vehicle_type_dialog(self):
        dialog = AddVehicleTypeDialog(self.vehicle_repo, self)
        if dialog.exec():
            QMessageBox.information(self, "Success", "Vehicle type added.")

    def open_edit_vehicle_dialog(self, vehicle_id):
        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle:
            QMessageBox.warning(self, "Error", "Vehicle not found.")
            return
        dialog = AddVehicleDialog(self.vehicle_repo, self, vehicle_data=vehicle)
        if dialog.exec():
            self.vehicles_page.load_data()
            self.dashboard_page.refresh()
            QMessageBox.information(self, "Success", "Vehicle updated successfully.")
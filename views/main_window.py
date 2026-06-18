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
from dialogs.add_vehicle_dialog import AddVehicleDialog
from dialogs.add_driver_dialog import AddDriverDialog
from dialogs.add_log_dialog import AddLogDialog
from dialogs.add_repair_dialog import AddRepairDialog


class MainWindow(QMainWindow):
    """Main application window with menu, stacked pages and status bar."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BBSTUD Transport Management System")
        self.resize(1100, 700)

        # Central stacked widget
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Create pages
        self.dashboard_page = DashboardPage()
        self.vehicles_page = VehiclesPage()
        self.drivers_page = DriversPage()
        self.logs_page = LogsPage()
        self.repairs_page = RepairsPage()
        self.reports_page = ReportsPage()

        self.stack.addWidget(self.dashboard_page)   # index 0
        self.stack.addWidget(self.vehicles_page)    # index 1
        self.stack.addWidget(self.drivers_page)     # index 2
        self.stack.addWidget(self.logs_page)        # index 3
        self.stack.addWidget(self.repairs_page)     # index 4
        self.stack.addWidget(self.reports_page)     # index 5

        self._setup_menu_bar()
        self._setup_status_bar()
        self._connect_dashboard_signals()
        self._connect_page_signals()

    def _setup_menu_bar(self):
        menubar = self.menuBar()

        # Master Data menu
        master_menu = menubar.addMenu("Master Data")

        add_driver_action = QAction(QIcon.fromTheme("contact-new"), "Add Driver", self)
        add_driver_action.triggered.connect(self.open_add_driver_dialog)
        master_menu.addAction(add_driver_action)

        add_vehicle_action = QAction(QIcon.fromTheme("document-new"), "Add Vehicle", self)
        add_vehicle_action.triggered.connect(self.open_add_vehicle_dialog)
        master_menu.addAction(add_vehicle_action)

        master_menu.addSeparator()

        drivers_list_action = QAction(QIcon.fromTheme("view-list-details"), "Drivers List", self)
        drivers_list_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.drivers_page))
        master_menu.addAction(drivers_list_action)

        vehicles_list_action = QAction(QIcon.fromTheme("view-list-tree"), "Vehicles List", self)
        vehicles_list_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.vehicles_page))
        master_menu.addAction(vehicles_list_action)

        # Operations menu
        ops_menu = menubar.addMenu("Operations")
        logs_action = QAction(QIcon.fromTheme("x-office-spreadsheet"), "Logs Management", self)
        logs_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.logs_page))
        ops_menu.addAction(logs_action)

        repair_action = QAction(QIcon.fromTheme("applications-engineering"), "Repair Management", self)
        repair_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.repairs_page))
        ops_menu.addAction(repair_action)

        # Reports menu
        reports_menu = menubar.addMenu("Reports")
        reports_action = QAction(QIcon.fromTheme("document-print-preview"), "Report Generation", self)
        reports_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.reports_page))
        reports_menu.addAction(reports_action)

        # Exit
        exit_menu = menubar.addMenu("Exit")
        exit_action = QAction(QIcon.fromTheme("application-exit"), "Exit Application", self)
        exit_action.triggered.connect(self.close)
        exit_menu.addAction(exit_action)

    def _setup_status_bar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")

    # ---------- Dashboard signal connections ----------
    def _connect_dashboard_signals(self):
        dash = self.dashboard_page
        dash.add_vehicle_clicked.connect(self.open_add_vehicle_dialog)
        dash.add_driver_clicked.connect(self.open_add_driver_dialog)
        dash.logs_clicked.connect(lambda: self.stack.setCurrentWidget(self.logs_page))
        dash.vehicles_list_clicked.connect(lambda: self.stack.setCurrentWidget(self.vehicles_page))
        dash.drivers_list_clicked.connect(lambda: self.stack.setCurrentWidget(self.drivers_page))
        dash.repairs_clicked.connect(lambda: self.stack.setCurrentWidget(self.repairs_page))
        dash.reports_clicked.connect(lambda: self.stack.setCurrentWidget(self.reports_page))

    # ---------- Page signal connections ----------
    def _connect_page_signals(self):
        self.vehicles_page.add_vehicle_clicked.connect(self.open_add_vehicle_dialog)
        self.drivers_page.add_driver_clicked.connect(self.open_add_driver_dialog)
        self.logs_page.add_log_requested.connect(self.open_add_log_dialog)
        self.repairs_page.add_repair_clicked.connect(self.open_add_repair_dialog)

    # ---------- Dialog openers ----------
    def open_add_vehicle_dialog(self):
        dialog = AddVehicleDialog(self)
        if dialog.exec():
            QMessageBox.information(self, "Success", "Vehicle added successfully (placeholder).")

    def open_add_driver_dialog(self):
        dialog = AddDriverDialog(self)
        if dialog.exec():
            QMessageBox.information(self, "Success", "Driver added successfully (placeholder).")

    def open_add_log_dialog(self, vehicle_reg=""):
        dialog = AddLogDialog(self, vehicle_reg)
        if dialog.exec():
            QMessageBox.information(self, "Success", "Log entry saved (placeholder).")

    def open_add_repair_dialog(self):
        dialog = AddRepairDialog(self)
        if dialog.exec():
            QMessageBox.information(self, "Success", "Repair record saved (placeholder).")
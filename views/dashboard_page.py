from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
from PySide6 import QtCore


class DashboardPage(QWidget):
    """Dashboard with summary cards and quick action buttons."""
    add_vehicle_clicked = Signal()
    add_driver_clicked = Signal()
    logs_clicked = Signal()
    vehicles_list_clicked = Signal()
    drivers_list_clicked = Signal()
    repairs_clicked = Signal()
    reports_clicked = Signal()

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)

        # Title
        title = QLabel("Dashboard")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        main_layout.addWidget(title)

        # Cards row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(30)

        # Total Vehicles card
        self.vehicle_card = self._create_stat_card("Total Vehicles", "15")
        cards_layout.addWidget(self.vehicle_card)

        # Total Drivers card
        self.driver_card = self._create_stat_card("Total Drivers", "10")
        cards_layout.addWidget(self.driver_card)

        main_layout.addLayout(cards_layout)
        main_layout.addSpacing(30)

        # Action buttons section
        main_layout.addWidget(QLabel("Quick Actions", font=QFont("Segoe UI", 14, QFont.Bold)))
        buttons_grid_layout = QHBoxLayout()
        buttons_grid_layout.setSpacing(20)

        btn_add_vehicle = self._create_action_button("Add Vehicle", "list-add")
        btn_add_vehicle.clicked.connect(self.add_vehicle_clicked.emit)
        buttons_grid_layout.addWidget(btn_add_vehicle)

        btn_add_driver = self._create_action_button("Add Driver", "list-add")
        btn_add_driver.clicked.connect(self.add_driver_clicked.emit)
        buttons_grid_layout.addWidget(btn_add_driver)

        btn_logs = self._create_action_button("Logs Management", "x-office-spreadsheet")
        btn_logs.clicked.connect(self.logs_clicked.emit)
        buttons_grid_layout.addWidget(btn_logs)

        main_layout.addLayout(buttons_grid_layout)

        buttons_grid2 = QHBoxLayout()
        buttons_grid2.setSpacing(20)

        btn_vehicles_list = self._create_action_button("Vehicles List", "view-list-tree")
        btn_vehicles_list.clicked.connect(self.vehicles_list_clicked.emit)
        buttons_grid2.addWidget(btn_vehicles_list)

        btn_drivers_list = self._create_action_button("Drivers List", "view-list-details")
        btn_drivers_list.clicked.connect(self.drivers_list_clicked.emit)
        buttons_grid2.addWidget(btn_drivers_list)

        btn_repairs = self._create_action_button("Repair Management", "applications-engineering")
        btn_repairs.clicked.connect(self.repairs_clicked.emit)
        buttons_grid2.addWidget(btn_repairs)

        btn_reports = self._create_action_button("Report Generation", "document-print-preview")
        btn_reports.clicked.connect(self.reports_clicked.emit)
        buttons_grid2.addWidget(btn_reports)

        main_layout.addLayout(buttons_grid2)
        main_layout.addStretch()

    def _create_stat_card(self, title: str, value: str) -> QFrame:
        """Creates a styled statistic card."""
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #d0d7de;
                border-radius: 12px;
                padding: 20px;
                min-width: 220px;
            }
        """)
        card_layout = QVBoxLayout(card)
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11))
        title_label.setStyleSheet("color: #555; border: none;")
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        value_label.setStyleSheet("color: #1a56db; border: none;")
        card_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        card_layout.addWidget(value_label, alignment=Qt.AlignCenter)
        return card

    def _create_action_button(self, text: str, icon_name: str) -> QPushButton:
        """Creates a large action button with icon."""
        btn = QPushButton(text)
        btn.setIcon(QIcon.fromTheme(icon_name))
        btn.setIconSize(QtCore.QSize(32, 32))
        btn.setMinimumHeight(60)
        btn.setFont(QFont("Segoe UI", 12))
        btn.setStyleSheet("""
            QPushButton {
                background-color: #1a56db;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1748b0;
            }
            QPushButton:pressed {
                background-color: #123a8c;
            }
        """)
        return btn
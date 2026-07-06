from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon

from database.repositories.vehicle_repository import VehicleRepository
from database.repositories.driver_repository import DriverRepository


class DashboardPage(QWidget):
    """Dashboard with live summary cards and quick action buttons."""

    # Signals
    add_vehicle_clicked = Signal()
    add_driver_clicked = Signal()
    logs_clicked = Signal()
    vehicles_list_clicked = Signal()
    drivers_list_clicked = Signal()
    repairs_clicked = Signal()
    reports_clicked = Signal()
    all_logs_clicked = Signal()

    PRIMARY_BLUE = "#1A56DB"
    GOLD = "#F2A900"

    def __init__(self, vehicle_repo: VehicleRepository, driver_repo: DriverRepository):
        super().__init__()
        self.vehicle_repo = vehicle_repo
        self.driver_repo = driver_repo
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)

        # Title
        title = QLabel("Dashboard")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet(
            f"color: {self.PRIMARY_BLUE}; border-bottom: 3px solid {self.GOLD}; padding-bottom: 5px;"
        )
        main_layout.addWidget(title)

        # Cards row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(30)

        self.vehicle_card, self.vehicle_value_label = self._create_stat_card("Total Vehicles")
        cards_layout.addWidget(self.vehicle_card)

        self.driver_card, self.driver_value_label = self._create_stat_card("Total Drivers")
        cards_layout.addWidget(self.driver_card)

        main_layout.addLayout(cards_layout)
        main_layout.addSpacing(30)

        # Quick Actions
        main_layout.addWidget(QLabel("Quick Actions", font=QFont("Segoe UI", 14, QFont.Bold)))

        buttons_grid1 = QHBoxLayout()
        buttons_grid1.setSpacing(20)

        btn_add_vehicle = self._create_action_button("Add Vehicle", "list-add")
        btn_add_vehicle.clicked.connect(self.add_vehicle_clicked.emit)
        buttons_grid1.addWidget(btn_add_vehicle)

        btn_add_driver = self._create_action_button("Add Driver", "list-add")
        btn_add_driver.clicked.connect(self.add_driver_clicked.emit)
        buttons_grid1.addWidget(btn_add_driver)

        btn_logs = self._create_action_button("Logs Management", "x-office-spreadsheet")
        btn_logs.clicked.connect(self.logs_clicked.emit)
        buttons_grid1.addWidget(btn_logs)

        main_layout.addLayout(buttons_grid1)

        buttons_grid2 = QHBoxLayout()
        buttons_grid2.setSpacing(20)

        btn_vehicles_list = self._create_action_button("Vehicles List", "view-list-tree")
        btn_vehicles_list.clicked.connect(self.vehicles_list_clicked.emit)
        buttons_grid2.addWidget(btn_vehicles_list)

        btn_drivers_list = self._create_action_button("Drivers List", "view-list-details")
        btn_drivers_list.clicked.connect(self.drivers_list_clicked.emit)
        buttons_grid2.addWidget(btn_drivers_list)

        btn_all_logs = self._create_action_button("All Logs", "view-list-tree")
        btn_all_logs.clicked.connect(self.all_logs_clicked.emit)
        buttons_grid2.addWidget(btn_all_logs)

        main_layout.addLayout(buttons_grid2)

        buttons_grid3 = QHBoxLayout()
        buttons_grid3.setSpacing(20)

        btn_repairs = self._create_action_button("Repair Management", "applications-engineering")
        btn_repairs.clicked.connect(self.repairs_clicked.emit)
        buttons_grid3.addWidget(btn_repairs)

        btn_reports = self._create_action_button("Report Generation", "document-print-preview")
        btn_reports.clicked.connect(self.reports_clicked.emit)
        buttons_grid3.addWidget(btn_reports)

        main_layout.addLayout(buttons_grid3)
        main_layout.addStretch()

    def refresh(self):
        """Fetch counts from database and update card labels."""
        try:
            vehicles = self.vehicle_repo.get_all_active()
            drivers = self.driver_repo.get_all_active_with_vehicle()
            self.vehicle_value_label.setText(str(len(vehicles)))
            self.driver_value_label.setText(str(len(drivers)))
        except Exception as e:
            self.vehicle_value_label.setText("?")
            self.driver_value_label.setText("?")

    def _create_stat_card(self, title: str) -> tuple[QFrame, QLabel]:
        """
        Creates a styled statistic card.
        Returns the card frame and the value label so we can update it later.
        """
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid #d0d7de;
                border-left: 6px solid {self.GOLD};
                border-radius: 10px;
                padding: 20px;
                min-width: 220px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11))
        title_label.setStyleSheet("color: #555; border: none;")
        value_label = QLabel("0")
        value_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        value_label.setStyleSheet(f"color: {self.PRIMARY_BLUE}; border: none;")
        card_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        card_layout.addWidget(value_label, alignment=Qt.AlignCenter)
        return card, value_label

    def _create_action_button(self, text: str, icon_name: str) -> QPushButton:
        """Creates a large action button with university colours."""
        btn = QPushButton(text)
        btn.setIcon(QIcon.fromTheme(icon_name))
        btn.setIconSize(QSize(32, 32))
        btn.setMinimumHeight(60)
        btn.setFont(QFont("Segoe UI", 12))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.PRIMARY_BLUE};
                color: white;
                border: 2px solid transparent;
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1748b0;
                border-color: {self.GOLD};
            }}
            QPushButton:pressed {{
                background-color: #123a8c;
            }}
        """)
        return btn